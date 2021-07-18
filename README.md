![logo](https://user-images.githubusercontent.com/17484350/124649379-6821ad00-de66-11eb-9b0e-890913c65311.png)

[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Coverage) [![codecov](https://codecov.io/gh/tj-django/django-migration-fixer/branch/main/graph/badge.svg?token=peNs0PpfP6)](https://codecov.io/gh/tj-django/django-migration-fixer)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/tj-django/django-migration-fixer.svg?logo=lgtm\&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-migration-fixer/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/tj-django/django-migration-fixer.svg?logo=lgtm\&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-migration-fixer/context:python) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Grade)

[![Test](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml) [![Upload Python Package](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml) [![Run linters](https://github.com/tj-django/django-migration-fixer/actions/workflows/lint.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/lint.yml) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![PyPI](https://img.shields.io/pypi/v/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![Downloads](https://pepy.tech/badge/django-migration-fixer)](https://pepy.tech/project/django-migration-fixer) [![Public workflows that use this action.](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi-tj-actions1.vercel.app%2Fapi%2Fgithub-actions%2Fused-by%3Faction%3Dtj-django%2Fdjango-migration-fixer%26badge%3Dtrue)](https://github.com/search?o=desc\&q=tj-django+django-migration-fixer+language%3AYAML\&s=\&type=Code)

# django-migration-fixer

Resolve django makemigrations `multiple leaf nodes in the migration graph` by ensuring that migration files and dependencies are always ordered regardless of remote changes.

## Features

*   100% test coverage.
*   Maintain a consistent migration history when conflicts occur as a result of changes made using different versions of the default branch.
*   Resolve migration conflicts on PR branches
*   Resolve migration conflicts on the default branch **(NOT RECOMMENDED)**
*   Supports default migration modules i.e (`0001_....py`)
*   Re-number all migrations using the last migration on the default branch i.e `main|master|develop` depending on your setup.

## Installation

```bash
$ pip install django-migration-fixer
```

#### Add `migration_fixer` to your INSTALLED_APPS

```python

INSTALLED_APPS = [
    ...,
    "migration_fixer",
    ...,
]

```

## Usage

```bash
$ python manage.py makemigrations --fix
```

By default this uses `main` as the default branch

### Specifying a different default branch

Run:

```bash
$ python manage.py makemigrations -b master --fix
```

### Github Actions

> NOTE: :warning:
>
> *   To get this action to work you'll need to install [django-migration-fixer](#installation) and update your `INSTALLED_APPS` setting.
>
>     See: https://github.com/tj-django/django-clone for an example setup.

```yaml
name: Fix django migrations

on:
  pull_request:
    branches:
      - main

jobs:
  fix-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.6.x'

      - name: Upgrade pip
        run: |
          pip install -U pip

      - name: Install project dependencies
        run: |
          make install

      - name: Run django-migration-fixer
        uses: tj-django/django-migration-fixer@v1.1.1
        with:
          managepy-path: /path/to/manage.py

      - name: Verify Changed files
        uses: tj-actions/verify-changed-files@v7.1
        id: verify-changed-files
        with:
          files: |
             /path/to/migrations

      - name: Commit migration changes
        if: steps.verify-changed-files.outputs.files_changed == 'true'
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add /path/to/migrations
          git commit -m "Update migrations"

      - name: Push migration changes
        if: steps.verify-changed-files.outputs.files_changed == 'true'
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: ${{ github.ref }}
```

## Test Platforms

*   [`ubuntu-*`](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idruns-on)
*   [`macos-*`](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idruns-on)
*   [`windows-*`](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idruns-on)

## Example

#### Local branch changes

![Screen Shot 2021-07-06 at 2 21 29 PM](https://user-images.githubusercontent.com/17484350/124649021-f6496380-de65-11eb-9b95-0f204abe142a.png)

#### After merging the default branch

![Screen Shot 2021-07-06 at 2 21 46 PM](https://user-images.githubusercontent.com/17484350/124648930-d7e36800-de65-11eb-99a3-bf806ecfd32b.png)

#### After running django-migration-fixer

![Screen Shot 2021-07-06 at 2 22 31 PM](https://user-images.githubusercontent.com/17484350/124649105-0feaab00-de66-11eb-80f3-7987d67b361d.png)

### More Examples

**Branch:** `main`

```bash

├── app
│   ├── migrations
│   ├── 0001_initial.py
│   ├── 0002_auto_20210521_2328.py  

```

**Branch:** `feature/test-a`

```bash

├── app
│   ├── migrations
│   ├── 0001_initial.py
│   ├── 0002_auto_20210521_2328.py
│   ├── 0003_auto_20210522_1128.py 

```

**Branch:**`feature/test-b`

```bash

├── app
│   ├── migrations
│   ├── 0001_initial.py
│   ├── 0002_auto_20210521_2328.py
│   ├── 0003_auto_20210522_1228.py 

```

Both `feature/test-a` and `feature/test-b` share the last migration on `main` (`0002_auto_20210521_2328.py`)

Once `feature/test-a` is merged into `main` you run into the problem of resolving migrations on `feature/test-b` which was dependent on `0002_auto_20210521_2328.py`

**Branch:** `main`

```bash

├── app
│   ├── migrations
│   ├── 0001_initial.py
│   ├── 0002_auto_20210521_2328.py
│   ├── 0003_auto_20210522_1128.py 

```

**Branch:** `feature/test-b`

```bash

├── app
│   ├── migrations
│   ├── 0001_initial.py
│   ├── 0002_auto_20210521_2328.py
│   ├── 0003_auto_20210522_1128.py \___________________ Both dependent on 0002_auto_20210521_2328.py
│   ├── 0003_auto_20210522_1228.py /

```

Running [`makemigrations`](https://docs.djangoproject.com/en/3.2/ref/django-admin/#django-admin-makemigrations) fails with the following error:

    CommandError: Conflicting migrations detected; multiple leaf nodes in the migration graph: (0003_auto_20210522_1128, 0003_auto_20210522_1228 in app).
    To fix them run 'python manage.py makemigrations --merge'

Using the [`--merge`](https://docs.djangoproject.com/en/3.2/ref/django-admin/#cmdoption-makemigrations-merge) option creates a new migration file which might not be desired.

## Solution

`django-migration-fixer` identifies changes between the default branch `main`, and the feature branch `feature/test-b` and maintains a consistent dependency history as shown below:

**Branch:** `feature/test-b`

```bash

├── app
│   ├── migrations
│   ├── 0001_initial.py
│   ├── 0002_auto_20210521_2328.py
│   ├── 0003_auto_20210522_1128.py
│   ├── 0004_auto_20210522_1228.py  # Renames: '0003_auto_20210522_1228.py' → '0004_auto_20210522_1228.py'

```

`0004_auto_20210522_1228.py`

```py
...
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20210522_1128'),  # Replaced '0002_auto_20210521_2328' → '0003_auto_20210522_1128'
    ]

    operations = [
        ...
    ]
```

> NOTE: :warning:
>
> *   This also works when there are conflicts detected on the default branch.
>
>     i.e You can run `python manage.py makemigrations --fix` on the `main` branch
>     which relies on primitively picking the first migration file.
>
>     e.g `(0003_auto_20210522_1128, 0003_auto_20210522_1228 in app)`
>     would result in `0003_auto_20210522_1128.py` being picked as the
>     base migration which might not be accurate in every case and is not recommended.

### Assumptions

The final migration on the default branch would be used as the base for all subsequent migrations.

## Found a Bug?

To file a bug or submit a patch, please head over to [django-migration-fixer on github](https://github.com/tj-django/django-migration-fixer/issues).

If you feel generous and want to show some extra appreciation:

Support me with a :star:

[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]

[buymeacoffee]: https://www.buymeacoffee.com/jackton1

[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
