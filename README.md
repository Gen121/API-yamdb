# api_yamdb
api_yamdb

## Описание

RESTful веб-сервис рейтингового сайта Yamdb на котором можно оставлять
отзывы на произведения искусства, и делиться мнениями в комментариях.

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Gen121/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

В целях безопасности SECRET_KEY проекта размещен в окружении,
для работы с которым используется библиотека python-dotenv.

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## Документация

После запуска сервера доступна в браузере по ссылке 

```
http://127.0.0.1:8000/redoc/
```

## Тестовая база данных

Создание тестовой базы данных осуществляется с помощью файла управления Django-проектом:

```
api_yamdb\manage.py
```

Файл скрипта располагается в следующем каталоге:

```
api_yamdb\reviews\management\commands\fill_db.py
```

Что бы создать тестовую базу нужно выполнить команду:

```
python3 manage.py fill_db

```

## Авторы проекта

![Михаил Патраков](<img src="https://avatars.githubusercontent.com/u/93536393?v=4" width="150"> "Михаил Патраков") [Михаил Патраков](https://github.com/MikhailPatrakov) - 
система регистрации и аутентификации, права доступа, работа с токенами, система подтверждения через e-mail

![Константин Тошин](<img src="https://avatars.githubusercontent.com/u/93771436?v=4" width="150"> "Константин Тошин") [Константин Тошин](https://github.com/KonstantinToshin) -
система отзывов, комментариев и рейтинга: модели, представления, сериализация и маршрутизация для них

![Евгений Челноков](<img src="https://avatars.githubusercontent.com/u/71381458?v=4" width="150"> "Евгений Челноков") [Евгений Челноков](https://github.com/Gen121) -
система категорий, жанров и произведений: модели, представления, сериализация и маршрутизация для них