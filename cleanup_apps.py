import tempfile
import os, os.path
import shutil


def clean():
    tempdir = tempfile.gettempdir()
    for directory in os.listdir(tempdir):
        if os.path.isdir(os.path.join(tempdir, directory, 'webapp')):
            shutil.rmtree(os.path.join(tempdir, directory))

if __name__ == "__main__":
    clean()
