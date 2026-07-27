# Deployment Guide — HR Assistant LoRA Landing v3

**Target URL:** `https://hra-lora.alex-n8n.site`

This document is the Source of Truth for deploying the static storytelling landing page for the [HR Assistant LoRA fine-tuning module](../README.md).

---

## What is being deployed

A self-contained static landing page located in `finetuning/landing/`:

- `index.html` — single-page film with 20 scenes based on [`docs/hra_lora_narrative_blueprint_v2.md`](docs/hra_lora_narrative_blueprint_v2.md), including a "Dramatis Personae" glossary scene
- `css/main.css` — styles, animations, responsive layout
- `js/app.js` — scene navigation, keyboard shortcuts, scroll animations, Lumina SVG generator, data binding
- `data/experimentData.js` — extracted experiment metrics and source inventory (auto-generated)
- `assets/visuals/*.svg` — generated engineering graphs and diagrams
- `archive/v1/` — first landing version (preserved, not served by default)
- `archive/v2/` — second landing version (preserved, not served by default)
- `docs/` — internal design and research artifacts (excluded from the Docker image via `.dockerignore`)

No build step, no server-side runtime, no API calls at page load.

---

## Prerequisites

- A web server capable of serving static files (nginx, Caddy, Apache, Python `http.server`, Cloudflare Pages, GitHub Pages, etc.)
- The domain `hra-lora.alex-n8n.site` pointing to the server
- HTTPS certificate for production

---

## Local preview

```bash
cd finetuning/landing
python3 -m http.server 8765
```

Open `http://localhost:8765/index.html`.

Quick validation:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/css/main.css
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/js/app.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/data/experimentData.js
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8765/assets/visuals/D-001-pipeline-schematic.svg
```

All should return `200`.

---

## Production deployment with Docker + Traefik (current)

This is the deployment method used for `https://hra-lora.alex-n8n.site`.

### Files

- `cases/hr-assistant/docker-compose.yml` — orchestration
- `finetuning/landing/Dockerfile` — nginx image
- `finetuning/landing/nginx.conf` — nginx configuration
- `finetuning/landing/.dockerignore` — excludes `docs/` and local artifacts from the image
- `/opt/n8n/dynamic.yml` — Traefik router/service definition

### Deploy

```bash
cd /opt/ai-automation-portfolio-lab/cases/hr-assistant
docker compose up -d --build
```

Then reload Traefik to pick up the router (if using file provider):

```bash
cd /opt/n8n
docker compose restart traefik
```

### Traefik dynamic configuration

Add to `/opt/n8n/dynamic.yml`:

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

The `hra-lora` container attaches to the existing `n8n_default` network so Traefik can reach it.

---

## Alternative: Production deployment with Caddy

Create a Caddyfile snippet:

```caddyfile
hra-lora.alex-n8n.site {
    root * /var/www/hra-lora
    file_server
    encode gzip
    header Cache-Control "public, max-age=3600"
    header -Server
}
```

Copy the `finetuning/landing/` contents to the web root:

```bash
rsync -av --delete finetuning/landing/ /var/www/hra-lora/
```

Reload Caddy:

```bash
caddy reload
```

---

## Alternative: Production deployment with nginx

```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name hra-lora.alex-n8n.site;

    root /var/www/hra-lora;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(svg|css|js|json|png|jpg|woff2)$ {
        expires 1h;
        add_header Cache-Control "public, max-age=3600";
    }
}
```

---

## Deployment validation

After deploying, verify:

1. `https://hra-lora.alex-n8n.site/` returns 200.
2. All 20 scenes are reachable via left-side dossier navigation.
3. Keyboard navigation works (ArrowUp/ArrowDown, PageUp/PageDown, Home/End).
4. Scatter plot on scene 9 renders points and diagonal.
5. Tables on scenes 10, 14, 17, 18, 19, 20 render without empty cells.
6. Evidence Room boxes on scene 19 show metrics and source inventory.
7. Mobile layout stacks vertically without horizontal overflow.
8. No console errors (check DevTools).

---

## Re-generating assets

If experiment artifacts change, regenerate the data and graphs:

```bash
cd finetuning/landing/data
python3 extract_data.py
python3 generate_graphs.py
```

Then re-deploy the `finetuning/landing/` directory.

---

## Notes

- The page follows a narrative blueprint that maps LoRA experiments to the storytelling structure.
- The visual hero is an inline SVG symbol representing the model; no external illustration dependencies.
- All numbers on the page are traceable to JSON source files listed in `experimentData.js`.
- `experimentData.js` is auto-generated; do not edit manually.
