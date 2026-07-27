# HR Assistant LoRA — Storytelling Landing v3

**Public URL:** `https://hra-lora.alex-n8n.site`

Production-ready static landing page that tells the engineering story behind the HR Assistant LoRA fine-tuning experiments as a 20-scene documentary film.

The hero of the story is the language model itself. The film follows Qwen2.5-1.5B-Instruct with a small LoRA adapter as it learns to make HR matching decisions — from base-model failures through dataset-engineering experiments, production smoke, and latency optimization.

This landing is part of the [HR Assistant fine-tuning module](../README.md) and serves as its visual presentation layer.

---

## What this is

- 20 full-viewport cinematic scenes based on [`docs/hra_lora_narrative_blueprint_v2.md`](docs/hra_lora_narrative_blueprint_v2.md), including a "Dramatis Personae" glossary scene.
- Left-side scene dossier with click and keyboard navigation.
- Inline SVG model hero (Lumina) and generated engineering graphs/diagrams.
- Scroll-triggered animations.
- All numbers traceable to public evidence files in [`../data/evidence/`](../data/evidence/) and auto-generated `data/experimentData.*`.
- Fully responsive layout.

---

## Quick start

```bash
cd finetuning/landing
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
| `data/extract_data.py` | Script to extract metrics from `../runs/` |
| `data/generate_graphs.py` | Script to generate SVG graphs and diagrams |
| `assets/visuals/` | All SVG graphs and diagrams |
| `archive/v1/` | First landing version (preserved) |
| `archive/v2/` | Second landing version (preserved) |
| `docs/` | Internal design and research artifacts (not included in Docker image) |

---

## Re-generating assets

If experiment artifacts in `../runs/` change:

```bash
cd finetuning/landing/data
python3 extract_data.py
python3 generate_graphs.py
```

---

## Navigation

| Document | Purpose |
|----------|---------|
| [../README.md](../README.md) | Fine-tuning module: experiments, metrics, evidence |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Production deployment, Docker, Traefik, Caddy, nginx |
| [NARRATIVE_BLUEPRINT.md](NARRATIVE_BLUEPRINT.md) | Narrative blueprint: 20 scenes, dramaturgy, messaging |
| [VISUAL_ASSETS_REGISTRY.md](VISUAL_ASSETS_REGISTRY.md) | Visual assets registry: 57 G/T/D/C elements |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Landing rework project plan (phases 1–8) |
