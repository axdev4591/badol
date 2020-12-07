#!/bin/bash

#Step for test
pwd

echo '######---------- Creating virtual environement -----------#####\n'
pipenv shell

echo '######---------- Install requirements -----------####\n'
pip install -r requirements.txt


echo '######---------- run tests -----------####\n'
./manage.py jenkins --enable-coverage

echo '######---------- deactivate virtual env -----------####\n'

exit