# Отчёт о внешнем валидационном датасете

**Эксперимент:** HRA-EXP-V5-EXT
**Датасет:** HRA-EVAL-V5-EXT
**Всего записей:** 102

## Распределение по case_type

- **obvious_match:** 45
- **borderline:** 33
- **obvious_no_match:** 24

## Коды кандидатов

```
HRA-EVAL-V2-000301, HRA-EVAL-V2-000302, HRA-EVAL-V2-000303, HRA-EVAL-V2-000304, HRA-EVAL-V2-000305, HRA-EVAL-V2-000306, HRA-EVAL-V2-000307, HRA-EVAL-V2-000308, HRA-EVAL-V2-000309, HRA-EVAL-V2-000310, HRA-EVAL-V2-000311, HRA-EVAL-V2-000312, HRA-EVAL-V2-000313, HRA-EVAL-V2-000314, HRA-EVAL-V2-000315, HRA-EVAL-V2-000316, HRA-EVAL-V2-000317, HRA-EVAL-V2-000318, HRA-EVAL-V2-000319, HRA-EVAL-V2-000320, HRA-EVAL-V2-000321, HRA-EVAL-V2-000322, HRA-EVAL-V2-000323, HRA-EVAL-V2-000324, HRA-EVAL-V2-000325, HRA-EVAL-V2-000326, HRA-EVAL-V2-000327, HRA-EVAL-V2-000328, HRA-EVAL-V2-000329, HRA-EVAL-V2-000330, HRA-EVAL-V2-000331, HRA-EVAL-V2-000332, HRA-EVAL-V2-000333, HRA-EVAL-V2-000334
```

## Проверки

- ✅ Все 102 записи присутствуют.
- ✅ Нет NULL в system/user сообщениях.
- ✅ Reference-аннотации заполнены после завершения Judge-прогона.

## Предсказания моделей на этом датасете

Summary-метрики и representative примеры prediction/reference для LoRA Experiment 004 vs GPT-4o-mini на HRA-EVAL-V5-EXT опубликованы в:

- [`../data/evidence/experiment_004_external_validation_examples.jsonl`](../data/evidence/experiment_004_external_validation_examples.jsonl) — канонический runtime FastAPI + Transformers + PEFT;
- [`../data/evidence/experiment_004_external_validation_vllm_examples.jsonl`](../data/evidence/experiment_004_external_validation_vllm_examples.jsonl) — vLLM OpenAI-compatible runtime, 3 повторных прогона.

### Representative example: ошибка LoRA на внешней выборке

**Candidate:** Специалист с опытом автоматизации бизнес-процессов, REST API, бизнес-процессы; без SQL и BPMN.

**Vacancy:** Системный аналитик; требуется SQL, BPMN, REST API, аналитика, постановка задач разработчикам.

**Reference (GPT-4o):** `match`, score 63.

**Model prediction (LoRA Experiment 004):** `no_match`, score 57, с обоснованием, что кандидат — AI Automation Specialist, а не системный аналитик, и не хватает ключевых hard skills.

**Почему этот пример важен:** Показывает, что LoRA остаётся более консервативной, чем GPT-4o-mini, на смежных ролях: она отклоняет кандидата, которого GPT-4o и GPT-4o-mini считают подходящим. Это один из источников FNR 13.6 % vs 4.5 % у GPT-4o-mini.

**Evidence:** [`../data/evidence/experiment_004_external_validation_examples.jsonl`](../data/evidence/experiment_004_external_validation_examples.jsonl), запись `HRA-EVAL-V2-000305`, vacancy "Системный аналитик".
