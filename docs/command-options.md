```bash
python manage.py makemigrations --help

usage: manage.py makemigrations [-h] [--fix] [-b DEFAULT_BRANCH] [-s] [-r REMOTE] [-f] [--dry-run] [--merge] [--empty] [--noinput] [-n NAME] [--no-header] [--check]
                                [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]
                                [app_label ...]

Creates new migration(s) for apps and fix conflicts.

positional arguments:
  app_label             Specify the app label(s) to create migrations for.

optional arguments:
  -h, --help            show this help message and exit
  --fix                 Fix migrations conflicts.
  -b DEFAULT_BRANCH, --default-branch DEFAULT_BRANCH
                        The name of the default branch.
  -s, --skip-default-branch-update
                        Skip pulling the latest changes from the default branch.
  -r REMOTE, --remote REMOTE
                        Git remote.
  -f, --force-update    Force update the default branch.
  --dry-run             Just show what migrations would be made; don't actually write them.
  --merge               Enable fixing of migration conflicts.
  --empty               Create an empty migration.
  --noinput, --no-input
                        Tells Django to NOT prompt the user for input of any kind.
  -n NAME, --name NAME  Use this name for migration file(s).
  --no-header           Do not add header comments to new migration file(s).
  --check               Exit with a non-zero status if model changes are missing migrations.
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will
                        be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```