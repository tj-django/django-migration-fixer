[![django migration fixer](./docs/images/logo.png)](https://tj-django.github.io/django-migration-fixer/)

[![PyPI](https://img.shields.io/pypi/v/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Coverage) [![codecov](https://codecov.io/gh/tj-django/django-migration-fixer/branch/main/graph/badge.svg?token=peNs0PpfP6)](https://codecov.io/gh/tj-django/django-migration-fixer) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Total alerts](https://img.shields.io/lgtm/alerts/g/tj-django/django-migration-fixer.svg?logo=lgtm\&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-migration-fixer/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/tj-django/django-migration-fixer.svg?logo=lgtm\&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-migration-fixer/context:python) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Grade)

[![Test](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml) [![Upload Python Package](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml) [![Run linters](https://github.com/tj-django/django-migration-fixer/actions/workflows/lint.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/lint.yml)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![Downloads](https://pepy.tech/badge/django-migration-fixer/month)](https://pepy.tech/project/django-migration-fixer)

# django-migration-fixer

Maintain a consistent migration history when conflicts occur as a result of changes made using different versions of the default branch.

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

### For specifying a different default branch

Run:

```bash
$ python manage.py makemigrations -b master --fix
```

## Features

*   Resolve migration conflicts on PR branches
*   Resolve migration conflicts on the default branch **(NOT RECOMMENDED)**
*   Supports default migration modules i.e (`0001_....py`)
*   Supports named migration modules i.e (`custom_migration.py`)
*   Re-nummber all migrations using the last migration on the default branch i.e `main` or `develop`

## Example

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
