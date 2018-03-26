# Hotel Reservation System

This is a room reservation system for hotels.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

```
### Install Pip
sudo easy_install pip

### Please take a look at the requirements.txt file for the project specific dependencies
Run the following command in your terminal
pip freeze - This shows the python packages installed on the current machine and you can identify if there are any version differences with requirements.txt file

```

### Installing

Installation examples that tell you have to get a development env running

```
To seperate different projects and it's dependencies, I would recommend to use virtualenv.

If the project requires a specific version of a package, let's say django==1.8.7, run the following command

pip install Django==1.8.7

```

## Setting up local environment

Add the following in .bash_profile or .bashrc file of the system.

```
export DJANGO_SETTINGS_MODULE = 'hotel_management.settings'
```

Now source the file in which the above command was added,

```
Running the following command applies the changes as the system variables.

source .bash_profile
```

In order to create migrations from the scratch, delete the files in reservation/migrations module and run the following command
```
python manage.py makemigrations
```

To apply the migrations to the database, run the following command
```
This will apply all the unapplied migrations in the project to the database (Using in-memory sqlite database for purposes of development)

python manage.py migrate

If you would like to apply only a specific migration in the app, <migration_name> is optional if you would like
to apply all the migrations of a particular app.

python manage.py migrate <app_name> <migration_name>
```

## To Run a local development server, run the following command
```
 python manage.py runserver

 Django starts the development server by default on 8000 port, but if you'd like to run it on an alternate port, look at the command below

 python manage.py runserver <port_num>
```

## Following are the APIs available for this project
```
List of Hotels - /api/hotels
To access a specific hotel - /api/hotels/<id>

List of reservations - /api/reservations
To access a specific reservation - /api/reservations/<id>
```

## Running the tests
Django uses sqlite as it's default database, each test has a setup code and once the test it done, db is destroyed automatically after the tests have finished.

```
To run all the unit tests, run the following command

python manage.py test

To run only specific tests in a module

    python manage.py test <module_name>
    Eg: python manage.py test reservation - runs all the tests in reservation app

To run only a specific suite of tests in a module

    python manage.py test <module_name>.<tests_folder>.<suite_name>
    Eg: python manage.py test reservation.tests.TestNormalize_date

To run only a specific test in a suite

    python manage.py test <module_name>.<tests_folder>.<suite_name>.<unit_test_method>
    Eg: python manage.py test reservation.tests.TestNormalize_date.test_normalize_date

    The above only runs the test_normalize_date test in TestNormalize_date suite of unit tests in reservation/tests

```
