# Hazel
Hazel is the result of my final project as part of my OpenClassRooms training as a Python developer.
## About
It is a django web application that I created for the leisure center in my town. It allows families to register their children directly online and allows the director of the center to access information relating to the children. it also provides information relating to the leisure center.
## Sources
The informations relating to the holidays periods are from [data.education.gouv.fr](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/api/?disjunctive.description&disjunctive.location&disjunctive.zones&disjunctive.annee_scolaire&disjunctive.population) API.
## Languages, libraries and frameworks
This web app was developed with **python 3** and the **Django** framework version 3.  
Dynamic part of the site use [JQuery](https://jquery.com/).  
Icones are from [Font Awesome](https://fontawesome.com/).  
All required python's libraries are in the requirements.txt file.
## In local mode
### Install
If you want to try it on localhost.
- Fake and clone the [hazel github's repository](https://github.com/screw-pack/hazel.git).
- Create a python 3 virtual environement.
- Install the required modules with `pip install -r requirements.txt`.
- Install [postgresql](https://www.postgresql.org/download/).
- Create a data base with it ([Official Documentation](https://www.postgresql.org/docs/)).
- Create a `.env` file to hazel/config/settings which contain:
  ```
  ENV='local'
  ```
- Create a `local.py` file to hazel/config/settings which contain:
  ```
  SECRET_KEY = <your secret key>

  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': <your DB name>,
        'USER': <your DB user>,
        'PASSWORD': <your DB password>,
        'HOST': 'localhost',
        'PORT': '',
    }
  }
  ```
- You may populate the periods table with a custom command `./manage.py get_holidays`.  
*the script for this command is in hazel/booking/management/commands/get_holidays.py, you can modify it as you wish.*
- To launch the server `./manage.py runserver`.
- Open your web browser at http://127.0.0.1:8000/
### Tests
Some tests are available: run `./manage.py test` to perform them.
