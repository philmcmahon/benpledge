Bristol Energy Network Pledge Application
=========

This application has been developed for Bristol Energy Network (BEN) and the Centre for Sustainable Energy (CSE) as part of a universtity project.

Installation
===========

I recommend that [virtualenv] is used to create a separate environment for the project. Otherwise you will need to make sure you have [pip] installed.

MySQL was used to develop the current version of the applicaiton, other SQL backends should also work.

```
// install requirements. During the installation of mysql you will be asked to create a password for the root user.
sudo apt-get install mysql-server libmysqlclient-dev python-dev

// create database for the project
// if you choose a different password be sure to update bpdbconfig.cnf

mysql -u root -p
CREATE DATABASE db_benpledge;
CREATE USER 'benpledge'@'localhost' IDENTIFIED BY 'password';
GRANT ALL ON db_benpledge.* TO 'benpledge'@'localhost';
exit


git clone [git-repo-url] benpledge
cd benpledge
// install dependencies
pip install -r requirements.txt  --allow-external PIL --allow-unverified PIL

// setup database
cd benpledge
python manage.py syncdb
python manage.py schemamigration publicweb --initial
python manage.py migrate publicweb

// you should now be able to run
python manage.py runserver

```


[virtualenv]:https://virtualenv.pypa.io/en/latest/
[pip]:https://pypi.python.org/pypi/pip