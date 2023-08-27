**FOODGRAM - FINAL PROJECT**

### Как запустить проект:

---

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

#### Импорт из CSV в базу данных был выполнен с помощью:

```
docker cp data/ingredients.csv foodgram-db:/ingredients.csv
```

```
COPY baseapp_ingredient (name, measurement_unit) FROM '/ingredients.csv' DELIMITER ',' CSV HEADER;
```

#### Данные админки:

Username(*Ник*): Admin

Email(*Электронная почта*): admin2019@yandex.ru

Password(*пароль*): admin

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

---

### *Над проектом работал Лисин Семён ❤️*

### *Код написан на языке Python ✌️*
