# Cайт Foodgram - «Продуктовый помощник».
### Описание
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Адрес
Проект планируется к публикации в интернете.

### Технологии
Python 3.9
Django 3.2
Django Rest Framework 3.14
Docker
PostgreSQL
Gunicorn
Nginx

### Запуск проекта локально.
1. Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:Gashev1989/foodgram-project-react.git
cd foodgram-project-react
```

2. Cоздать файл виртуального окружения .env в директории infra/ по образцу в env.example:

```
cd infra/
```
```
touch .env
```
Файл вирутального окружения должен содержать:
```
DB_ENGINE=движок базы данных
DB_NAME=имя базы данных
POSTGRES_USER=логин для подключения к базе данных
POSTGRES_PASSWORD=пароль для подключения к БД
DB_HOST=название сервиса (контейнера)
DB_PORT=порт для подключения к БД
SECRET_KEY='секретный ключ проекта'
```

3. Запустить проект:

```
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```
4. Заполнить базу данных ингридиентами рецептов:

```
docker-compose exec backend python manage.py load_data
```

5. Открыть документацию проекта:

```
http://127.0.0.1/api/docs/
```

6. Через админку Django создать необходимые теги.
```
http://127.0.0.1/admin/
```
***

### Автор
Гашев Константин