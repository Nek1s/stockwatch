# Наблюдаемость

## Метрики

Endpoint `GET /metrics` возвращает Prometheus-метрики без JWT и предназначен
только для внутренней сети или локальной разработки. Метрики содержат:

- `stockwatch_http_requests_total` — число HTTP-запросов по методу, маршруту и статусу;
- `stockwatch_http_request_duration_seconds` — длительность HTTP-запросов;
- `stockwatch_price_checks_total` — результаты задач проверки цены (`success` или `error`);
- `stockwatch_price_check_duration_seconds` — длительность фоновой проверки;
- `stockwatch_price_snapshots_total` — созданные снимки цен.

Маршрут метрики использует шаблон API-маршрута, а не конкретный UUID. Это не
создаёт бесконтрольную кардинальность меток.

## Локальный запуск

```bash
docker compose up --build
```

После старта доступны:

- метрики приложения: `http://localhost:8000/metrics`;
- Prometheus: `http://localhost:9090`;
- Grafana: `http://localhost:3000` (стандартные для контейнера учётные данные:
  `admin` / `admin`).

Dashboard `StockWatch Overview` подхватывается автоматически. Docker Compose
использует общий `PROMETHEUS_MULTIPROC_DIR`: поэтому endpoint API агрегирует
метрики API, worker и Beat. Для сброса локальных метрик остановите окружение с
томами: `docker compose down -v`.

В production не публикуйте `/metrics`, Prometheus и Grafana напрямую в интернет:
ограничьте доступ сетевой политикой, reverse proxy или VPN.
