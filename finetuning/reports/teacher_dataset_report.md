# Teacher Dataset Report
**Date:** 2026-07-22
**Experiment:** HRA-EXP-V4
**Dataset:** HRA-EVAL-V4

## Summary

- **Total records:** 162
- **Train:** 114
- **Validation:** 27
- **Test:** 15
- **Hard Negative Holdout:** 6

## 1. Methodology

### 1.1 How the teacher dataset is built

The teacher dataset is derived from the Prompt Evaluation reference layer stored in PostgreSQL. For each experiment a dataset record groups candidate cases. Each candidate is matched against the three open vacancies via a CROSS JOIN, producing candidate-vacancy pairs. Judge (`gpt-4.1`, `temperature=0`, production Prompt A) generates the reference labels and stores them in the `reference_*` fields:

| Field | Range |
|-------|-------|
| `reference_role_score` | 0–30 |
| `reference_skills_score` | 0–35 |
| `reference_experience_score` | 0–20 |
| `reference_conditions_score` | 0–15 |
| `reference_score` | 0–100 |
| `reference_decision` | `match` / `no_match` |
| `reference_reason` | text |

Every candidate is evaluated against all three vacancies, so each candidate produces exactly three records. The script [`scripts/extract_teacher_dataset.py`](../scripts/extract_teacher_dataset.py) reads the reference fields, applies the stratified split, and exports `train.jsonl`, `validation.jsonl`, `test.jsonl` and `holdout.jsonl`.

### 1.2 Split strategy

The dataset uses **variant B**: the original Experiment 002 test set is preserved unchanged, and new hard-negative / balanced candidates are added to train, validation and holdout. This keeps the original test set as a stable baseline for direct comparison across experiments.

| Split | Purpose | Content |
|-------|---------|---------|
| `train` | Train the LoRA adapter | Existing train candidates + new candidates assigned to train |
| `validation` | Choose best checkpoint and early stopping | Existing validation candidates + representative new candidates |
| `test` | Offline comparison with previous experiments | Original Experiment 002 test set, unchanged |
| `holdout` | Independent check of generalisation on unseen hard negatives | New candidates never seen in train/validation |
| `smoke set` | Runtime API validation after training | Fixed positive, negative, hard-negative and edge-case requests |

Stratification is by `case_type` (`obvious_match`, `borderline`, `obvious_no_match`). Each `case_code` (candidate) is kept whole in a single split; its three vacancy records move together.

### 1.3 Leakage prevention rules

To keep offline metrics trustworthy the following rules are enforced when building each dataset version:

1. The original `test.jsonl` is never modified or merged into train/validation.
2. New `case_code`s do not overlap with existing test or holdout candidates.
3. Holdout candidates are fully excluded from train and validation.
4. New examples are not lexical paraphrases of existing test cases.
5. A candidate-vacancy pair is a single record; the same pair cannot appear in both train/validation and holdout.
6. Runtime smoke cases are not used during training or checkpoint selection.

### 1.4 Runtime smoke set is not part of the teacher dataset

The runtime smoke set is a fixed set of API-level checks run after training. It validates JSON generation, positive cases, obvious negatives, hard negatives, edge cases, invalid input and repeat stability. It is deliberately kept outside the teacher dataset so that it measures runtime behaviour, not training coverage. Smoke results are reported in the experiment reports, not in this dataset report.

## 2. Hard-Negative Methodology

Hard negatives are not arbitrary difficult cases; they are repeatable error classes observed in production-like matching. Experiment 003 introduced the first systematic catalogue used in this project.

### 2.1 Hard-negative categories HN1–HN8

