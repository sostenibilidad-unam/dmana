# Install AgNeS

External dependencies for running AgNeS are:

 - Git
 - Python 3.6 or greater
 - A unix-like OS

There are many ways of running this software. Here follows a recipe
using [virtualenv](http://virtualenv.org):

## Clone AgNeS repository

    $ git clone https://github.com/sostenibilidad-unam/agnes.git
	[ ... git clones the repo ]
	$ cd agnes
	$
	

## Setup and activate virtual environment

    $ virtualenv -p python3 venv3
	[ ... env is setup ]
	$ source venv3/bin/activate
	(venv3) $
	
## Install python dependencies

    (venv3) $ pip install -r website/requirements.txt
	[ ... pip installs all dependencies ]
	
## Initialize database

These commands will create the database schema of AgNeS into a local SQLite file.

	(venv3) $ cd website
	(venv3) $ ./manage.py migrate
	
## Create user

	(venv3) $ ./manage.py createsuperuser
	
Follow instructions to setup first user.

## Run local webserver

	(venv3) $ ./manage.py runserver
	
This is a development server suitable for local usage of AgNeS. Follow instructions in the [Django manual](https://docs.djangoproject.com/en/2.2/howto/deployment/) for a more robust setup.
