# django-migration-fixer

## Problem

Maintain a linear migration history when conflicts occur due to changes made with different versions of the default branch.


### Example

**Branch:** `main`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py 

```


Branch: `feature/test-a`

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


## Solution

Using `django-migration-fixer` identifies changes between the default branch and your feature branch modifying the migrations to look like:

Branch: `feature/test-b`

```text

migrations
  ├── 0001_initial.py
  ├── 0002_auto_20210521_2328.py
  ├── 0003_auto_20210522_1128.py
  ├── 0004_auto_20210522_1228.py

```

after running 

```bash script
$ python manage.py makemigrations --fix
```


## Installation

```bash script
$ pip install django-view-breadcrumbs
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