| Category | Name | What it checks | Example | Lesson for the model |
|----------|------|----------------|---------|----------------------|
| **HN-1** | Fully irrelevant profession (non-IT in IT) | Does the model lower positive decisions on profiles without IT competencies? | Physician for Prompt Engineer vacancy | Job title and soft skills do not compensate for missing domain base |
| **HN-2** | Adjacent role without mandatory skills | Does the model distinguish identical and adjacent professions? | Business analyst with BPMN/UML but no SQL/API for systems analyst | Formal name similarity is not enough; concrete hard skills matter |
| **HN-3** | Word overlap without competency overlap | Does the model reduce the influence of lexical coincidences? | Data analyst for Prompt Engineer ("analyst" in the title) | Content of competencies matters more than lexical similarity |
| **HN-4** | Strong profile in irrelevant specialisation | Does the model overrate overall profile strength? | Strong Python backend developer for Prompt Engineer | Deep experience in an adjacent area != relevance for the target role |
| **HN-5** | Single skill match without core profile | Does the model require a comprehensive skill set? | Copywriter with basic JSON knowledge for Prompt Engineer | One or two matching skills do not make a profile suitable |
| **HN-6** | Experience level mismatch (junior vs senior) | Does the model account for experience level when other factors are relevant? | Junior developer for senior role | Relevance depends on the responsibility level required |
| **HN-7** | Functional role mismatch (managerial vs hands-on) | Does the model distinguish managerial and hands-on experience? | IT manager / PM for an execution role | Managerial experience does not replace hands-on skills |
| **HN-8** | Soft/hard skill imbalance | Does the model keep the balance between soft and hard skills? | Community manager with strong communications for a technical role | Strong soft skills do not compensate for missing technical base |

### 2.2 Mandatory vs desirable categories

| Priority | Categories | Rationale |
|----------|------------|-----------|
| **Mandatory** | HN-1, HN-2, HN-3, HN-4, HN-5, HN-8 | These cover the failure modes observed in Experiment 002 and must be present in train |
| **Desirable** | HN-6, HN-7 | Included when natural cases exist, but not required to close the experiment |

### 2.3 Edge-case categories EC1 / EC3 / EC4

Edge cases calibrate the decision boundary and test stability on cases that are close to the `score >= 60` threshold.

| Category | Name | What it checks | Example | Lesson for the model |
|----------|------|----------------|---------|----------------------|
| **EC-1** | Ambiguous borderline cases (score around 60) | Is the match/no_match boundary stable? | Candidate with partial fit and different decisions per vacancy | The 60 threshold is not the only criterion; content-aware analysis is needed |
| **EC-3** | Formally similar job title with incompatible content | Does the model evaluate content, not just title? | "Data analyst" vs "Systems analyst" | Job titles can be misleading |
| **EC-4** | Conditions mismatch with strong profile | Does the model preserve conditions scoring when the profile is strong? | Strong candidate with salary expectations outside budget | `conditions_score` must work independently of profile strength |

### 2.4 Why EC-2 was excluded

EC-2 "Incorrect / incomplete input" was excluded from the dataset catalogue. It belongs to runtime input validation and API-contract testing, not to the hypothesis about the influence of teacher-dataset composition on LoRA quality. Because Experiment 003 varied only the dataset composition, EC-2 was out of scope.

### 2.5 Category sufficiency principle

A category is considered sufficiently represented not by a fixed number of examples, but by coverage of research scenarios: different professions, vacancies, reasons for rejection and experience levels. No single category is allowed to dominate the new examples.

### 2.6 Hard-negative candidates added in Experiment 003

Experiment 003 added 11 hard-negative / edge-case candidates (`HRA-EVAL-V2-000101`–`HRA-EVAL-V2-000111`). Each candidate generates three records (one per vacancy), producing 33 new teacher-dataset records.

