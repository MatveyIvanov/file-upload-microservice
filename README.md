# FastAPI File Upload Microservice
![Static Badge](https://img.shields.io/badge/python-3.11-brightgreen?style=flat&logo=python)
![Static Badge](https://img.shields.io/badge/FastAPI-0.112.0-brightgreen?style=flat&logo=python)
![Static Badge](https://img.shields.io/badge/coverage-75%25-brightgreen?logo=pytest)
![Static Badge](https://img.shields.io/badge/tests-passing-brightgreen?style=flat&logo=pytest)
![Static Badge](https://img.shields.io/badge/flake8-passing-brightgreen?style=flat&logo=python)
![Static Badge](https://img.shields.io/badge/mypy-passing-brightgreen?style=flat&logo=python)

## Оглавление
* [Разворачивание проекта](#разворачивание-проекта)
    * [Зависимости](#зависимости)
    * [Окружение](#окружение)
    * [Запуск в локальном окружении](#запуск-в-локальном-окружении)
    * [Запуск в тестовом окружении](#запуск-в-тестовом-окружении)
    * [Запуск в прод окружении](#запуск-в-прод-окружении)
    * [После запуска](#после-запуска)
    * [Возможные ошибки](#возможные-ошибки)
* [Стэк](#стэк)
    * [Основные инструменты](#основные-инструменты)
    * [Другие библиотеки / интеграции](#другие-библиотеки--интеграции)
* [Запуск тестов](#запуск-тестов)
    * [Внутри Docker-контейнера (рекомендуется)](#внутри-docker-контейнера-рекомендуется)
    * [Вне Docker-контейнера](#вне-docker-контейнера)
* [Запуск flake8](#запуск-flake8)
    * [Внутри Docker-контейнера (рекомендуется)](#внутри-docker-контейнера-рекомендуется-1)
    * [Вне Docker-контейнера](#вне-docker-контейнера-1)
* [Запуск mypy](#запуск-mypy)
    * [Внутри Docker-контейнера (рекомендуется)](#внутри-docker-контейнера-рекомендуется-2)
    * [Вне Docker-контейнера](#вне-docker-контейнера-2)
* [Разработка](#разработка)
    * [Форматирование кода](#форматирование-кода)
    * [Git хуки](#git-хуки)

## Разворачивание проекта
### Зависимости
* docker
* docker compose
* python 3.8+ (опционально, для локального запуска pytest/flake8/mypy)
* poetry (опционально, для локального запуска pytest/flake8/mypy)
### Окружение
Перед запуском контейнеров, необходимо убедиться, что директории [docker](./docker/) присутствует файл `.env`, в котором заполнены все необходимые переменные окружения.<br>
Названия этих переменных можно посмотреть в [.env.example](./docker/.env.example)<br>

<details>
<summary><b>Подробное описание переменных окружения</b></summary>
<p>

#### REGISTRY
Ссылка на container registry. Необходимо заполнить, если используется compose файл с указанными image для кастомных сборок (например, [docker-compose.main.yml](./docker/docker-compose.main.yml))
#### ENVIRONMENT
Окружение (development, production, testing, etc). Может быть использовано для различных нужд в рамках проекта
#### PROJECT_NAME
Название проекта
#### DEBUG
Режим отладки<br>
0 - выключен<br>
1 - включен<br>
Если включен, то:
* 500 ошибки сервера не будут обработаны обработчиком исключений
* В логах будут отображаться запросы в БД, генерируемые в рамках запроса
#### PROD
Режим прод окружения<br>
0 - выключен<br>
1 - включен<br>
Если выключен, то:
* Будет доступна документация swagger-ui/redoc
* Чувствительные данные будут исключены из логов
#### MEDIA_PATH
Путь к директории, в которой хранятся медиа-файлы
#### MEDIA_URL
Префикс в ссылке для медиа-файлов
#### STATIC_PATH
Путь к директории, в которой хранятся статические файлы
#### STATIC_URL
Префикс в ссылке для статических-файлов
#### LOG_PATH
Путь к директории, в которой хранятся лог-файлы
#### Database
При первом запуске DB_NAME, DB_USER, DB_PASSWORD могут быть любыми<br>
При дальнейших запусках DB_NAME, DB_USER, DB_PASSWORD должны быть такими же, как при первом запуске<br>
DB_HOST должен соответствовать названию сервиса БД из compose конфигурации<br>
DB_PORT должен соответствовать порту БД из compose конфигурации<br>
#### Nginx
NGINX_OUTER_PORT - порт, через который можно обращаться к контейнеру nginx<br>
NGINX_INNER_PORT - порт, на который будут переадресовываться все запросы внутри контейнера nginx<br>
#### ASGI
ASGI_PORT - порт, по которому можно обращаться к asgi сервису
#### Logging
LOGGING_SENSITIVE_FIELDS - чувствительные поля, которые нужно игнорировать при записи лога. Должны быть разделены через запятую, без пробелов<br>
LOGGING_LOGGERS - названия логеров. Должны быть разделены через запятую, без пробелов<br>
LOGGING_MAX_BYTES - максимальное кол-во байт на один лог файл<br>
LOGGING_BACKUP_COUNT - максимальное кол-во бэкап файлов для логов<br>
#### Docker Compose Specific
RESTART_POLICY - политика рестарта контейнеров<br>
NGINX_VERSION - версия Nginx<br>
POSTGRES_VERSION - версия PostgreSQL<br>
ASGI_TARGET - образ для сборки asgi сервиса<br>
*_CPUS - лимит ядер на контейнер<br>
*_MEM_LIMIT - лимит памяти на контейнер<br>
*_MEM_RESERVATION - запас памяти на контейнер<br>
#### UPLOAD_MAX_SIZE_IN_BYTES
Максимальный размер загружаемого файла в байтах
# S3
Доступы к S3-хранилищу
# Scheduler
SCHEDULER_DISK_CLEANUP_EVERY - очищать диск каждые n минут
SCHEDULER_REMOVE_FILES_OLDER_THAN - удалять файлы через n дней после создания<br>
SCHEDULER_REMOVE_FILES_UNUSED_MORE_THAN - удалять файлы через n дней после последнего обновления<br>
</p>
</details>

### Запуск в локальном окружении
```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml up
```
или
```bash
make localup
```
После запуска проект будет доступен по адресу http://localhost:.../
### Запуск в тестовом окружении
```bash
docker-compose up
```
или
```bash
make up
```
### Запуск в прод окружении
```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.main.yml up
```
или
```bash
make mainup
```
### После запуска
Проект станет доступен по порту ${NGINX_OUTER_PORT}<br>
В локальном окружении достаточно перейти по адресу http://localhost:${NGINX_OUTER_PORT}/<br>
В другом окружении необходимо настроить домен, при обращении к которому веб-сервер (Nginx/Apache) будет проксировать все запросы на порт ${NGINX_OUTER_PORT}
### Возможные ошибки
Если на хосте установлена docker compose версии >2, то может возникнуть ошибка синтаксиса команды. В таком случае в командах выше нужно заменить
```bash
docker-compose
```
на 
```bash
docker compose
```

## Стэк
### Основные инструменты
* Используемый язык программирования — `Python 3.11`
* Используемый фреймворк — `FastAPI 0.112.0`
* Используемая СУБД — `PostgreSQL 14.5`
### Другие библиотеки / интеграции
* `uvicorn (0.30.5)` — HTTP-сервер для FastAPI
* `psycopg (2.9.7)` — библиотека для работы с PostgreSQL в Python
* `JSON-log-formatter (1.0)` — библиотека для форматирования логов в JSON-формате
* `dependency-injector (4.41.0)` — библиотека для внедрения зависимостей (DI)
* `pytest (8.2.1)` — библиотека для тестирования
* `pytest-cov (5.0.0)` — библиотека для оценки покрытия кода тестами через pytest
* `pytest-mock (3.14.0)` — библиотека для мока зависимостей через pytest
* `pytest-timeout (2.3.1)` — библиотека для ограничения времени выполнения тестов через pytest 
* `concurrent-log-handler (0.9.25)` — библиотека для последовательной записи логов в файлы при запуске веб приложения через несколько воркеров (как в uvicorn)
* `mypy (1.10.0)` — статический анализатор типов
* `flake8 (7.1.0)` — инструмент линтинга для Python
* `black (24.4.2)` — библиотека для форматирования кода на языке Python
* `isort (5.13.2)` - библиотека для сортировки импортов

## Запуск тестов
### Внутри Docker-контейнера (рекомендуется)

1. Зайти в контейнер `asgi` через команду

    ```bash
    docker exec -it ${PROJECT_NAME}-asgi bash
    ```
2. Начать выполнение тестов через команду
    ```bash
    pytest
    ```

или
```bash
make test
```

### Вне Docker-контейнера

При таком запуске тесты, в которых тестируется работа с БД, выполнятся с ошибкой<br>
При ошибке выполнения команды запустите тесты внутри Docker-контейнера
1. Перейти в директорию с [конфигурационным файлом](./src/pyproject.toml)
2. Начать выполнение тестов через команду

    ```bash
    poetry run pytest
    ```

## Запуск Flake8
### Внутри Docker-контейнера (рекомендуется)

1. Зайти в контейнер `asgi` через команду

    ```bash
    docker exec -it ${PROJECT_NAME}-asgi bash
    ```
2. Начать выполнение flake8 через команду
    ```bash
    flake8 .
    ```

или
```bash
make lint
```

### Вне Docker-контейнера

1. Перейти в директорию с [конфигурационным файлом](./src/.flake8)
2. Начать выполнение flake8 через команду

    ```bash
    poetry run flake8 .
    ```

## Запуск mypy
### Внутри Docker-контейнера (рекомендуется)

1. Зайти в контейнер `asgi` через команду

    ```bash
    docker exec -it ${PROJECT_NAME}-asgi bash
    ```
2. Начать выполнение mypy через команду
    ```bash
    mypy .
    ```

или
```bash
make typecheck
```

### Вне Docker-контейнера

При возникновении ошибок запуск возможен только внутри Docker-контейнера
1. Перейти в директорию с [конфигурационным файлом](./src/pyproject.toml)
2. Начать выполнение mypy через команду

    ```bash
    poetry run mypy .
    ```

## Разработка
### Форматирование кода
При разработке рекомендуется использовать [black](https://pypi.org/project/black/), чтобы поддерживать чистоту кода и избегать лишних изменений при работе с гитом.<br>
Пример конфигурационного файла для Visual Studio Code `.vscode/settings.json`:
```json
{
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true
    }
}
```

### Git хуки
При разработке рекомендуется использовать [pre-commit](https://pre-commit.com/), чтобы перед формированием МР код был уже подготовленным и поверхностно проверенным (например, через `flake8`)<br><br>
**Для использования должны быть установлены dev-зависимости**

#### Pre-commit хуки
Установка
```bash
poetry run pre-commit install
```
Удаление
```bash
poetry run pre-commit uninstall
```
После установки, при каждом коммите будут отрабатывать хуки из [конфигурационного файла](./src/.pre-commit-config.yaml), предназначенные для коммитов (`stages: [commit]`)

#### Pre-push хуки
Установка
```bash
poetry run pre-commit install --hook-type pre-push
```
Удаление
```bash
poetry run pre-commit uninstall -t pre-push
```
После установки, при каждом пуше будут отрабатывать хуки из [конфигурационного файла](./src/.pre-commit-config.yaml), предназначенные для пушей (`stages: [push]`)

### Git хуки
При разработке рекомендуется использовать [pre-commit](https://pre-commit.com/), чтобы перед формированием МР код был уже подготовленным и поверхностно проверенным (например, через `flake8`)<br><br>
**Для использования должны быть установлены dev-зависимости**

#### Pre-commit хуки
Установка
```bash
poetry run pre-commit install
```
Удаление
```bash
poetry run pre-commit uninstall
```
После установки, при каждом коммите будут отрабатывать хуки из [конфигурационного файла](./src/.pre-commit-config.yaml), предназначенные для коммитов (`stages: [commit]`)

#### Pre-push хуки
Установка
```bash
poetry run pre-commit install --hook-type pre-push
```
Удаление
```bash
poetry run pre-commit uninstall -t pre-push
```
После установки, при каждом пуше будут отрабатывать хуки из [конфигурационного файла](./src/.pre-commit-config.yaml), предназначенные для пушей (`stages: [push]`)

### Make
Для удобного запуска контейнеров, их сборки, запуска тестов и т.п. в проекте есть [Makefile](./Makefile)

Для выполнения инструкции, на примере запуска тестов, нужно выполнить команду
```bash
make test
```

### CHANGELOG.md
**Заметки о релизах ведутся начиная с версии `1.0.0`**

По готовности релиза в `release/*` ветке или при хотфиксе в `hotfix/*` ветке, нужно обновить файл [CHANGELOG.md](./CHANGELOG.md).  

Заметки о новом релизе добавляются в начало файла, т.е. до предыдущего релиза.
Шаблон заметки о релизе
```md
## 1.1.0 (2024-01-01)

Security:

  -   

Features:

  - 

Bugfixes:

  - 

```

При необходимости, можно вести заметки о будущем релизе прямо в ветке `develop`. В таком случае, вместо даты релиза нужно писать `unreleased`, который потом следует заменить на фактическую дату релиза
```md
## 1.2.0 (unreleased)

Security:

  -   

Features:

  - 

Bugfixes:

  - 

```
