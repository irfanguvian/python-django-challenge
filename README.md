# python-django-challenge

1. git clone
2. make virtual enviroment, python -m venv your_env_name
3. source your_env_name/bin/activate
4. pip install django djangorestframework black pylint pylint-django
5. python manage.py makemigrations
6. python manage.py migrate
7. python manage.py runserver

note : make sure, token from /api/v1/init is use in Authorization header, `Token your_token_here`
