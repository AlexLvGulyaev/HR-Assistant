# HR Assistant LoRA — Storytelling Landing v3

**Публичный URL:** `https://hra-lora.alex-n8n.site`

Статичный storytelling-лендинг, который рассказывает инженерную историю обучения небольшой языковой модели для HR-задачи. Главный герой — сама модель: от базового Qwen2.5-1.5B-Instruct, который умеет лишь красиво оформлять ответ, до LoRA-адаптера, способного принимать HR-решения и работать в production.

Лендинг входит в состав [модуля дообучения HR Assistant](../README.md) и служит его визуальным слоем.

---

## Что это такое

- 21 интерфейсная сцена, переключаемых через боковое досье.
- Левое меню-оглавление с кликами и клавиатурной навигацией (стрелки, PageUp/PageDown, Home/End).
- Главный персонаж — inline SVG «Люмина», которая меняет состояние от сцены к сцене.
- Инженерные графики и диаграммы в формате SVG, сгенерированные из JSON-артефактов экспериментов.
- Все числа привязаны к `data/experimentData.js` и исходным файлам в `../data/` и `../runs/`.
- Адаптивная вёрстка: на мобильных устройствах меню сворачивается, контент выстраивается в одну колонку.

> **Почему 21 сцена, а в HTML 23 DOM-секции.** Интерфейс landing использует пользовательскую нумерацию из 21 сцены. В HTML ей соответствуют 23 DOM-секции, потому что две главы (`8a/8b` и `13a/13b`) реализованы отдельными DOM-секциями (`scene-8`/`scene-9` и `scene-14`/`scene-15`).

---

## Быстрый старт

```bash
cd finetuning/landing
python3 -m http.server 8765
```

Откройте `http://localhost:8765/index.html`.

Подробности по production-развёртыванию — в [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

---

## Структура каталога

| Файл / каталог | Назначение |
|----------------|------------|
| `index.html` | Одностраничный фильм, 21 интерфейсная сцена |
| `css/main.css` | Стили, анимации, адаптивные правила |
| `js/app.js` | Навигация, IntersectionObserver, генератор Люмины, привязка данных |
| `data/experimentData.js` | Извлечённые метрики экспериментов (auto-generated) |
| `data/experimentData.json` | Те же данные в JSON (auto-generated) |
| `data/extract_data.py` | Скрипт извлечения метрик из `../runs/` |
| `data/generate_graphs.py` | Скрипт генерации SVG-графиков |
| `assets/visuals/*.svg` | SVG-графики и диаграммы, используемые на сценах |
| `archive/` | Снимки предыдущих версий landing (не отдаются nginx по умолчанию) |
| `Dockerfile` | Образ nginx для production |
| `nginx.conf` | Конфигурация nginx внутри контейнера |
| `.dockerignore` | Исключение локальных артефактов из образа |

---

## Перегенерация данных и графиков

Если исходные артефакты в `../runs/` изменились:

```bash
cd finetuning/landing/data
python3 extract_data.py
python3 generate_graphs.py
```

После этого пересоберите образ:

```bash
cd /opt/ai-automation-portfolio-lab/cases/hr-assistant
docker compose up -d --build
```

---

## Публичная документация

| Документ | Назначение |
|----------|------------|
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Развёртывание: Docker, nginx, docker-compose, Traefik |
| [NARRATIVE_BLUEPRINT.md](NARRATIVE_BLUEPRINT.md) | Повествовательная спецификация: сцены, драматургия, ключевые артефакты |
| [VISUAL_ASSETS_REGISTRY.md](VISUAL_ASSETS_REGISTRY.md) | Реестр SVG-графиков landing и иллюстраций Blueprint |
| [LANDING_ARCHITECTURE.md](LANDING_ARCHITECTURE.md) | Архитектура реализации: подсистемы, поток данных, принципы сопровождения |
---

## Статус

Landing v3 реализован и развёрнут по адресу `https://hra-lora.alex-n8n.site`.

**Критерии готовности:**
- [x] 21 интерфейсная сцена реализована в `index.html` (23 DOM-секции, см. раздел «Что это такое»).
- [x] Все SVG-артефакты привязаны к сценам и документированы в [`VISUAL_ASSETS_REGISTRY.md`](VISUAL_ASSETS_REGISTRY.md).
- [x] Развёртывание проверено по [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md).
- [x] Все числа на landing прослеживаются к [`data/experimentData.js`](data/experimentData.js) и исходным JSON-файлам проекта.
- [x] Публичная документация не содержит ссылок на внутренние материалы проекта.

**Последнее обновление:** 2026-07-27
