# Epam final project
[![Build Status](https://travis-ci.com/antkrit/project.svg?branch=main)](https://travis-ci.com/antkrit/project)
[![Coverage Status](https://coveralls.io/repos/github/antkrit/project/badge.svg?branch=main)](https://coveralls.io/github/antkrit/project?branch=main)
[![Updates](https://pyup.io/repos/github/antkrit/project/shield.svg)](https://pyup.io/repos/github/antkrit/project/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Description
Personal Account - a simple website for ISP users. Users can view their information, payment history or top up their
balance. Administrators have the ability to view general information, search, edit and register users.
Also available a restful api that performs almost the same functionality.

## Installation
### Prerequisites
Make sure you have installed all of the following prerequisites on your development machine:
- Python 3.6+ (with `setuptools`,  `wheel` and `virtualenv` packages)

## Set up project
- **Clone repository**
```bash
git clone https://github.com/antkrit/project.git
```

- **Move into project root folder:**
```bash
cd project
```

- **Create and activate virtual environment:**

*Linux:*
```bash
virtualenv -p python .venv
source .venv/bin/activate
```

*Windows:*
```bash
python -m venv .venv
<full-path-to-project>\.venv\Scripts\activate.bat
```

- **Install dependencies:**

*Development requirements (include production requirements)*
```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

*Production requirements
(if you are only interested in launching the application,
these requirements are enough for you)*
```bash
python -m pip install -r requirements/prod.txt
python -m pip install -e .
```

- **Prepare database:**
```bash
flask db upgrade
flask populate admin -p secret_password  # create admin
flask populate cards  # create test payment cards(optional)
```

## Run application
### Configuration
All configuration objects are stored in [config.py](module/server/config.py).

Some environment variables (*you may edit their values*) are stored in [.env](.env) and [.flaskenv](.flaskenv).

### Deploy
- **Development server:**
```bash
flask run
```
Or
```bash
python module/app.py
```
Web app will be available locally `http://127.0.0.1/`.

- **Production server:**
```bash
cd module
python run.py
```
Web app will be available locally:
- Windows (waitress) - `http://127.0.0.1:8001/`
- Linux (gunicorn) - `http://127.0.0.1:8080/`

> API root: `/api/v1/`

## Tests:
**Run tests with coverage report:**
```bash
pytest --cov
```
All tests are stored in [module/tests](module/tests/)

## Module structure
```
module/
    ├── client
    |   ├── static/
    |   └── templates/
    ├── commands/
    |   ├── __init__.py
    |   └── common.py
    ├── server/
    |   ├── api/
    |   |   ├── resources/
    |   |   |   ├── ...
    |   |   └── schemas/
    |   |       ├── ...
    |   ├── models/
    |   |   ├── migrations/
    |   |   └── ...
    |   ├── static/
    |   |   ├── logs/
    |   |   └── ...
    |   ├── view/
    |   |   ├── admin/
    |   |   |   ├── __init__.py
    |   |   |   ├── forms.py
    |   |   |   └── routes.py
    |   |   ├── cabinet/
    |   |   |   └── ...
    |   |   └── login/
    |   |       └── ...
    |   ├── __init__.py
    |   └── config.py
    ├── tests/
    |   └── ...
    ├── __init__.py
    ├── app.py
    └── run.py
```

Run flask application
```
├── app.py
```

Run wsgi application with waitress(On Windows) or gunicorn(Linux)
```
└── run.py
```

### Client
Use this directory to store `html`, `css` and `js` files and everything related to them:
```
├── client
    ├── static/
    └── templates/
```

### Commands
Use this directory to store custom cli commands:
```
├── commands/
    ├── __init__.py
    ├── common.py
```

### Server
Use this directory to store everything related to the api:
```
...
├── server/
    ├── api/
    ...
```

Use this directory to store database models:
```
...
├── server/
    ...
    ├── models/
    ...
```

Use this directory to store static and temporary files:
```
...
├── server/
    ...
    ├── static/
    ...
```

Use this directory to store flask views:
```
...
├── server/
    ...
    ├── view/
    ...
```

Store all config objects in this file:
```
...
├── server/
    ...
    └── config.py
```

### Tests
Store all tests in this directory:
```
├── tests/
```
