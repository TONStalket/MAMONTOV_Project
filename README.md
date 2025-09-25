# MAMONTOV_Project

Backend прототип социальной сети на FastAPI.

## Запуск

1. Создайте и активируйте виртуальное окружение.
2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Запустите сервер разработки:

   ```bash
   uvicorn app.main:app --reload
   ```

Приложение использует SQLite (`social.db`) по умолчанию. Для изменения настроек создайте файл `.env` и переопределите переменные окружения (`DATABASE_URL`, `SECRET_KEY`, и т.д.).

## Тесты

```bash
pytest
```