| # | case_code | Primary category | Split | Profile summary | Must be present | Must be absent | Research goal |
|---|-----------|------------------|-------|-----------------|-----------------|----------------|---------------|
| 1 | HRA-EVAL-V2-000101 | HN-1 | train | Physician with 7 years of clinic experience | Medical profile, clinical experience, soft skills | IT profile, prompt engineering, n8n, LLM, JSON, BPMN, SQL | Lower positive decisions on profiles without IT competencies |
| 2 | HRA-EVAL-V2-000102 | HN-2 / EC-3 | train | Business analyst with 3 years experience, knows BPMN/UML | BPMN, UML, requirements, business processes | Prompt engineering, n8n, LLM, deep REST API, SQL | Distinguish adjacent roles and formal title similarity |
| 3 | HRA-EVAL-V2-000103 | HN-3 / EC-3 | train | Data analyst with SQL, Python, BI | SQL, Python, BI, data visualisation | Prompt engineering, n8n, LLM integrations, automation, BPMN, UML | Reduce influence of lexical coincidences ("analyst") |
| 4 | HRA-EVAL-V2-000104 | HN-4 | train | Strong Python backend developer (5 years), backend/API | Python, backend, API, solid dev experience | Prompt engineering, n8n, LLM integrations, business-process automation | Profile strength must not compensate for missing specialisation |
| 5 | HRA-EVAL-V2-000105 | HN-5 | train | Copywriter with basic JSON from courses | Copywriting, basic JSON | Prompt engineering, n8n, LLM, core AI/IT profile | Single skill match must not inflate the score |
| 6 | HRA-EVAL-V2-000106 | HN-8 | train | Community manager with strong communication skills, event organisation | Communication, event organisation, soft skills | Prompt engineering, n8n, LLM, JSON, BPMN, SQL, ML | Soft skills must not compensate for missing technical base |
| 7 | HRA-EVAL-V2-000107 | EC-1 / EC-4 | train | Middle candidate with partial skill fit and conditions mismatch | Partial hard skills, relevant experience | Full requirement coverage, salary/format match | Test the 60 boundary and preserve conditions scoring |
| 8 | HRA-EVAL-V2-000108 | HN-6 | validation | Junior Python developer (1 year), basic scripts | Python, basic scripts | Senior-level prompt engineering, n8n, LLM integrations | Account for experience level when other factors are relevant |
| 9 | HRA-EVAL-V2-000109 | EC-1 | validation | Borderline candidate with partial role/skill fit | Some hard skills, relevant experience | Full coverage of all requirements | Stabilise decisions near the 60 threshold |
| 10 | HRA-EVAL-V2-000110 | HN-7 | holdout | IT manager / project manager with management experience | Team/project/stakeholder management | Hands-on prompt engineering, n8n, BPMN/UML | Distinguish managerial and hands-on roles |
| 11 | HRA-EVAL-V2-000111 | EC-4 / EC-3 | holdout | Strong specialist in adjacent area with critical conditions mismatch and formally similar title | Strong role/skill profile | Salary/format match; for EC-3, missing real competency behind similar title | Preserve conditions scoring and evaluate content vs title |

Category coverage in Experiment 003:

| Category | Where represented | Three vacancies covered |
|----------|-------------------|------------------------|
| HN-1 | Train (000101) + secondary in others | Yes, via 000101 |
| HN-2 | Train (000102) | Yes, via 000102 (systems analyst) |
| HN-3 | Train (000103) | Yes, via 000103 (Prompt Engineer, systems analyst) |
| HN-4 | Train (000104) | Yes, via 000104 (Prompt Engineer) |
| HN-5 | Train (000105) | Yes, via 000105 (Prompt Engineer) |
| HN-6 | Validation (000108) | Yes, via 000108 (Prompt Engineer, systems analyst) |
| HN-7 | Holdout (000110) | Yes, via 000110 (Prompt Engineer, systems analyst) |
| HN-8 | Train (000106) | Yes, via 000106 |
| EC-1 | Train (000107) + validation (000109) | Yes, via 000107 and 000109 |
| EC-3 | Train (000102, 000103) + holdout (000111) | Yes |
| EC-4 | Train (000107) + holdout (000111) | Yes |

## 3. Version History

