![PyPI](https://img.shields.io/pypi/v/django-migration-fixer) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-migration-fixer)

# django-migration-fixer

## Problem

Maintain a linear migration history when conflicts occur as a result of changes made using different versions of the default branch.


### Example

**Branch:** `main`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py 

```


**Branch:** `feature/test-a`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py
  ├── 0003_auto_20210522_1128.py 

```

**Branch:**`feature/test-b`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py
  ├── 0003_auto_20210522_1228.py 

```


Both `feature/test-a` and `feature/test-b` share the last migration on `main` (`0002_auto_20210521_2328.py`) 


Once `feature/test-a` is merged into `main` you run into the problem of resolving migrations on `feature/test-b` which was dependent on `0002_auto_20210521_2328.py`

**Branch:** `main`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py
  ├── 0003_auto_20210522_1128.py 

```

**Branch:** `feature/test-b`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py
  ├── 0003_auto_20210522_1128.py \___________________ Both dependent on 0002_auto_20210521_2328.py
  ├── 0003_auto_20210522_1228.py /

```


Error running [`makemigrations`](https://docs.djangoproject.com/en/3.2/ref/django-admin/#django-admin-makemigrations)

```
CommandError: Conflicting migrations detected; multiple leaf nodes in the migration graph: (0003_auto_20210522_1128, 0003_auto_20210522_1228 in my_app).
To fix them run 'python manage.py makemigrations --merge'
```

Using the default `--merge` option creates a new migration file which might not be desired.


## Solution

`django-migration-fixer` identifies changes between the default branch `main`, and the feature branch `feature/test-b` and maintains a linear dependency history as shown below:

Run

```bash script
$ python manage.py makemigrations --fix
```


**Branch:** `feature/test-b`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py
  ├── 0003_auto_20210522_1128.py
  ├── 0004_auto_20210522_1228.py

```

> NOTE: This also works when there are conflicts detected on the default branch. i.e You can run `... makemigrations --fix` on the `main` branch. 

### Assumptions

The final migration on the default branch would be used as the base for all subsequent migrations.



## Installation

```bash script
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

```bash script
$ python manage.py makemigrations --fix 
```

### Specifying a different default branch name

Use:

```bash script
$ python manage.py makemigrations -b master --fix 
```


## Features
- Resolves migration conflicts on both the default branch or feature/PR branches
- Supports numbered migration files i.e (`0001_....py`)
- Supports non-numbered migration files i.e (`custom_migration.py`)
- Re-index all migrations using the last migration on the default branch i.e `main`
