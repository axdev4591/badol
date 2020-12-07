#!/bin/bash

#Step for test
pwd
ls

echo '######---------- Creating virtual environement -----------#####\n'
pipenv shell

echo '######---------- Install requirements -----------####\n'
pip freeze requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install


echo '######---------- run tests -----------####\n'
pip install Django
./manage.py jenkins --enable-coverage

echo '######---------- deactivate virtual env -----------####\n'

exit