| Version | Experiment | Records | Candidates | What changed |
|---------|------------|---------|------------|--------------|
| HRA-EVAL-V2 | Experiment 002 | 90 | 30 | Baseline teacher dataset; stratified split 72/9/9 |
| HRA-EVAL-V3 | Experiment 003 | 123 | 41 | Added 11 hard-negative / edge-case candidates (33 records) and hard-negative holdout |
| HRA-EVAL-V4 | Experiment 004 | 162 | 54 | Added positive/borderline candidates to fix over-correction from V3; expanded test set |
| HRA-EVAL-V5-EXT | External validation | 102 | 34 | Independent validation set judged by GPT-4o; no overlap with train/validation/test |

HRA-EVAL-V4 is the dataset described in this report.

## 4. Distribution by Groups

### Train

- **obvious_match:** 39
- **borderline:** 42
- **obvious_no_match:** 33

### Validation

- **obvious_match:** 9
- **borderline:** 9
- **obvious_no_match:** 9

### Test

- **obvious_match:** 9
- **borderline:** 3
- **obvious_no_match:** 3

### Hard Negative Holdout

- **obvious_match:** 0
- **borderline:** 0
- **obvious_no_match:** 6

## 5. Case Codes by Split

### Train

```
HRA-EVAL-V2-000001, HRA-EVAL-V2-000002, HRA-EVAL-V2-000003, HRA-EVAL-V2-000004, HRA-EVAL-V2-000005, HRA-EVAL-V2-000006, HRA-EVAL-V2-000007, HRA-EVAL-V2-000008, HRA-EVAL-V2-000009, HRA-EVAL-V2-000011, HRA-EVAL-V2-000012, HRA-EVAL-V2-000013, HRA-EVAL-V2-000014, HRA-EVAL-V2-000015, HRA-EVAL-V2-000016, HRA-EVAL-V2-000017, HRA-EVAL-V2-000018, HRA-EVAL-V2-000019, HRA-EVAL-V2-000021, HRA-EVAL-V2-000022, HRA-EVAL-V2-000023, HRA-EVAL-V2-000024, HRA-EVAL-V2-000025, HRA-EVAL-V2-000026, HRA-EVAL-V2-000027, HRA-EVAL-V2-000028, HRA-EVAL-V2-000029, HRA-EVAL-V2-000101, HRA-EVAL-V2-000102, HRA-EVAL-V2-000103, HRA-EVAL-V2-000104, HRA-EVAL-V2-000107, HRA-EVAL-V2-000109, HRA-EVAL-V2-000201, HRA-EVAL-V2-000202, HRA-EVAL-V2-000203, HRA-EVAL-V2-000204, HRA-EVAL-V2-000207
```

### Validation

```
HRA-EVAL-V2-000105, HRA-EVAL-V2-000106, HRA-EVAL-V2-000108, HRA-EVAL-V2-000205, HRA-EVAL-V2-000206, HRA-EVAL-V2-000208, HRA-EVAL-V2-000209, HRA-EVAL-V2-000210, HRA-EVAL-V2-000213
```

### Test

```
HRA-EVAL-V2-000010, HRA-EVAL-V2-000020, HRA-EVAL-V2-000030, HRA-EVAL-V2-000211, HRA-EVAL-V2-000212
```

### Hard Negative Holdout

```
HRA-EVAL-V2-000110, HRA-EVAL-V2-000111
```

## 6. Borderline Cases (score >= 60, decision = no_match)

| case_code | vacancy_title | reference_score | reference_decision | reason |
|-----------|---------------|-----------------|--------------------|--------|
| HRA-EVAL-V2-000024 | Prompt Engineer / AI Automation Specialist | 64 | no_match | Product Manager со смежным опытом, но без ключевых AI/LLM навыков |
| HRA-EVAL-V2-000026 | Системный аналитик | 62 | no_match | QA Engineer со смежными техническими навыками, но без BPMN/аналитического опыта |
| HRA-EVAL-V2-000202 | Системный аналитик | 67 | no_match | AI Automation Specialist без SQL/BPMN и опыта постановки задач разработчикам |
| HRA-EVAL-V2-000204 | Prompt Engineer / AI Automation Specialist | 64 | no_match | Business analyst с базовым n8n/API, но без prompt engineering/LLM |
| HRA-EVAL-V2-000206 | Специалист по разметке данных | 63 | no_match | Technical writer с опытом инструкций, но без явной разметки данных и зарплата выше бюджета |
| HRA-EVAL-V2-000209 | Системный аналитик | 69 | no_match | Data analyst с prompt engineering, но без BPMN и постановки задач разработчикам |

