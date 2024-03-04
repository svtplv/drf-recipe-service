# Foodgram

## Информация для ревьюера
* Почта суперпользователя - admin@admin.ru
* Пароль суперпользователя - admin
* Адрес - http://foodgram-svt.duckdns.org/

## Описание:

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Используемые технологии:
* Python 3.10
* Django 4.2
* Django REST framework 3.14
* Docker 
* Docker Compose
* nginx
* PostgreSQL
* GitHub Actions

### Установка:

1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:svtplv/foodgram-project-react.git
```

2. Запустить Docker Compose с конфигурацией docker-compose.production.yml:
```
docker compose -f docker-compose.production.yml up -d
```

3. Собрать статику:
```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```

4. Выполнить миграции:
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

5. Наполненить БД подготовленными данными:
```
docker compose -f docker-compose.production.yml exec backend python manage.py import_data
```

### Документация:

```
http://localhost:9000/api/docs/
```
