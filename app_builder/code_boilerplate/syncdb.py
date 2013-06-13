#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"]

    commands = []
    commands.append('python manage.py syncdb --noinput')

    if not os.path.isdir(os.path.join(app.app_dir, 'webapp', 'migrations')):
        sys.stdout.write("Web app has not yet been migrated - converting to south.")
        commands.append('python manage.py convert_to_south webapp')
    else:
        commands.append('python manage.py schemamigration webapp --auto')

    commands.append('python manage.py migrate')

    for c in commands:
        print("Running `{}`".format(c))
        try:
            log_msg = subprocess.check_output(shlex.split(c), env=child_env, cwd=app.app_dir)
        except subprocess.CalledProcessError, e:
            sys.stderr.write(repr(e.cmd) + " returned with exit code of " + str(e.returncode))
            sys.stderr.write("Command output: " + e.output)
        else:
            sys.stdout.write("%r succeeded. Output:\n%s" % (c, log_msg))

