import tempfile
import os, os.path
import shutil


def clean():
    tempdir = tempfile.gettempdir()
    count = 0
    bytecount = 0
    for directory in os.listdir(tempdir):
        if os.path.isdir(os.path.join(tempdir, directory, 'webapp')):
            count += 1
            bytecount += os.path.getsize(os.path.join(tempdir, directory))
            shutil.rmtree(os.path.join(tempdir, directory))

    return (count, bytecount)

if __name__ == "__main__":
    count, bytecount = clean()
    print "Deleted %d apps, cleared %d bytes" % (count, bytecount)
