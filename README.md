# ElkollegeScheduleBot

#### Telegram-бот для просмотра актуального расписания ЭК

---

## Оглавление

- [Контакты](#контакты)
    - [Связь с разработчиком](#связь-с-разработчиком)
    - [Прочие ссылки](#прочие-ссылки)
- [Сборка и запуск](#сборка-и-запуск)
    - [Необходимые компоненты](#необходимые-компоненты)
    - [.env](#env)
    - [config.ini](#configini)
        - [Раздел `Settings`](#раздел-settings)
    - [Docker](#docker)

---

## Контакты

#### Связь с разработчиком

- [Telegram для связи](https://t.me/diquoks)
- [Почта для связи](mailto:diquoks@yandex.ru)

#### Прочие ссылки

- [Telegram-канал с новостями](https://t.me/diquoks_channel)

---

## Сборка и запуск

### Необходимые компоненты

- [Docker Desktop](https://docs.docker.com/desktop)
- [Git](https://git-scm.com/downloads)
- [Python 3.14](https://www.python.org/downloads)

### .env

| Переменная           | Описание              |
|:---------------------|:----------------------|
| `TELEGRAM_BOT_TOKEN` | Токен бота в Telegram |


### config.ini

#### Раздел `Settings`

| Настройка            |  Тип   | Описание                                       |
|:---------------------|:------:|:-----------------------------------------------|
| `admins_list`        | `list` | Список ID аккаунтов администраторов в Telegram |
| `file_logging`       | `bool` | Использовать логирование в файлы `.log`        |
| `skip_updates`       | `bool` | Пропускать ожидающие события при запуске бота  |
| `workbook_extension` | `str`  | Расширение файлов с расписанием и заменами     |

### Docker

##### Перейдите в корневую директорию

##### Создайте образ

```shell
docker build -t elkollege_schedule_bot .
```

##### Запустите контейнер

```shell
docker run -d --env-file .env --name ElkollegeScheduleBot elkollege_schedule_bot
```
