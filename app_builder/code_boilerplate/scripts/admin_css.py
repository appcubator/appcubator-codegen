import os
import sys
import subprocess
import shlex

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'settings.prod')
    APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    commands = []
    commands.append('python manage.py collectstatic --noinput')

    for c in commands:
        print("Running `{}`".format(c))
        try:
            log_msg = subprocess.check_output(shlex.split(c), cwd=APP_DIR)
        except subprocess.CalledProcessError, e:
            sys.stderr.write("\n%r returned with exit code of %s" % (e.cmd, e.returncode))
            sys.stderr.write("\nCommand output: %s" % e.output)
        else:
            sys.stdout.write("\n%r succeeded. Output:\n%s" % (c, log_msg))

