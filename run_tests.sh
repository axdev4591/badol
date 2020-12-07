#!/bin/bash

#Step for test
pwd

echo '######---------- Creating virtual environement -----------#####\n'
pipenv shell

echo '######---------- Install requirements -----------####\n'

pip install -r ./requirements.txt

#### Jump to the workspace #####
echo '######---------- Jump to wokspace -----------####\n'
cd /var/lib/jenkins/workspace/$JOB_NAME/

echo '######---------- run tests -----------####\n'
pytest mexpenses/test --junitxml=./xmlReport/output.xml

echo '######---------- deactivate virtual env -----------####\n'
deactivate
exit