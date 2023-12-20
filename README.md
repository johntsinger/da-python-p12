# Python Application Developer - P12 - Develop a secure back-end architecture with Python and SQL

## Description

CRM (Customer Relationship Management) with command-line interface using django orm as a standalone.

Using jwt to authenticate users, permissions system and Sentry to track errors.

## Installation guide

### Clone repository with Git :

    git clone https://github.com/johntsinger/da-python-p12.git
    
or

### Download the repository :

- On the [project page](https://github.com/johntsinger/da-python-p12)
- Click on green Code button
- Click on download ZIP
- Extract the file.

### Install Python :

**Requires python 3.9 or higher**

If you don't have Python 3, please visit : https://www.python.org/downloads/ to download it !

### Virtual Environment :

#### Create a virtual environment in the project root :

    python -m venv env

#### Activate a virtual environment :

##### windows :

    env/Scripts/activate
    
##### linux/mac :

    source env/bin/activate
    
#### Install dependencies :

    pip install -r requirements.txt

## Go to the epicevents folder :

    cd epicevents

## Initialize CRM (admin):

##### Run migrations :

    python manage.py migrate

##### Set DSN for sentry (optional) :

    python manage.py setsentrydsn

or directly with option `--dsn` :

    python manage.py sentry --dsn DSN_ADDRESS

##### Set secret key (optional) :

*Note : A secret key is automatically generated the first time a command using manage.py is run.* </br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*You can find it in .env file.* </br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*Changing the secret key invalidates the JWT authentication token, after which the user must log in again.*

    python manage.py setsecretkey

or directly with option `--key` :

    python manage.py setsecretkey --key SECRET_KEY

##### Create a superuser :

    python manage.py createsuperuser

After that login as superuser using crm commands described below and add new collaborators

*Tip : First add a management collaborator and let him create other collaborators, since he has permission to create collaborators.*

## CRM usage :

### Commands :

Each commands must be like :

    python epicevents.py COMMAND SUB_COMMAND [ARGS] [OPTIONS]

#### Commands and sub commands:

  - login
  - collaborator
    - view
    - add
    - change
    - delete
  - client
    - view
    - add
    - change
  - contract
    - view
    - add
    - change
  - event
    - view
    - add
    - change
   
*Note : See help below to get more help with each commands.*

### Help :

All commands have a help option `--help`

##### Global help :
  
    python epicevents.py --help

##### Commands help :

    python epicevents.py COMMAND --help

##### Sub commands help :

    python epicevents.py COMMAND SUB_COMMAND --help

## Running Tests :

⚠️ **Migrations must be run before testing**

    python manage.py test

or more faster

    python manage.py test -- parallel

#### Coverage :

Coverage : 99%

Get tests coverage with [Coverage](https://coverage.readthedocs.io/en/coverage-5.1/) :

  - Update coverage file :

        coverage run manage.py test

  *Note : a cover file already exists, but you can update it with this command.*

  - Get report :
  
        coverage report

  - Get html format report :

        coverage html

   You can find the report in the htmlcov folder by openning the index.html file.

## Contact :
Jonathan Singer - john.t.singer@gmail.com\
Project link : https://github.com/johntsinger/da-python-p12
