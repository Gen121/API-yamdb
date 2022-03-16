# api_yamdb
api_yamdb

## Описание

RESTful веб-сервис рейтингового сайта Yamdb на котором можно оставлять отзывы на произведения искусства, и делиться мнениями в комментариях.

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
