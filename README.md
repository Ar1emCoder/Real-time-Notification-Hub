# Real-time Notification Hub

**Real-time Notification Hub** — это масштабируемый backend-сервис для приема, обработки и доставки событий конечным пользователям через различные каналы связи.

Проект фокусируется на инженерных задачах доставки: асинхронной обработке, соблюдении пользовательских ограничений (тихие часы), защите от спама и гарантиях доставки при сбоях внешних API.

## MVP

1. **POST /events** принимает событие (кому, текст, канал, приоритет).
2. **Настройки пользователя** (каналы, «тихие часы») хранятся в PostgreSQL через SQLAlchemy со схемой под Alembic.
3. **Доставка**: Telegram-бот и WebSocket в браузер.
4. **Тихие часы**: уведомление откладывается через Celery до утра; при сбое доставки — повтор с экспоненциальной задержкой.
5. **Rate limit на Redis**: не чаще одного уведомления в 5 минут одному пользователю. Pub/Sub добавляем, когда появится второй воркер.

## Технологический стек

- **API & Core**: Python, FastAPI, Pydantic
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.0 (async), Alembic
- **Async Tasks & Caching**: Celery, Redis
- **Real-time**: FastAPI WebSockets
- **Infrastructure**: Docker, Docker Compose

## Out of scope (v2)

- Гео-триггеры и контекстные уведомления
- Разбор естественного языка (NLP) для создания правил
- Нативные мобильные пуши (APNs / FCM)
- Redis Pub/Sub для синхронизации между несколькими воркерами Celery

## Запуск

```bash
docker-compose up -d
alembic upgrade head
uvicorn main:app --reload
```
## Roadmap

- [ ] Реализация базовой доставки через Telegram
- [ ] Настройка Celery для отложенных задач
- [ ] Интеграция WebSocket для браузерных уведомлений
- [ ] Rate limiting через Redis