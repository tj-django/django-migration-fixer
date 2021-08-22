![logo](https://user-images.githubusercontent.com/17484350/124649379-6821ad00-de66-11eb-9b0e-890913c65311.png)

[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Coverage) [![codecov](https://codecov.io/gh/tj-django/django-migration-fixer/branch/main/graph/badge.svg?token=peNs0PpfP6)](https://codecov.io/gh/tj-django/django-migration-fixer)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/tj-django/django-migration-fixer.svg?logo=lgtm\&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-migration-fixer/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/tj-django/django-migration-fixer.svg?logo=lgtm\&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-migration-fixer/context:python) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Grade)

[![Test](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml) [![Upload Python Package](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml) [![Run linters](https://github.com/tj-django/django-migration-fixer/actions/workflows/lint.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/lint.yml) [![Updates](https://pyup.io/repos/github/tj-django/django-migration-fixer/shield.svg)](https://pyup.io/repos/github/tj-django/django-migration-fixer/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![PyPI](https://img.shields.io/pypi/v/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![Downloads](https://pepy.tech/badge/django-migration-fixer)](https://pepy.tech/project/django-migration-fixer) [![Public workflows that use this action.](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi-tj-actions1.vercel.app%2Fapi%2Fgithub-actions%2Fused-by%3Faction%3Dtj-django%2Fdjango-migration-fixer%26badge%3Dtrue)](https://github.com/search?o=desc\&q=tj-django+django-migration-fixer+language%3AYAML\&s=\&type=Code)

# django-migration-fixer

Resolve django makemigrations `multiple leaf nodes in the migration graph` by ensuring that migration files and dependencies are always ordered regardless of remote changes, without having to run `python manage.py makemigrations --merge`

## Features

*   100% test coverage.
*   Maintain a consistent migration history when conflicts occur as a result of changes made using different versions of the target branch.
*   Resolve migration conflicts on Pull Request branches
*   Resolve migration conflicts on the default branch **(NOT RECOMMENDED)**
*   Supports default migration modules i.e (`0001_....py`)
*   Re-number all migrations using the last migration on the target branch.

## Example

#### After merging the default branch

![Screen Shot 2021-07-06 at 2 21 46 PM](https://user-images.githubusercontent.com/17484350/124648930-d7e36800-de65-11eb-99a3-bf806ecfd32b.png)

#### After running django-migration-fixer

![Screen Shot 2021-07-06 at 2 22 31 PM](https://user-images.githubusercontent.com/17484350/124649105-0feaab00-de66-11eb-80f3-7987d67b361d.png)

### Assumptions

The final migration on the default branch would be used as the base for all subsequent migrations.

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

### Setup using Github Actions

> NOTE: :warning:
>
> *   To get this action to work you'll need to install [django-migration-fixer](#installation) and update your `INSTALLED_APPS` setting.

## Inputs

|   Input       |    type     |  required      |  default                      |  description               |
|:-------------:|:-----------:|:--------------:|:-----------------------------:|:--------------------------:|
| managepy-path |  `string`   |    `true`     | `./manage.py`                  | The location of manage.py. |
| default-branch |  `string`  |    `false`     |  `${{ github.base_ref }}`      |  The default branch or <br> target branch of a Pull request.  |
| force-update |  `string`  |    `false`     |        |  Force update the target branch <br> locally when git fetch fails.  |

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
        uses: tj-django/django-migration-fixer@v1.2.1
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

See: https://github.com/tj-django/django-clone for a working example.

## Test Platforms

*   [`ubuntu-*`](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idruns-on)
*   [`macos-*`](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idruns-on)
*   [`windows-*`](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idruns-on)

## Found a Bug?

To file a bug or submit a patch, please head over to [django-migration-fixer on github](https://github.com/tj-django/django-migration-fixer/issues).

If you feel generous and want to show some extra appreciation:

Support me with a :star:

[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]

[buymeacoffee]: https://www.buymeacoffee.com/jackton1

[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
