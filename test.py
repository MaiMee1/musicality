import sys
import inspect
import requests

import pyglet
from pyglet.media import *

pyglet.lib.load_library('avbin')
pyglet.have_avbin = True


def url_to_filename(url):
    return url.split('/')[-1]


def download_file(url, filename=None):
    filename = filename or url_to_filename(url)

    with open(filename, "wb") as f:
        print("Downloading %s" % filename)
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()


url = "https://freemusicarchive.org/file/music/ccCommunity/DASK/Abiogenesis/DASK_-_08_-_Protocell.mp3"
filename = "mcve.mp3"
download_file(url, filename)

music = pyglet.media.load(filename)
music.play()
pyglet.app.run()