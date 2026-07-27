# Руководство по развёртыванию — HR Assistant LoRA Landing v3

**Целевой URL:** `https://hra-lora.alex-n8n.site`

Единый источник истины (Source of Truth) для развёртывания статического storytelling-лендинга модуля [HR Assistant LoRA](../README.md).

---

## Что развёртывается

Самодостаточный статический сайт в каталоге `finetuning/landing/`:

- `index.html` — 21 интерфейсная сцена (23 DOM-секции) с боковой навигацией;
- `css/main.css` — стили, анимации, адаптивная вёрстка;
- `js/app.js` — навигация, клавиатурное управление, генератор персонажа Люмины, привязка данных;
- `data/experimentData.js` — извлечённые метрики экспериментов;
- `assets/visuals/*.svg` — SVG-графики и диаграммы;
- `archive/` — резервные копии предыдущих версий (не отдаются по умолчанию).

Нет шага сборки, нет серверной части, нет вызовов внешних API при загрузке страницы.

> **Нумерация сцен.** В интерфейсе landing используется 21 сцена с промежуточными номерами `8a/8b` и `13a/13b`. Эти две группы реализованы отдельными DOM-секциями (`scene-8`/`scene-9` и `scene-14`/`scene-15`), поэтому в `index.html` всего 23 DOM-секции.

---

## Предварительные требования

- Docker и Docker Compose на хосте.
- Внешняя сеть `n8n_default`, к которой подключён Traefik.
- Домен `hra-lora.alex-n8n.site`, направленный на сервер с Traefik.
- Настроенный в Traefik TLS-резолвер (например, `myresolver`).

---

## Локальный предпросмотр

```bash
cd finetuning/landing
python3 -m http.server 8765
```

Откройте `http://localhost:8765/index.html`.

Быстрая проверка:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/css/main.css
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/js/app.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/data/experimentData.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/assets/visuals/G-001-loss-curves.svg
```

Все запросы должны вернуть `200`.

---

## Production-развёртывание: Docker + Traefik

Используемый способ для `https://hra-lora.alex-n8n.site`.

### Файлы

- `finetuning/landing/docker-compose.yml` — оркестрация контейнера;
- `finetuning/landing/Dockerfile` — образ nginx;
- `finetuning/landing/nginx.conf` — конфигурация nginx;
- `finetuning/landing/.dockerignore` — исключение локальных артефактов из образа;
- `/opt/n8n/dynamic.yml` — динамическая конфигурация Traefik.

### Шаг 1. Собрать и запустить контейнер

```bash
cd /opt/ai-automation-portfolio-lab/cases/hr-assistant/finetuning/landing
docker compose up -d --build
```

Контейнер `hra-lora` подключается к существующей сети `n8n_default`, чтобы Traefik мог маршрутизировать на него запросы.

### Шаг 2. Перезагрузить Traefik

Если используется file-провайдер, Traefik должен подхватить новый router:

```bash
cd /opt/n8n
docker compose restart traefik
```

### Конфигурация Traefik

Фрагмент `/opt/n8n/dynamic.yml`:

```yaml
http:
  routers:
    hra-lora:
      rule: "Host(`hra-lora.alex-n8n.site`)"
      entryPoints:
        - websecure
      tls:
        certResolver: myresolver
      service: hra-lora
      priority: 1

  services:
    hra-lora:
      loadBalancer:
        servers:
          - url: "http://hra-lora:80"
```

---

## Конфигурация nginx

Контейнер использует `finetuning/landing/nginx.conf`:

- корень сайта — `/usr/share/nginx/html`;
- `index.html` отдаётся без кеширования;
- статика (`css`, `js`, `svg`, шрифты) кешируется на 1 год;
- gzip включён для текстовых типов;
- добавлены базовые security-заголовки;
- скрытые файлы (начинающиеся с `.`) недоступны.

---

## Проверка после развёртывания

1. `https://hra-lora.alex-n8n.site/` возвращает `200`.
2. Все 21 сцена доступны через боковое досье.
3. Работает клавиатурная навигация (стрелки, PageUp/PageDown, Home/End).
4. На сцене 10 (внешняя проверка) отображается scatter-график с диагональю.
5. Таблицы и карточки на сценах 15–21 отображаются без пустых ячеек.
6. Мобильная вёрстка не даёт горизонтального скролла.
7. В консоли браузера нет ошибок.

---

## Перегенерация активов

Если экспериментальные артефакты изменились:

```bash
cd finetuning/landing/data
python3 extract_data.py
python3 generate_graphs.py
```

Затем пересоберите и перезапустите контейнер:

```bash
cd /opt/ai-automation-portfolio-lab/cases/hr-assistant/finetuning/landing
docker compose up -d --build
```

---

## Примечания

- `data/experimentData.js` генерируется автоматически; редактировать его вручную не рекомендуется.
- Для развёртывания в другом окружении достаточно любого веб-сервера, отдающего статику из `finetuning/landing/`.
- Файлы в `archive/` не отдаются посетителям и предназначены только для резервного копирования.

---

**Статус:** актуально для landing v3.  
**Последнее обновление:** 2026-07-27
