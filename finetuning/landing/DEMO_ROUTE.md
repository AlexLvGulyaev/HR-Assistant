# Маршрут проверки демо — HRA LoRA (storytelling-лендинг)

Как быстро пройти историю эксперимента: лендинг — не интерактивное
демо, а последовательность кадров, где главный герой — сама модель.

## Маршрут проверки

1. **Открыть** [лендинг](https://hra-lora.alex-n8n.site) → **прочитать**
   первую сцену → **увидеть** постановку: главный герой — языковая модель
   Qwen2.5-1.5B-Instruct, которая учится принимать HR-решения.
2. **Пролистать** меню сцен слева до раздела словаря → **увидеть** язык
   эксперимента: LoRA, Teacher Dataset, Decision Accuracy, Hard Negatives —
   история объясняет каждую метрику, а не постулирует.
3. **Остановиться** на сцене-ловушке (Experiment 002, runtime smoke) →
   **увидеть**, что offline-метрики не покрывают production-риски —
   история показывает неудачу, а не только успех.
4. **Дойти** до внешней валидации → **сравнить** с эталоном на
   независимой выборке: LoRA 93.1% против GPT-4o-mini 94.1%.

## Что ещё доступно

- Первоисточники истории — четыре GitHub-отчёта по экспериментам:
  - [Experiment 001 — Technical Baseline](https://github.com/AlexLvGulyaev/HR-Assistant/blob/main/finetuning/Experiment_001_Report.md)
  - [Experiment 002 — Parameter Optimisation and Runtime Negative Failure](https://github.com/AlexLvGulyaev/HR-Assistant/blob/main/finetuning/Experiment_002_Report.md)
  - [Experiment 003 — Understanding Model Failures Through Hard Negatives](https://github.com/AlexLvGulyaev/HR-Assistant/blob/main/finetuning/Experiment_003_Report.md)
  - [Experiment 004 — Balanced Teacher Dataset for Production-Ready LoRA](https://github.com/AlexLvGulyaev/HR-Assistant/blob/main/finetuning/Experiment_004_Report.md)
- Как лендинг развёрнут:
  [DEPLOYMENT_GUIDE.md](https://github.com/AlexLvGulyaev/HR-Assistant/blob/main/finetuning/landing/DEPLOYMENT_GUIDE.md).
