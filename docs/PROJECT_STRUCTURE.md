# 📂 PROJECT_STRUCTURE — HR Assistant

**Назначение:** карта репозитория — каталоги, файлы, их роль. Дополнение к [`README.md`](../README.md) (там — только верхний уровень).

---

## 🎯 1. Верхний уровень

```
hr-assistant/
├── README.md            # Точка входа: назначение, live demo, карта документации
├── .env.example         # Шаблон переменных окружения
├── .gitignore
├── docs/                # Документация кейса
├── workflows/           # Workflow n8n (экспортированные JSON)
├── database/            # SQL-схемы: боевой контур + eval-контур
├── config/              # Инфраструктура: Docker Compose
├── api/                 # Экспериментальные LLM-бэкенды (LoRA runtime)
└── finetuning/          # Модуль Fine-tuning (LoRA) — экспериментальная подсистема
```

---

## 🧩 2. Каталоги

### 📚 docs/ — документация

| Раздел | Содержимое |
|--------|-----------|
| Корень `docs/` | Документы кейса по слоям читателей (см. карту в [`README.md`](../README.md#-документация)) |
| `docs/prompt_evaluation/` | Подсистема A/B-оценки промптов: [`README.md`](prompt_evaluation/README.md) — индекс подсистемы |
| `docs/screenshots/` | Изображения кейса: [`MEDIA_INDEX.md`](screenshots/MEDIA_INDEX.md) — реестр и визуальный контракт |

Основные документы: [`ARCHITECTURE.md`](ARCHITECTURE.md), [`SPEC.md`](SPEC.md), [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md), [`PROJECT_STATE.md`](PROJECT_STATE.md), [`CHANGE_LOG.md`](CHANGE_LOG.md).

### ⚙️ workflows/ — workflow n8n

Файлы — экспортированные JSON, импортируются в n8n. Имена файлов соответствуют именам workflow в n8n.

| Файл | Назначение |
|------|-----------|
| `HR Intake.json` | Приём сообщений из Telegram, нормализация |
| `HR Processing Worker.json` | Extraction + matching (production) |
| `HR Delivery Worker.json` | Формирование и отправка мультимедийного ответа |
| `HR Generate Video.json` | Генерация визуальной карточки результата |
| `HR Queue Watchdog - candidate_inputs.json` | Watchdog очереди обработки |
| `HR Queue Watchdog - outbox.json` | Watchdog очереди отправки |
| `PEm05_ error_handler.json` | Централизованная обработка ошибок |
| `HR Processing Worker - Multi Provider Test.json` | Инженерный стенд тестирования LLM-провайдеров (не production) |
| `HRA Prompt Evaluation Experiment.json` | Workflow A/B-оценки промптов (eval-контур) |
| `llm-provider-config.js` | Конфигурация провайдеров для Multi Provider Test |

Детальное описание — [`workflows/README.md`](../workflows/README.md).

### 🗄️ database/ — SQL-схемы

| Файл | Назначение |
|------|-----------|
| `schema_hr_assistant.sql` | Основная схема боевого контура (11 таблиц, индексы, функция логирования) |
| `02-prompt-evaluation.sql` | Схема eval-контура (таблицы `eval_prompt_*`) |
| `03…17-*.sql` | Сидирование датасетов, создание экспериментов, валидационные проверки, экспорт teacher dataset |
| `README.md` | Описание всех таблиц, индексов и применения схем |

### 🔧 config/ — инфраструктура

| Файл | Назначение |
|------|-----------|
| `docker-compose.yml` | Traefik v3.3 + PostgreSQL 16 + n8n (production-стек) |

Переменные окружения — [`.env.example`](../.env.example); полный порядок развёртывания — [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md).

### 🔬 api/ — экспериментальные LLM-бэкенды

Скрипты API-серверов для runtime-тестирования LoRA-моделей (экспериментальный контур, не production):

- `hra_qwen_api.py` — базовый Qwen-бэкенд
- `hra_qwen_api_lora.py`, `hra_qwen_api_lora_4bit.py`, `hra_qwen_api_lora_vllm.py` — варианты с LoRA-адаптером
- `requirements.txt` — зависимости

### 🧪 finetuning/ — Fine-tuning (LoRA)

Экспериментальная подсистема обучения LoRA-адаптеров: конфигурации, скрипты, отчёты Experiments 001–004, данные evidence. Точка входа и полная карта — [`finetuning/README.md`](../finetuning/README.md).

---

## 📚 3. Связанные документы

- [`README.md`](../README.md) — точка входа в проект
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — как компоненты устроены и связаны
- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) — как развернуть содержимое репозитория
- [`screenshots/MEDIA_INDEX.md`](screenshots/MEDIA_INDEX.md) — какие изображения где используются

---

**Статус:** Карта репозитория проекта
**Последнее обновление:** 2026-09-16
