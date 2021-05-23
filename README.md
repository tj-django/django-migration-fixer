# django-migration-fixer
Fix issues with django migration nodes on multiple branches


## Installation

```bash script
$ pip install django-view-breadcrumbs
```

## Add `migration_fixer` to your INSTALLED_APPS

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
