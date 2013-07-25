import os
import sys
import subprocess
import shlex

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'settings.prod')
    APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    commands = []
    commands.append('python manage.py syncdb --noinput')
    commands.append('python manage.py migrate')

    if not os.path.isdir(os.path.join(APP_DIR, 'webapp', 'migrations')):
        sys.stdout.write("\nWeb app has not yet been migrated - converting to south.")
        commands.append('python manage.py convert_to_south webapp')
        # The following line is a workaround for this issue: http://south.aeracode.org/ticket/1179
        commands.append('python manage.py migrate webapp 0001 --fake')

    else:
        commands.append('python manage.py schemamigration webapp --auto')
        commands.append('python manage.py migrate webapp')

    for c in commands:
        print("Running `{}`".format(c))
        try:
            log_msg = subprocess.check_output(shlex.split(c), cwd=APP_DIR)
        except subprocess.CalledProcessError, e:
            sys.stderr.write("\n%r returned with exit code of %s" % (e.cmd, e.returncode))
            sys.stderr.write("\nCommand output: %s" % e.output)
        else:
            sys.stdout.write("\n%r succeeded. Output:\n%s" % (c, log_msg))

