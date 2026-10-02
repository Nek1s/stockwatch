# Project State — StockWatch

**Обновлено:** 2026-10-02  
**Этап:** 0 — инициализация

## Сделано

- Выбрана идея: StockWatch — сервис мониторинга товаров и цен.
- Создан локальный Git-репозиторий с веткой `main`.
- Созданы стартовые документы: README, roadmap, changelog и backlog issues.
- Создан каркас FastAPI с `GET /health` и OpenAPI.
- Добавлены конфигурация окружения, заготовки Celery и Alembic.
- Добавлены Docker Compose, `.env.example`, MIT-лицензия, pytest, Ruff, mypy и GitHub Actions.
- Локально пройдены форматирование, линтер, типизация и тесты.
- Создан GitHub Issue #1 для инициализации приложения.
- Созданы GitHub Issues #3–#11 для оставшихся этапов MVP и портфолио-готовности.
- PR #2 для этапа инициализации открыт; GitHub Actions CI завершился успешно.

## В работе

- Ревью и merge PR #2 `feature/project-bootstrap` → `main` (закроет Issues #1, #3 и #4).

## Дальше

1. Выполнить merge PR #2 после ревью.
2. Создать ветку `feature/user-authentication` от обновлённой `main`.
3. Реализовать Issue #5: пользователи и JWT-аутентификация.

## Блокеры

- Нет.
