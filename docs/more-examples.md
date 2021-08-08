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
