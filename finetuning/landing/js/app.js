/** HR Assistant LoRA Landing v3 — interactions */
(function () {
  'use strict';

  const d = document;
  const dossier = d.getElementById('dossier');
  const toggle = d.querySelector('.dossier-toggle');
  const sceneThumbs = dossier.querySelectorAll('.scene-thumb');
  const scenes = d.querySelectorAll('.scene');

  // Toggle navigation on mobile / small screens
  toggle.addEventListener('click', () => {
    dossier.classList.toggle('expanded');
    dossier.classList.toggle('collapsed');
    const width = dossier.classList.contains('collapsed') ? '64px' : '260px';
    d.documentElement.style.setProperty('--sidebar-width', width);
  });

  // Scene navigation
  sceneThumbs.forEach(btn => {
    btn.addEventListener('click', () => {
      const num = btn.dataset.scene;
      const target = d.getElementById('scene-' + num);
      if (target) target.scrollIntoView({ behavior: 'smooth' });
      if (window.innerWidth < 640) {
        dossier.classList.remove('expanded');
        dossier.classList.add('collapsed');
      }
    });
  });

  // Keyboard navigation
  let currentScene = 1;
  const totalScenes = 23;

  function goToScene(n) {
    if (n < 1) n = 1;
    if (n > totalScenes) n = totalScenes;
    const target = d.getElementById('scene-' + n);
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  }

  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === 'PageDown') {
      e.preventDefault();
      goToScene(currentScene + 1);
    } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      goToScene(currentScene - 1);
    } else if (e.key === 'Home') {
      e.preventDefault();
      goToScene(1);
    } else if (e.key === 'End') {
      e.preventDefault();
      goToScene(totalScenes);
    }
  });

  // IntersectionObserver for active scene + animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        const id = entry.target.id;
        const num = parseInt(id.replace('scene-', ''), 10);
        currentScene = num;
        sceneThumbs.forEach(t => t.classList.toggle('active', parseInt(t.dataset.scene, 10) === num));
        updateLumina(entry.target.dataset.lumina, id);
      }
    });
  }, { threshold: 0.5, rootMargin: '-10% 0px -10% 0px' });

  scenes.forEach(scene => observer.observe(scene));

  // Initial animation for first scene
  setTimeout(() => {
    const first = d.getElementById('scene-1');
    if (first) {
      first.classList.add('in-view');
      updateLumina(first.dataset.lumina, 'scene-1');
    }
  }, 100);

  // Lumina SVG generator — recognizable AI character
  const luminaStates = {
    base:       { color: '#4ECDC4', phase: 'dormant', halo: 0, glow: 0.10, expression: 'curious' },
    form:       { color: '#4ECDC4', phase: 'forming', halo: 1, glow: 0.18, expression: 'focused' },
    direction:  { color: '#4ECDC4', phase: 'awakening', halo: 2, glow: 0.24, expression: 'hopeful' },
    shell:      { color: '#FF6B6B', phase: 'guarded', halo: 3, glow: 0.22, expression: 'stern' },
    contracted: { color: '#FFB347', phase: 'hesitant', halo: 2, glow: 0.20, expression: 'worried' },
    balance:    { color: '#2DD4BF', phase: 'stable', halo: 3, glow: 0.26, expression: 'calm' },
    learning:   { color: '#2DD4BF', phase: 'learning', halo: 3, glow: 0.24, expression: 'focused' },
    production: { color: '#4ECDC4', phase: 'ready', halo: 4, glow: 0.30, expression: 'confident' },
    next:       { color: '#4ECDC4', phase: 'growing', halo: 4, glow: 0.28, expression: 'curious' }
  };

  function createLumina(stateKey) {
    const state = luminaStates[stateKey] || luminaStates.base;
    const c = state.color;
    const cx = 100, cy = 120;
    const faceR = 54;
    const haloR = 82 + state.halo * 6;

    // Expression geometry
    const expressions = {
      curious:   { eyeY: -8, mouth: 'slight', brow: 0 },
      focused:   { eyeY: -6, mouth: 'line', brow: -2 },
      hopeful:   { eyeY: -8, mouth: 'soft', brow: 1 },
      stern:     { eyeY: -4, mouth: 'flat', brow: -3 },
      worried:   { eyeY: -8, mouth: 'down', brow: 2 },
      calm:      { eyeY: -8, mouth: 'soft', brow: 0 },
      confident: { eyeY: -6, mouth: 'slight', brow: -1 }
    };
    const expr = expressions[state.expression] || expressions.curious;

    // Outer halo ring with nodes
    const nodeCount = 6 + state.halo;
    let haloNodes = '';
    for (let i = 0; i < nodeCount; i++) {
      const a = (i / nodeCount) * Math.PI * 2;
      const nr = haloR;
      const nx = cx + Math.cos(a) * nr;
      const ny = cy + Math.sin(a) * nr;
      haloNodes += `<circle cx="${nx}" cy="${ny}" r="3" fill="${c}" opacity="0.55" />`;
      haloNodes += `<line x1="${cx}" y1="${cy}" x2="${nx}" y2="${ny}" stroke="${c}" stroke-width="0.7" opacity="0.25" />`;
    }

    // Inner data-lattice rings
    let rings = '';
    const ringCount = 3 + (state.halo > 1 ? 1 : 0);
    for (let i = 0; i < ringCount; i++) {
      const rr = faceR + 8 + i * 8;
      const opacity = 0.45 - i * 0.08;
      rings += `<circle class="halo" cx="${cx}" cy="${cy}" r="${rr}" fill="none" stroke="${c}" stroke-width="${1.2 + i * 0.3}" opacity="${opacity}" />`;
    }

    // Side / top antennae (more in production / next)
    let antennae = '';
    const antCount = state.halo >= 4 ? 5 : state.halo >= 2 ? 3 : state.halo >= 1 ? 2 : 0;
    for (let i = 0; i < antCount; i++) {
      const a = -Math.PI / 2 + (i - (antCount - 1) / 2) * 0.35;
      const x1 = cx + Math.cos(a) * faceR;
      const y1 = cy + Math.sin(a) * faceR;
      const x2 = cx + Math.cos(a) * (faceR + 28 + i * 4);
      const y2 = cy + Math.sin(a) * (faceR + 28 + i * 4);
      antennae += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}" stroke-width="2" opacity="0.7" stroke-linecap="round" />`;
      antennae += `<circle cx="${x2}" cy="${y2}" r="4" fill="${c}" opacity="0.9" />`;
    }

    // Face
    const eyeY = cy + expr.eyeY;
    const eyeRX = 15, eyeRY = 10 + Math.abs(expr.brow) * 0.8;
    const eyeXo = 24;

    let mouthPath = '';
    const my = cy + 14;
    if (expr.mouth === 'slight') mouthPath = `<path d="M${cx - 10} ${my} Q${cx} ${my + 6} ${cx + 10} ${my}" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" opacity="0.85" />`;
    else if (expr.mouth === 'soft') mouthPath = `<path d="M${cx - 12} ${my + 2} Q${cx} ${my + 8} ${cx + 12} ${my + 2}" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" opacity="0.85" />`;
    else if (expr.mouth === 'line') mouthPath = `<line x1="${cx - 10}" y1="${my}" x2="${cx + 10}" y2="${my}" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" opacity="0.85" />`;
    else if (expr.mouth === 'flat') mouthPath = `<line x1="${cx - 10}" y1="${my + 2}" x2="${cx + 10}" y2="${my}" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" opacity="0.85" />`;
    else if (expr.mouth === 'down') mouthPath = `<path d="M${cx - 10} ${my + 4} Q${cx} ${my - 2} ${cx + 10} ${my + 4}" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" opacity="0.85" />`;

    // Brows / eyelids
    let brows = '';
    if (expr.brow !== 0) {
      const browY = eyeY - 12 + expr.brow;
      brows += `<path d="M${cx - eyeXo - 10} ${browY} Q${cx - eyeXo} ${browY - 4} ${cx - eyeXo + 10} ${browY}" fill="none" stroke="${c}" stroke-width="1.5" opacity="0.6" />`;
      brows += `<path d="M${cx + eyeXo - 10} ${browY} Q${cx + eyeXo} ${browY - 4} ${cx + eyeXo + 10} ${browY}" fill="none" stroke="${c}" stroke-width="1.5" opacity="0.6" />`;
    }

    return `
      <svg class="lumina-svg" viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id="glow-${stateKey}" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="${c}" stop-opacity="${state.glow}"/>
            <stop offset="60%" stop-color="${c}" stop-opacity="${state.glow * 0.4}"/>
            <stop offset="100%" stop-color="${c}" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <circle cx="${cx}" cy="${cy}" r="${haloR + 25}" fill="url(#glow-${stateKey})" />
        ${haloNodes}
        <circle cx="${cx}" cy="${cy}" r="${haloR}" fill="none" stroke="${c}" stroke-width="1" opacity="0.35" />
        ${rings}
        ${antennae}
        <circle cx="${cx}" cy="${cy}" r="${faceR}" fill="rgba(10,10,12,0.55)" stroke="${c}" stroke-width="2" opacity="0.95" />
        ${brows}
        <ellipse class="eye" cx="${cx - eyeXo}" cy="${eyeY}" rx="${eyeRX}" ry="${eyeRY}" fill="#ffffff" opacity="0.9" />
        <ellipse class="eye" cx="${cx + eyeXo}" cy="${eyeY}" rx="${eyeRX}" ry="${eyeRY}" fill="#ffffff" opacity="0.9" />
        <circle cx="${cx - eyeXo}" cy="${eyeY}" r="5" fill="${c}" opacity="0.8" />
        <circle cx="${cx + eyeXo}" cy="${eyeY}" r="5" fill="${c}" opacity="0.8" />
        ${mouthPath}
        <circle cx="${cx}" cy="${cy + 38}" r="4" fill="${c}" opacity="0.5" />
      </svg>
    `;
  }

  function updateLumina(stateKey, sceneId) {
    const target = d.getElementById('lumina-' + sceneId.replace('scene-', ''));
    if (!target || !stateKey) return;
    target.innerHTML = createLumina(stateKey);
  }

  // Fill numeric values from experimentData
  function formatValue(val, source) {
    if (typeof val === 'number') {
      if (source.includes('accuracy') || source.includes('fpr') || source.includes('fnr') || source.includes('valid_json_rate')) {
        return (val * 100).toFixed(1).replace(/\.0$/, '') + '%';
      }
      if (source.includes('mae_score') || source.includes('best_eval_loss') || source.includes('loss')) {
        return val.toFixed(source.includes('best_eval_loss') ? 3 : 1).replace(/\.0$/, '');
      }
      if (source.includes('latency') && val > 1000) {
        return (val / 1000).toFixed(1);
      }
      return val.toString();
    }
    return val;
  }

  function getPath(obj, path) {
    return path.split('.').reduce((acc, key) => {
      if (acc == null) return null;
      if (/^\d+$/.test(key) && Array.isArray(acc)) return acc[parseInt(key, 10)];
      return acc[key];
    }, obj);
  }

  function getData() {
    return window.experimentData || (typeof experimentData !== 'undefined' ? experimentData : null);
  }

  function bindData() {
    const data = getData();
    if (!data) return;
    d.querySelectorAll('[data-source]').forEach(el => {
      const source = el.dataset.source;
      const val = getPath(data, source);
      if (val != null) {
        const formatted = formatValue(val, source);
        if (!el.dataset.raw) el.textContent = formatted;
      }
    });
  }

  bindData();
  setTimeout(bindData, 300);

})();
