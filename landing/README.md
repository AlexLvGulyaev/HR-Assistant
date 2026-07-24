# HR Assistant LoRA — Storytelling Landing v3

**Public URL:** `https://hra-lora.alex-n8n.site`

Production-ready static landing page that tells the engineering story behind the HR Assistant LoRA fine-tuning experiments as a 12-scene documentary film.

The hero of the story is the language model itself. The film follows Qwen2.5-1.5B-Instruct with a small LoRA adapter as it learns to make HR matching decisions — from base-model failures through dataset-engineering experiments, production smoke, and latency optimization.

---

## What this is

- 20 full-viewport cinematic scenes based on `docs/hra_lora_narrative_blueprint_v2.md`, including a "Dramatis Personae" glossary scene
- Left-side scene dossier with click and keyboard navigation
- Inline SVG model hero (Lumina) and generated engineering graphs/diagrams
- Scroll-triggered animations
- All numbers traceable to JSON source files in `finetuning/runs/`
- Fully responsive layout

---

## Quick start

```bash
cd landing
python3 -m http.server 8765
# open http://localhost:8765/index.html
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment instructions.

---

## Structure

| File / Directory | Purpose |
|------------------|---------|
| `index.html` | Single-page film with all 20 scenes |
| `css/main.css` | Styles, animations, responsive rules |
| `js/app.js` | Navigation, observer, Lumina generator, data binding |
| `data/experimentData.js` | Extracted experiment metrics (auto-generated) |
| `data/experimentData.json` | Same metrics in JSON (auto-generated) |
| `data/extract_data.py` | Script to extract metrics from `finetuning/runs/` |
| `data/generate_graphs.py` | Script to generate SVG graphs and diagrams |
| `assets/visuals/` | All SVG graphs and diagrams |
| `archive/v1/` | First landing version (preserved) |
| `archive/v2/` | Second landing version (preserved) |

---

## Re-generating assets

If experiment artifacts in `finetuning/runs/` change:

```bash
cd landing/data
python3 extract_data.py
python3 generate_graphs.py
```

---

## Design source of truth

- `docs/hra_lora_narrative_blueprint_v2.md` — narrative blueprint (21-page specification, 20 implemented scenes).
- `docs/visual_assets_registry.md` — visual assets registry v2 (57 elements: G/T/D/C).
- `docs/IMPLEMENTATION_PLAN.md` — project plan for landing rework (phases 1–8).
