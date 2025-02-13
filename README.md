![logo](https://user-images.githubusercontent.com/17484350/124649379-6821ad00-de66-11eb-9b0e-890913c65311.png)

[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Coverage)
[![codecov](https://codecov.io/gh/tj-django/django-migration-fixer/branch/main/graph/badge.svg?token=peNs0PpfP6)](https://codecov.io/gh/tj-django/django-migration-fixer)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1e607eb508f64cefad18f50d6ff920cf)](https://www.codacy.com/gh/tj-django/django-migration-fixer/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-migration-fixer\&utm_campaign=Badge_Grade)
[![Test](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/test.yml)
[![Upload Python Package](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml/badge.svg)](https://github.com/tj-django/django-migration-fixer/actions/workflows/deploy.yml)

[![PyPI](https://img.shields.io/pypi/v/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-migration-fixer)](https://pypi.python.org/pypi/django-migration-fixer) [![Downloads](https://pepy.tech/badge/django-migration-fixer)](https://pepy.tech/project/django-migration-fixer)
[![Public workflows that use this action.](https://img.shields.io/endpoint?url=https%3A%2F%2Fused-by.vercel.app%2Fapi%2Fgithub-actions%2Fused-by%3Faction%3Dtj-django%2Fdjango-migration-fixer%26badge%3Dtrue)](https://github.com/search?o=desc\&q=tj-django+django-migration-fixer+language%3AYAML\&s=\&type=Code)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# django-migration-fixer

Resolve django makemigrations `multiple leaf nodes in the migration graph` by ensuring that migration files and dependencies are always ordered regardless of remote changes, without having to run `python manage.py makemigrations --merge`.

## Table of Contents

*   [Features](#features)
*   [Installation](#installation)
    *   [Add `migration_fixer` to your INSTALLED\_APPS](#add-migration_fixer-to-your-installed_apps)
*   [Usage](#usage)
*   [Example](#example)
    *   [After merging the default branch](#after-merging-the-default-branch)
    *   [After running django-migration-fixer](#after-running-django-migration-fixer)
*   [Assumptions](#assumptions)
    *   [Specifying a different default branch](#specifying-a-different-default-branch)
*   [Setup using Github Actions](#setup-using-github-actions)
    *   [Inputs](#inputs)
*   [Test Platforms](#test-platforms)
*   [Found a Bug?](#found-a-bug)

## Features

*   Resolve migration conflicts on Pull Request branches
*   Resolve migration conflicts on the default branch **(NOT RECOMMENDED)**

## Installation

```bash
$ pip install django-migration-fixer
```

### Add `migration_fixer` to your INSTALLED\_APPS

```python

INSTALLED_APPS = [
    ...,
    "migration_fixer",
    ...,
]
```

## Usage

Merge the changes from the default branch or the target branch of the pull request.

```bash
$ git checkout main # OR: develop/another parent feature branch
$ git pull
$ git checkout feature/xxxx
$ git merge main
```

Fix the migration conflicts

```bash
$ python manage.py makemigrations --fix
```

By default this uses `main` as the default branch

## Example

### After merging the default branch

![Screen Shot 2021-07-06 at 2 21 46 PM](https://user-images.githubusercontent.com/17484350/124648930-d7e36800-de65-11eb-99a3-bf806ecfd32b.png)

### After running django-migration-fixer

![Screen Shot 2021-07-06 at 2 22 31 PM](https://user-images.githubusercontent.com/17484350/124649105-0feaab00-de66-11eb-80f3-7987d67b361d.png)

## Assumptions

The final migration on the default branch would be used as the base for all subsequent migrations.

### Specifying a different default branch

Run:

```bash
$ python manage.py makemigrations -b master --fix
```

## Setup using Github Actions

> NOTE: :warning:
>
> *   To get this action to work you'll need to install [django-migration-fixer](#installation) and update your `INSTALLED_APPS` setting.

### Inputs

|   Input       |    type     |  required      |  default                      |  description               |
|:-------------:|:-----------:|:--------------:|:-----------------------------:|:--------------------------:|
| managepy-path |  `string`   |    `true`     | `./manage.py`                  | The location of manage.py. |
| default-branch |  `string`  |    `false`     |  `${{ github.base_ref }}`      |  The default branch or <br> target branch of a Pull request.  |
| force-update |  `string`  |    `false`     |        |  Force update the target branch <br> locally when git fetch fails.  |
| skip-default-branch-update |  `string`  |    `false`     |        |  Skip pulling the latest <br> changes from the default branch.  |

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
        uses: tj-django/django-migration-fixer@v1.3.6
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
          git commit -m "Updated migrations"

      - name: Push migration changes
        if: steps.verify-changed-files.outputs.files_changed == 'true'
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          branch: ${{ github.ref }}
```

See: [here](https://github.com/tj-django/django-clone/blob/main/.github/workflows/migration-fixer.yml) for a working example.

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
