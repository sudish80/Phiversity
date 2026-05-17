/* ── Phiversity Core Layer ── App state, events, utilities ── */
const Phiversity = (() => {
  const STATE_KEY = 'phivity_state';
  const listeners = {};

  // ── State ──
  let state = {
    user: null,
    jobs: [],
    activeJobId: null,
    settings: {
      theme: 'dark',
      playbackSpeed: 1.0,
      autoPlay: true,
    },
    overlays: {},
  };

  try {
    const saved = localStorage.getItem(STATE_KEY);
    if (saved) Object.assign(state, JSON.parse(saved));
  } catch (_) {}

  function _save() {
    try { localStorage.setItem(STATE_KEY, JSON.stringify(state)); } catch (_) {}
  }

  function getState(key) { return key ? state[key] : state; }

  function setState(key, val) {
    state[key] = val;
    _save();
    _emit('state:' + key, val);
    return val;
  }

  function patchState(obj) {
    Object.assign(state, obj);
    _save();
    Object.keys(obj).forEach(k => _emit('state:' + k, obj[k]));
  }

  // ── Events ──
  function on(evt, fn) {
    (listeners[evt] = listeners[evt] || []).push(fn);
    return () => { listeners[evt] = listeners[evt].filter(f => f !== fn); };
  }

  function _emit(evt, data) {
    (listeners[evt] || []).forEach(fn => { try { fn(data); } catch (_) {} });
    window.dispatchEvent(new CustomEvent('phiversity:' + evt, { detail: data }));
  }

  // ── DOM shortcuts ──
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }
  function el(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    if (attrs) Object.entries(attrs).forEach(([k, v]) => {
      if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else if (k === 'style' && typeof v === 'object') Object.assign(e.style, v);
      else e.setAttribute(k, v);
    });
    kids.forEach(k => { if (k != null) e.append(k); });
    return e;
  }

  // ── Layer management ──
  const layers = [];

  function registerLayer(id, cfg) {
    const existing = layers.find(l => l.id === id);
    if (existing) Object.assign(existing, cfg);
    else layers.push({ id, ...cfg });
  }

  function openLayer(id) {
    const layer = layers.find(l => l.id === id);
    if (!layer) return;
    state.overlays[id] = true;
    _emit('layer:open', id);
    if (layer.onOpen) layer.onOpen();
    _save();
  }

  function closeLayer(id) {
    const layer = layers.find(l => l.id === id);
    state.overlays[id] = false;
    _emit('layer:close', id);
    if (layer && layer.onClose) layer.onClose();
    _save();
  }

  function closeAllLayers() {
    Object.keys(state.overlays).forEach(k => { state.overlays[k] = false; });
    _emit('layer:closeAll');
    _save();
  }

  function isLayerOpen(id) { return !!state.overlays[id]; }

  // ── Utilities ──
  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function debounce(fn, ms) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
  }

  // ── Theme ──
  function _applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
  }

  function toggleTheme() {
    const current = getState('settings').theme || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    patchState({ settings: { ...getState('settings'), theme: next } });
    _applyTheme(next);
  }

  // ── Init ──
  function init() {
    // Apply saved theme
    const savedTheme = getState('settings').theme || 'dark';
    _applyTheme(savedTheme);

    document.addEventListener('keydown', (e) => {
      const tag = e.target;
      const isInput = tag.closest('input,textarea,select');
      if (e.key === 'Escape') { closeAllLayers(); return; }

      if (e.key === '?' && !isInput) {
        e.preventDefault();
        isLayerOpen('shortcuts') ? closeLayer('shortcuts') : openLayer('shortcuts');
        return;
      }

      const key = e.key.toLowerCase();
      if (!e.ctrlKey && !e.metaKey && !isInput) {
        if (key === 't') { e.preventDefault(); toggleTheme(); return; }
        if (key === 's') { e.preventDefault(); isLayerOpen('settings') ? closeLayer('settings') : openLayer('settings'); return; }
        if (key === 'h') { e.preventDefault(); isLayerOpen('history') ? closeLayer('history') : openLayer('history'); return; }
      }
    });
  }

  return {
    getState, setState, patchState,
    on, _emit,
    $, $$, el,
    escapeHtml, debounce,
    registerLayer, openLayer, closeLayer, closeAllLayers, isLayerOpen,
    init, toggleTheme,
  };
})();

document.addEventListener('DOMContentLoaded', () => Phiversity.init());
