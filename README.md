# newsPortal
This application about news companies, users and users' posts.

## Mac

Creating the environment:

```
python3 -m venv venv  # create the python virtual environment
. venv/bin/activate  # activate the python virtual environment
pip install -r requirements.txt  # install our python dependencies
```

---

## Windows

Uninstall any previous installations of:
- Python
- PostgreSQL

Install Python 3.7.9 as Admin (https://www.python.org/downloads/release/python-379/)

Add both Python and Pip to Windows PATH Environment Variables
```
run sysdm.cpl
```

Creating the environment:
```
pip install virtualenv
virtualenv --python C:\Path\To\Python\python.exe venv
```

Installing dependencies:
```
. .\venv\Scripts\activate
pip install -r requirements.txt
```
---

## Environment variables:

- Create an `.env` file at the root of the project

## Dev DB Setup

1. Create DB via terminal:

 - ## Ubuntu

locally
```
sudo postgres
psql
CREATE DATABASE portal_db
```

with docker
```
docker-compose up --build
```

 - ## Mac

locally
```
brew install postgresql
psql
CREATE DATABASE currency_ex
```

with docker
```
docker-compose up --build
```

2. Run migrations

```
python manage.py makemigrations
python manage.py migrate
```

To populate DB with 10 companies, 200 users and 30 posts for each user:
```
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations --empty portal_app

- copy and insert the code from data-migration.txt into empty migration file

python manage.py migrate
```
