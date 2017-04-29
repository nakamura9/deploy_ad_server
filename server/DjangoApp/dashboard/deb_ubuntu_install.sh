#will work
apt-get update
apt-get install python-django
apt-get install git
apt-get install vlc

git clone https://github.com/nakamura9/deploy_ad_server.git

cd deploy_ad_server/server/DjangoApp/dashboard

python manage.py makemigrations
python manage.py migrate

python manage.py runserver 0.0.0.0 8000