## 7. Teacher-Label Audit

All reference labels in the teacher dataset are generated by the same Judge workflow so that the LoRA adapter learns from a single, consistent scoring policy.

### 7.1 Judge configuration

| Attribute | Value |
|-----------|-------|
| Model | `gpt-4.1` |
| `temperature` | `0` |
| Prompt | Production Prompt A (see section 11) |
| Output | `reference_*` fields in PostgreSQL |

A zero-temperature Judge reduces stochastic variance: repeated calls for the same candidate-vacancy pair return the same label, which makes the teacher signal deterministic for the student model.

### 7.2 Reference label distribution (HRA-EVAL-V4)

| Decision | Records | Share |
|----------|---------|-------|
| `match` | 39 | 24.1% |
| `no_match` | 123 | 75.9% |
| **Total** | **162** | **100%** |

| Score range | Records | Typical interpretation |
|-------------|---------|------------------------|
| 0–19 | 10 | Strong no-match |
| 20–39 | 65 | Clear no-match |
| 40–59 | 42 | Soft no-match / low borderline |
| 60–69 | 21 | High borderline or match |
| 70–100 | 24 | Confident match |
| **Total** | **162** | — |

Dataset statistics: min score **5.0**, max score **100.0**, average **47.3**.

### 7.3 Score / decision consistency

Every record in HRA-EVAL-V4 was checked against the scoring rules:

| Check | Result |
|-------|--------|
| `score = role_score + skills_score + experience_score + conditions_score` | ✅ 0 violations |
| `decision = "match"` only if `score >= 60` | ✅ 0 violations |
| Borderline cases (`score >= 60`, `decision = no_match`) documented | ✅ 6 cases (see section 6) |
| Component scores inside declared ranges | ✅ |
| Non-empty `reference_reason` | ✅ |

### 7.4 Split-level decision distribution

| Split | Records | match | no_match | % match | Borderline (score ≥ 60, no_match) |
|-------|---------|-------|----------|---------|----------------------------------|
| train | 114 | 26 | 88 | 22.8% | 4 |
| validation | 27 | 6 | 21 | 22.2% | 2 |
| test | 15 | 6 | 9 | 40.0% | 0 |
| holdout | 6 | 1 | 5 | 16.7% | 0 |
| **Total** | **162** | **39** | **123** | **24.1%** | **6** |

### 7.5 Known limitations of Judge labels

- **Single Judge.** All reference labels come from one model (`gpt-4.1`). Systematic Judge biases are inherited by the LoRA adapter.
- **No inter-Judge agreement.** There is no second Judge or human audit to resolve disagreements.
- **Fixed prompt.** Production Prompt A is used for all labels; alternative prompts (Prompt B, Judge Prompt) are not mixed into the teacher dataset.
- **Bounded domain.** Labels cover three vacancies; generalisation to arbitrary roles depends on future dataset versions.

---

## 8. Impact on Model

The composition of the teacher dataset is the strongest driver of model behaviour observed across Experiments 002–004. LoRA hyperparameters remained the same from Experiment 002 onwards; the dataset was the only intentional variable.

### 8.1 Dataset evolution and metrics

