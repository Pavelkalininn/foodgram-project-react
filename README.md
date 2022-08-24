# Foodgram - социальная сеть для обмена рецептами


## Описание

На данный момент написан только Django-бэк

##Запуск

Для запуска необходимо в директории api_foodgram выполнить

    python manage.py runserver  

также необходима БД Postgress или настроить Sqlite в settings.py:

    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


## Технологии

    Django==3.2.15
    django-filter==22.1
    django-templated-mail==1.1.1
    djangorestframework==3.13.1
    djangorestframework-simplejwt==4.8.0
    djoser==2.1.0
    drf-extra-fields==3.4.0
    filter==0.0.0.20200724
    isort==5.10.1
    Pillow==9.2.0
    python-dotenv==0.20.0
    requests==2.28.1




Автор: [__Паша Калинин__](https://github.com/Pavelkalininn)
