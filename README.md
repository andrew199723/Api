# Поиск запчастей по артикулу

Простое приложение на Node.js/TypeScript с REST API и минимальным фронтендом.

## Возможности
- GET `/api/parts?article=...` — поиск запчастей по артикулу
- Провайдеры данных:
  - `mock` (по умолчанию) — локальные тестовые данные
  - `http` — прокси к внешнему API (настраивается переменными окружения)

## Быстрый старт
```bash
npm install
npm run dev
# откройте http://localhost:3000
```

## Переменные окружения
Создайте файл `.env` при необходимости:
```
PORT=3000
PROVIDER=mock           # mock | http
API_BASE_URL=https://example.com/api
API_KEY=your_api_key
```

## Скрипты
- `npm run dev` — запуск в dev-режиме (nodemon + ts-node)
- `npm run build` — сборка в `dist`
- `npm start` — запуск собранного кода

## Структура
- `src/server.ts` — настройка сервера, статика
- `src/transport/http/parts.router.ts` — HTTP-роут `/api/parts`
- `src/usecases/getPartsByArticle.ts` — бизнес-логика
- `src/vendors/` — провайдеры данных (mock/http)
- `src/public/index.html` — минимальный UI

## Пример запроса
```bash
curl 'http://localhost:3000/api/parts?article=123-ABC'
```

## Под внешнее API
Отредактируйте маппинг в `src/vendors/http/HttpPartsProvider.ts` под фактический формат ответа внешнего сервиса.