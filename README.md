### Yatube - соцсеть для блогеров

это место где вы можете делиться своими публикациями, а так же выражать свое мнение в комментариях и подписываться на любимых авторов.  В проекте реализована возможность размещения постов, комментариев к ним, подписки на авторов, сортировка по группам и пагинация. Так же написаны тесты для проверки функций сервиса.

Стек: Python, Django, PostgreSQL, Gunicorn, Nxinx, pytest

# Как запустить проект на Windows:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/MrKep/Yatube
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

Активация виртуального окружения для Windows
```
source venv/script/activate
```
Активация виртуального окружения для Linux и MacOS
```
source venv/bin/activate
```

Обновить pip до актуальной версии

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

# Проект будет откроется по адресу:
http://127.0.0.1:8000/
