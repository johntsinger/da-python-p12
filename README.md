# Python Application Developer - P12 - Develop a secure back-end architecture with Python and SQL

## Description

CRM (Customer Relationship Management) with command-line interface using django orm standalone.



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

## Init CRM (admin):

Go to the epicevents folder :

    cd epicevents

Run migrations :

    python manage.py migrate

Set DNS for sentry (optional) :

    python manage.py sentry

Create a superuser :

    python manage.py createsuperuser

After that login as superuser using crm commands described below and add new collaborator

## CRM usage :

If you are not in epicevents folder :

    cd epicevents

#### Help :

All commands have a help option `--help`

Global help :
  
    py epicevents.py --help



## Running Tests :

    python manage.py test

or more faster

    python manage.py test -- parallel

#### Coverage :

Coverage : 98%

Get tests coverage with [Coverage](https://coverage.readthedocs.io/en/coverage-5.1/) :

  - Update coverage file :

        coverage run manage.py test

  Note : a cover file already exists, but you can update it with this command.

  - Get report :
  
        coverage report

  - Get html format report :

        coverage html

   You can find the report in the htmlcov folder by openning the index.html file.

## Contact :
Jonathan Singer - john.t.singer@gmail.com\
Project link : https://github.com/johntsinger/da-python-p12
