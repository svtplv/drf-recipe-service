# Foodgram
## Описание:

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Стек технологий:
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

### Примеры запросов:
***Получить рецепт:***
```
GET http://localhost:9000/api/recipes/1/
```
Ответ:
```
{
    "id": 1,
    "tags": [
        {
            "id": 2,
            "name": "Обед",
            "color": "#19f081",
            "slug": "lunch"
        }
    ],
    "author": {
        "email": "second_user@email.org",
        "id": 3,
        "username": "second-user",
        "first_name": "Андрей",
        "last_name": "Макаревский",
        "is_subscribed": false
    },
    "ingredients": [
        {
            "id": 1,
            "name": "абрикосовое варенье",
            "measurement_unit": "г",
            "amount": 25
        }
    ],
    "is_favorited": false,
    "is_in_shopping_cart": false,
    "name": "Нечто съедобное (пробовать на свой страх и риск)",
    "image": "http://foodgram-svt.duckdns.org/media/recipe/images/l-intro-1660422159.jpg",
    "text": "Приготовьте как нибудь эти ингредиеты, не забудьте посолить.",
    "cooking_time": 12
}
```
***Добавить рецепт в избранное:***
```
POST http://localhost:9000/api/recipes/{id}/favorite/
```

Ответ:
```
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```



### Авторы:
[Святослав Поляков](https://github.com/svtplv)
