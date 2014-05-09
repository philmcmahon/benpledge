Bristol Energy Network Pledge Application
=========

This application has been developed for Bristol Energy Network (BEN) and the Centre for Sustainable Energy (CSE) as part of a universtity project.

Please note: In order to work on this application you will need access to CSE's Housing Assessment Tool data. I can provide the data, but only at the approval of CSE. 

Installation
===========

I recommend that [virtualenv] is used to create a separate environment for the project. Otherwise you will need to make sure you have [pip] installed.

MySQL was used to develop the current version of the applicaiton, other SQL backends should also work.

Install requirements (you will be asked to provide a password for MySQL):

    sudo apt-get install mysql-server libmysqlclient-dev python-dev



Create a database for the project (if you choose a different password be sure to update bpdbconfig.cnf) :

    mysql -u root -p
    CREATE DATABASE db_benpledge;
    CREATE USER 'benpledge'@'localhost' IDENTIFIED BY 'password';
    GRANT ALL ON db_benpledge.* TO 'benpledge'@'localhost';
    exit


Clone the repository
    
    git clone [git-repo-url] benpledge
    cd benpledge
    
Install application dependencies:

    pip install -r requirements.txt  --allow-external PIL --allow-unverified PIL

Setup the database (you will be asked to create a new user):

    python manage.py syncdb
    python manage.py schemamigration publicweb --initial
    python manage.py migrate publicweb
    
You should now be able to run:

    python manage.py runserver

If you wish to use the account you made when running syncdb with the application you'll need to add a UserProfile for it. You can do this using the admin interface at  http://127.0.0.1:8000/admin/ 

You will now need to load some data into the database in order for the application to function properly. Some of the required data is included in the repository but the HAT and DECC data will need to be obtained by contacting me. To load the provided data:

    python manage.py loaddata /publicweb/fixtures/benpledge_publicweb_data.json

If you have been provided with the HAT data and DECC datasets, you can load them into the database by placing the .csv files in benpledge/publicweb/sql/ and executing the SQL commands in load_hat_data_sql.

Finally, in order to make requests to the Google Maps API, you will need an API key for the Google Maps Geolocation API. You can get an API key from the [Google APIs console]. Create a Python file in the /benpledge/publicweb/ directory called benpledge_keys.py and add the following line to it:

    GOOGLE_API_KEY = your_api_key
    
Development
==========
The application is written using the Django web framework. If you are new to the framework I recommend you work through the [Django tutorial].

The main components are:


 * URL Config file - urls.py - this file dictates which view handles requests to a URL
 * Views - publicweb/views.py - there is one view for each page of the application.
 * Models - publicweb/models.py - this file defines the database models for the application
 * Forms - publicweb/forms.py
 * Helper functions - publicweb/utils.py - contains all the methods used by the views to fetch database results, geolocate addresses etc
 * Settings - benpledge/settings.py
 * Tests - publicweb/tests.py
 * Templatetags - publicweb/templatetags/publicweb_filters.py - these are used by templates to help render a page

Database migrations in the application are handled using django-south. After you have updated models.py, in order to update the databse you will need to run:

    python manage.py schemamigration publicweb --auto
    python manage.py migrate publicweb
    
Testing 
--------
In order to run the tests included with the application (and to write more), you will need to create fixtures to be used in the test database. You can do so using the publicwebdatadump.sh script in /benpledge/scripts/ - this script creates fixtures from the first 50 rows of the larger tables, and dumps the smaller tables in their entirity. For more information on Django test fixtures see the [django testing documentation].

    ./scripts/publicwebdatadump.sh
    
The included tests rely on the user test99 existing in the database. Either create this user (with password test99) or change tests.py to use a different user. Then, you can run the tests using the following command:

    // run all tests
    python manage.py test publicweb
    // run all tets in TestCase
    python manage.py test publicweb.tests.TestCase
    // run test_method
    python manage.py test publicweb.tests.TestCase.test_method

    
Templates
---------
Django provides a powerful templating system which supports template inheritance. You can find out which template is used for a page by looking at the return value of the view which renders the page.

Main templates:

 * base.html - all templates extend this one, it contains the header, footer and navigation bar of the application
 * base_offset.html - used to ensure content is situated below the toolbar
 * form_base.html - When passed a Django form object as context, this template will render the form as a bootstrap horizontal form, together with any error messages
 * base_pledges_page - extended by all pledges, my pledegs and area pledges pages - contains the map javascript and HTML

CSS, Javascript
------------
In benpledge/publicweb/static/publicweb you will find the static files used in the application. syle.css and publicweb_scripts.js are the most relevant of these, the rest are mainly third party libraries.

[virtualenv]:https://virtualenv.pypa.io/en/latest/
[pip]:https://pypi.python.org/pypi/pip
[Google APIs console]: https://code.google.com/apis/console/
[Django tutorial]:https://docs.djangoproject.com/en/dev/intro/tutorial01/
[django testing documentation]: https://docs.djangoproject.com/en/1.6/topics/testing/