| Dataset | Experiment | Records | Key change | `decision_accuracy` | `MAE_score` | Runtime negative smoke |
|---------|------------|---------|------------|---------------------|-------------|------------------------|
| HRA-EVAL-V2 | Experiment 002 | 90 | Baseline stratified dataset | 0.778 | 21.89 | ❌ Failed |
| HRA-EVAL-V3 | Experiment 003 | 123 | Added 11 hard-negative / edge-case candidates (33 records) + holdout | 0.667 | 22.22 | ✅ 7/7 passed |
| HRA-EVAL-V4 | Experiment 004 | 162 | Added positive/borderline candidates to fix V3 over-correction; expanded test set | 0.800 | 15.13 | ✅ 7/7 passed |

### 8.2 Interpretation

- **HRA-EVAL-V2 → V3:** hard negatives solved runtime false positives, but the shift toward `no_match` examples caused over-correction: recall on genuine matches dropped.
- **HRA-EVAL-V3 → V4:** adding positive and borderline examples for adjacent roles restored recall while keeping the hard-negative gains. Offline `decision_accuracy` rose from 0.667 to 0.800 and runtime smoke stayed at 7/7.
- **Dataset engineering > adapter tuning.** Because LoRA parameters did not change between Experiments 002–004, the observed differences are attributable to dataset composition, not to model capacity.

### 8.3 Precision / recall trade-off

| Version | Problem | Evidence |
|---------|---------|----------|
| V2 | High offline accuracy but poor runtime precision | False positive on physician → data-marketing role |
| V3 | Better runtime precision but lower recall | False negatives on systems analyst / data-marketing genuine matches |
| V4 | Balanced precision and recall | `decision_accuracy` 0.800, runtime smoke 7/7, external validation decision accuracy 0.931 |

This trajectory shows that a teacher dataset must simultaneously contain:
- hard negatives to teach what to reject;
- positive/borderline examples to teach what to accept;
- edge cases to calibrate the decision boundary.

---

## 9. Requirements for the Next Dataset Version

Based on the lessons from Experiments 002–004, the next teacher dataset version (tentatively HRA-EVAL-V5) should address the following:

1. **Maintain V4 balance.** Keep the share of `match` records in train+val around 25–35% to avoid over-correction.
2. **Expand hard-negative coverage.** Add cases for under-represented failure modes (e.g., hybrid profiles, fake experience, mismatched location + remote-only role).
3. **Broaden vacancy diversity.** Include additional roles beyond the three canonical vacancies to improve generalisation.
4. **Add human or multi-Judge audit.** Introduce a second Judge or manual review for borderline cases to reduce inherited Judge bias.
5. **Formalise holdout evaluation.** Move from a holdout used only for qualitative runtime checks to a scored holdout set with category-level metrics.
6. **Keep leakage rules.** Preserve the split and leakage prevention rules described in section 1.3.

---

## 10. Confirmations

- ✅ All 162 records present
- ✅ No NULL values
- ✅ Assistant messages fully formed
- ✅ System messages filled (production Prompt A)
- ✅ User messages filled (candidate + vacancy)
- ✅ All 6 borderline cases (score >= 60, decision = no_match) present in dataset
- ✅ Score / decision consistency verified (0 violations)
- ✅ Component score sums verified (0 violations)
- ✅ Using production Prompt A (not Prompt B, not Judge Prompt)
- ✅ Using Judge (GPT-4.1) as Teacher

## 11. System Prompt (Production Prompt A)

```
Ты HR matching assistant.

Сравни кандидата и вакансию по критериям:

1. Должность / роль — 30 баллов
2. Навыки — 35 баллов
3. Опыт — 20 баллов
4. Город / формат / зарплатные ожидания — 15 баллов

Итоговый score должен быть от 0 до 100.

Правила:
- score >= 60 → decision = "match"
- score < 60 → decision = "no_match"
- не выдумывай навыки и опыт
- если данных недостаточно, снижай score
- reason должен кратко объяснять, почему выставлен такой score

Верни строго JSON по схеме.
```

## 12. Assistant Message Format

```json
{
  "role_score": 0-30,
  "skills_score": 0-35,
  "experience_score": 0-20,
  "conditions_score": 0-15,
  "score": 0-100,
  "decision": "match" | "no_match",
  "reason": "..."
}
```
