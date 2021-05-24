#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

# with open("HISTORY.rst") as history_file:
#     history = history_file.read()

deploy_requires = [
    "bump2version",
    "readme_renderer[md]",
    "changes",
    "git-changelog",
]

docs_requires = [
    "watchdog[watchmedo]",
    "Sphinx",
]

install_requires = [
    "django",
    "djangorestframework",
]

setup_requires = ["pytest-runner"]

test_requires = [
    "pytest>=3",
    "tox",
    "tox-gh-actions",
    "coverage",
    "codacy-coverage",
]

lint_requires = [
    "flake8",
    "yamllint",
    "isort",
    "black",
    "mypy",
]

extras_require = {
    "development": [
        install_requires,
        deploy_requires,
        test_requires,
        lint_requires,
    ],
    "test": test_requires,
    "lint": lint_requires,
    "deploy": deploy_requires,
    "docs": docs_requires,
}

setup(
    author="Tonye Jack",
    author_email="jtonye@ymail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
    ],
    description="Resolve migration errors",
    install_requires=install_requires,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=False,
    keywords=[
        "migration fixer",
        "django migrations",
        "django migrations fixer",
        "migrations auto fix",
        "migrations fix",
        "migrations conflict resolver",
        "django migrations",
        "django migrations autofix",
    ],
    name="django-migration-fixer",
    packages=find_packages(include=["migration_fixer", "migration_fixer.*"]),
    setup_requires=setup_requires,
    test_suite="tests",
    tests_require=test_requires,
    extras_require=extras_require,
    url="https://github.com/tj-django/django-migration-fixer",
    project_urls={
        "Source": "https://github.com/tj-django/django-migration-fixer",
        "Documentation": "https://github.com/tj-django/django-migration-fixer",
    },
    version="0.0.3",
    zip_safe=False,
)
