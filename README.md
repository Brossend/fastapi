# FastAPI Microservices (ToDo + Short URL)

Проект содержит два микросервиса на FastAPI:
- **ToDo Service** - CRUD для задач
- **Short URL Service** - сервис сокращения ссылок с редиректом

Оба сервиса используют **SQLite** и запускаются в Docker с сохранением данных через **именованные volume**.

---

## Запуск через Docker Compose

### Требования
- Docker
- Docker Compose (v2)

### Запуск всех сервисов одной командой

Из корня проекта:

```bash
  docker compose up --build -d
```

После запуска будут доступны:
- ToDo Service: http://localhost:8000/docs
- Short URL Service: http://localhost:8001/docs

### Остановка сервисов

```bash
  docker compose down
```

Данные сохраняются, так как используются именованные Docker volumes.

Чтобы удалить данные (SQLite):

```bash
  docker compose down -v
```

---

### Запуск сервисов через docker run (альтернативный compose)

Нужно предварительно создать volumes:

```bash
  docker volume create todo_data
  docker volume create shorturl_data
```

#### Запуск ToDo Service

```bash
  docker run -d -p 8000:80 -v todo_data:/app/data ilyamcev/todo-service:latest
```

#### Запуск Short URL Service

```bash
  docker run -d -p 8001:80 -v shorturl_data:/app/data ilyamcev/shorturl-service:latest
```

#### Остановка

```bash
  docker stop <container_id>
  docker rm <container_id>
```

---

### Полное удаление контейнеров и данных проекта

```bash
  docker compose down -v --rmi all --remove-orphans
```

---

### ToDo Service
#### Swagger

http://localhost:8000/docs

#### Эндпоинты:

- POST /items — создать задачу
- GET /items — получить список задач
- GET /items/{id} — получить задачу по ID
- PUT /items/{id} — обновить задачу
- DELETE /items/{id} — удалить задачу

---

### Short URL Service
#### Swagger

http://localhost:8001/docs

#### Эндпоинты

- POST /shorten — создать короткую ссылку
- GET /{short_id} — редирект на полный URL
- GET /stats/{short_id} — информация о ссылке

**Проверка редиректа выполняется напрямую через браузер:** http://localhost:8001/{short_id}

---

### Хранение данных

Для каждого сервиса используется отдельная SQLite база данных, подключённая через Docker volumes:
- todo_data
- shorturl_data

Данные сохраняются после перезапуска контейнеров.