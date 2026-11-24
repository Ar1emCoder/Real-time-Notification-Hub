# Real-time Notification Hub

**Real-time Notification Hub** — масштабируемый backend-сервис для приёма, обработки и доставки событий через различные каналы связи.

Проект фокусируется на инженерных задачах доставки: асинхронной обработке, соблюдении пользовательских ограничений (тихие часы), защите от спама и гарантиях доставки при сбоях внешних API.

## Статус

### ✅ Реализовано
- Приём событий через `POST /events` (FastAPI + Pydantic валидация)
- Доставка через Telegram-бот
- Хранение настроек пользователей в PostgreSQL (SQLAlchemy 2.0 async + Alembic)
- Тихие часы: откладка уведомлений до разрешённого времени
- Celery Beat: планировщик периодических задач
- Retry-логика с экспоненциальной задержкой (1 → 5 → 30 минут) и лимитом попыток

### 🚧 В работе (In progress)
- Rate limiting на Redis (не чаще 1 уведомления в 5 минут на пользователя):
  - Ограничение ставится при доставке пользователю (не чаще 1 раза в 5 минут). При превышении лимита событие не отбрасывается, а его send_at сдвигается, статус остается pending
- Ключ идемпотентности для защиты от дублирования
- Условная отмена уведомлений
- WebSocket для браузерных push-уведомлений

## Технологический стек

- **API & Core**: Python, FastAPI, Pydantic
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.0 (async), Alembic
- **Async Tasks & Caching**: Celery, Redis
- **Real-time**: FastAPI WebSockets
- **Infrastructure**: Docker, Docker Compose

## Запуск

```bash
docker-compose up -d
alembic upgrade head
uvicorn main:app --reload