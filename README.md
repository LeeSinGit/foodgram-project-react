
**FOODGRAM - FINAL PROJECT**


### Как запустить проект:
****
#### ШАГ 0 - Клонировать проект к себе на PC;
```
git clone git@github.com:LeeSinGit/foodgram-project-react.git
```
#### ШАГ 1 - Зайти в папку infra проекта;
```
cd foodgram-project-react/infra/
```
#### ШАГ 2 - Применить команду;
```
docker-compose up --build
```
#### Данные админки | URL.

ip: 158.160.27.151 (не указывал в настройках nginx и .env, выдаёт ошибку)

URL: https://foodgram-final.hopto.org/

Userame: Admin;
Email: admin2019@yandex.ru;
Password: admin.


#### Импорт из CSV в базу данных был выполнен с помощью:
Копирование с пк на сервер.
```
scp -i C:/Dev/vm_access/yc-semenlisin2019 C:/Dev/foodgram-project-react-master/data/* yc-user@158.160.27.151:/home/yc-user/foodgram/data/
```
Копирование с сервера в докер контейнер с БД.
```
docker cp data/ingredients.csv foodgram-db:/ingredients.csv
```
Копирование данных из файла основной директории контейнера в БД.
```
COPY baseapp_ingredient (name, measurement_unit) FROM '/ingredients.csv' DELIMITER ',' CSV HEADER;
```

#### Виртуальное окружение.
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```
****
#### Примеры запросов.

Получить токен регистрации.

```
http://foodgram-final.hopto.org/api/auth/token/login/
```

Пример 'body -> json' (в проекте такого пользователя нет).
```
{
  "password": "OEFEFJjdhwedheh2443",
  "email": "vpupkin665@yandex.ru"
}
```

Получить теги.
```
http://foodgram-final.hopto.org/api/tags/
```

Получить ингредиенты.
```
http://localhost/api/ingredients/
```

### *Над проектом работал Лисин Семён :heart:*
### *Код написан на языке Python :v:*
