#!/bin/bash

#Step for test
pwd
ls

#export PIPENV_VENV_IN_PROJECT=1

echo '######---------- Creating virtual environement -----------#####\n'
#pipenv shell
virtualenv --python=python3.8 env 

echo '######---------- Install requirements -----------####\n'
#pip freeze requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install
cat requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 env/bin/pip install


echo '######---------- run tests -----------####\n'
#./manage.py jenkins --enable-coverage
env/bin/python manage.py jenkins

echo '######---------- deactivate virtual env -----------####\n'

exit