## django_valid - Validation des compétences
Gestion des épreuves de la validation des compétences

#### Installation des dépendances

    pip install django_cleanup django_ckeditor pytz openpyxl
    git clone https://github.com/Lapin-Blanc/django_survey
    git clone https://github.com/Lapin-Blanc/djangobeid

#### Personnalisation de settings.py

    INSTALLED_APPS += [
        'ckeditor',
        'django_survey',
        'djangobeid',
        # 'django_valid',
        'django_cleanup',
        ]

    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    CKEDITOR_UPLOAD_PATH = 'uploads/'

#### Modification des urls

    from django.conf.urls import url, include

ajouter dans urlpatterns :

    urlpatterns += [
        url(r'^sondage/', include("django_survey.urls")),
        url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    ]

#### Migrations

    ./manage.py makemigrations
    ./manage.py migrate
    ./manage.py createsuperuser

Dans settings.py, décommenter 'django_valid', puis :

    ./manage.py makemigratsion
    ./manage.py migrate
    ./manage.py collectstatic
