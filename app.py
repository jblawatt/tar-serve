import os
import os.path
import bottle
import tarfile
from bottle import request

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ARC_ROOT = os.path.join(APP_ROOT, 'archives')


app = bottle.default_app()


@app.route('/', method=['GET'])
def list_archives():

    tars = []

    for filename in os.listdir(ARC_ROOT):
        if filename.endswith('tar'):
            tf = tarfile.open(os.path.join(ARC_ROOT, filename))
            name, __ = os.path.splitext(filename)
            tars.append({
                'path': name,
                'name': filename,
                'fileinfo': tf.tarinfo.size
            })

    return bottle.template('archives.html', tars=tars)


@app.route('/', method=['POST'])
def upload_archive():
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.tar'):
        return bottle.HTTPError(400, 'File extension not allowed.')

    save_path = os.path.join(APP_ROOT, 'archives')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = os.path.join(save_path, upload.filename)

    upload.save(save_path, overwrite=True)

    return bottle.redirect('/')


def lookup_file(t, filenames):
    for filename in filenames:
        try:
            return t.getmember(filename)
        except KeyError:
            pass
    else:
        raise KeyError(filenames)


@app.route('/<archive_name>')
@app.route('/<archive_name>/<filename:re:.*>')
def serve(archive_name, filename=None):
    file_path = os.path.join(ARC_ROOT, archive_name + '.tar')
    t = tarfile.open(file_path)

    try:
        tar_info = lookup_file(t, [filename] if filename else [
                               'index.html', 'index.htm'])
    except KeyError:
        members = []
        for m in t.getmembers():
            members.append({
                'name': m.name,
                'type': m.type,
            })
        return bottle.template("memberlist.html", members=members)
    if not tar_info.isfile():
        return bottle.HTTPError(400, 'not a file')

    headers = {
        'Content-Length': tar_info.size,
        'Content-Type': tar_info.type
    }

    body = t.extractfile(filename).read()

    return bottle.HTTPResponse(
        body=body,
        headers=headers)


if __name__ == '__main__':
    app.run(reloader=True, debug=False, host='0.0.0.0',
            port=int(os.getenv('PORT', 8080)))
