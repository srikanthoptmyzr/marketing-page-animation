/*!
 * Scene player for the marketing-page-animation skill.
 *
 * Plays a declarative timeline over final-state markup. No dependencies, no inline
 * scripts, no strings of its own (labels come from the markup). Animates opacity and
 * transform only (plus SVG stroke offset for `draw`). Deterministic: every step is a
 * pure function of timeline progress, so seek() and replay() always agree.
 *
 * Markup contract (see references/animation-system.md section 9 and runtime/README.md):
 *   <figure class="product-ui" data-scene="id" data-final-state="approved"
 *           data-scene-config='{"states":[...],"timeline":[...]}'   (or data-scene-src="url.json")
 *           data-trigger="view|load|click" data-loop="3" data-speed="1">
 *     ... elements carry data-target="component-id"; authored in the FINAL state,
 *         with data-hidden on anything not visible in that state ...
 *     <button data-action="play|pause|toggle|replay|next|prev">label from the template</button>
 *   </figure>
 */
(function (global) {
  'use strict';
  // Tells the stylesheet that scripts run, so stages can stay hidden until each scene has set its first frame.
  try { global.document.documentElement.classList.add('pu-js'); } catch (e) {}

  var DUR = { instant: 80, fast: 150, base: 250, slow: 400, deliberate: 700 };
  var START_DELAY = 250;
  // How long a finished scene rests on its final state before looping again.
  var LOOP_GAP = 5000;
  // A scene scaled below this is too wide for its slot. 0.8 keeps 15px design text at 12px.
  var MIN_FIT_SCALE = 0.8;
  // Viewport at/above which the slot is at its widest, so the fit is worth judging.
  var FIT_JUDGE_FROM = 1280;
  var _fitWarned = {};
  function warnFit(fig, k, dw, w) {
    var id = fig.getAttribute('data-scene') || 'scene';
    if (_fitWarned[id]) return;
    _fitWarned[id] = 1;
    var advise = Math.round(w / 0.85);
    console.warn('[scene-player] "' + id + '" is scaled to ' + k.toFixed(2) +
      ' to fit its slot (design width ' + dw + 'px into ' + Math.round(w) + 'px). ' +
      'Text will render around ' + Math.round(15 * k) + 'px, under the 11px floor. ' +
      'Recompose the scene at about ' + advise + 'px with fewer columns or shorter labels ' +
      'instead of scaling it down.');
  }
  var MAX_CONCURRENT_NOTE = 6;

  // ---------- small utilities ----------
  function bez(x1, y1, x2, y2) {
    function A(a, b) { return 1 - 3 * b + 3 * a; }
    function B(a, b) { return 3 * b - 6 * a; }
    function C(a) { return 3 * a; }
    function calc(t, a, b) { return ((A(a, b) * t + B(a, b)) * t + C(a)) * t; }
    function slope(t, a, b) { return 3 * A(a, b) * t * t + 2 * B(a, b) * t + C(a); }
    return function (x) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      var t = x;
      for (var i = 0; i < 8; i++) {
        var s = slope(t, x1, x2);
        if (Math.abs(s) < 1e-6) break;
        t -= (calc(t, x1, x2) - x) / s;
      }
      t = Math.min(1, Math.max(0, t));
      return calc(t, y1, y2);
    };
  }
  var EASE = {
    out: bez(0.2, 0, 0, 1),
    'in': bez(0.4, 0, 1, 1),
    'in-out': bez(0.4, 0, 0.2, 1),
    linear: function (x) { return Math.min(1, Math.max(0, x)); }
  };
  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function hash(str) {
    var h = 1779033703 ^ String(str).length;
    for (var i = 0; i < str.length; i++) {
      h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    return h >>> 0;
  }
  function rng(seed) {
    var a = hash(seed);
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function arr(x) { return x == null ? [] : Array.isArray(x) ? x : [x]; }
  function warn(scene, msg) {
    if (scene && scene._warned[msg]) return;
    if (scene) scene._warned[msg] = true;
    if (global.console && console.warn) console.warn('[scene' + (scene ? ':' + scene.id : '') + '] ' + msg);
  }
  function lang(el) {
    return (el.closest && el.closest('[lang]') && el.closest('[lang]').getAttribute('lang')) ||
      document.documentElement.lang || undefined;
  }

  // Text segmentation that works for any script.
  var segCache = {};
  function segments(text, unit) {
    var key = unit + '|' + text;
    if (segCache[key]) return segCache[key];
    var out = [];
    if (global.Intl && Intl.Segmenter) {
      var seg = new Intl.Segmenter(undefined, { granularity: unit === 'word' ? 'word' : 'grapheme' });
      var buf = '';
      var iter = seg.segment(text)[Symbol.iterator]();
      var r;
      if (unit === 'word') {
        // a unit ends at each word-like segment; punctuation and spaces attach to the previous unit
        var cur = '';
        while (!(r = iter.next()).done) {
          var s = r.value;
          if (s.isWordLike && cur !== '') { out.push(cur); cur = ''; }
          cur += s.segment;
        }
        if (cur !== '') out.push(cur);
        return (segCache[key] = out);
      }
      while (!(r = iter.next()).done) { buf = r.value.segment; out.push(buf); }
      return (segCache[key] = out);
    }
    out = unit === 'word' ? text.split(/(?<=\s)/) : Array.from(text);
    return (segCache[key] = out);
  }
  // Updates two persistent text nodes instead of rebuilding the element each frame,
  // so typing and streaming cause no DOM churn and no layout thrash.
  function setPartial(el, units, n, caret) {
    var pt = el.__pt;
    if (!pt || pt.caret !== !!caret || el.firstChild !== pt.v) {
      el.textContent = '';
      pt = el.__pt = { caret: !!caret, v: document.createElement('span'), h: document.createElement('span'), c: null };
      pt.v.className = 'pu-t-v'; pt.h.className = 'pu-t-h';
      el.appendChild(pt.v);
      if (caret) { pt.c = document.createElement('span'); pt.c.className = 'pu-caret'; el.appendChild(pt.c); }
      el.appendChild(pt.h);
    }
    pt.v.textContent = units.slice(0, n).join('');
    pt.h.textContent = units.slice(n).join('');
  }

  var reducedQuery = global.matchMedia ? global.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  // ---------- Scene ----------
  function Scene(el) {
    this.el = el;
    this.id = el.getAttribute('data-scene') || 'scene';
    this._warned = {};
    this.cfg = null;
    this.prims = [];
    this.t = 0;
    this.speed = parseFloat(el.getAttribute('data-speed')) || 1;
    this.playing = false;
    this.userPaused = false;
    this.autoPaused = true;
    this.finished = false;
    this.cycle = 0;
    this.loop = null;
    this.ratio = 0;
    this.visible = false;
    this.trigger = el.getAttribute('data-trigger') || 'view';
    this.touched = new Set();
    this.flags = [];
    this.rings = [];
    this.textOrig = new Map();
    this.finalHidden = new Set();
    this.managed = [];
    this.cursorPos = null;
    this.ready = false;
    this._raf = 0;
    this._last = 0;
    this._resetting = false;
  }

  Scene.prototype.load = function (cb) {
    var self = this;
    var inline = this.el.getAttribute('data-scene-config');
    var src = this.el.getAttribute('data-scene-src');
    if (inline) {
      try { this.cfg = JSON.parse(inline); } catch (e) { warn(this, 'invalid data-scene-config JSON'); this.cfg = {}; }
      return cb();
    }
    if (src && global.fetch) {
      fetch(src).then(function (r) { return r.json(); }).then(function (j) { self.cfg = j; cb(); })
        .catch(function () { warn(self, 'could not load ' + src); self.cfg = {}; cb(); });
      return;
    }
    this.cfg = {};
    cb();
  };

  Scene.prototype.find = function (id, quiet) {
    if (!id) return null;
    var el = this.el.querySelector('[data-target="' + String(id).replace(/"/g, '\\"') + '"]');
    if (!el && !quiet) warn(this, 'missing target "' + id + '"');
    return el;
  };
  Scene.prototype.textEl = function (target) {
    var el = typeof target === 'string' ? this.find(target) : target;
    if (!el) return null;
    if (el.hasAttribute('data-text') || el.hasAttribute('data-input')) return el;
    var inner = el.querySelector('[data-text]');
    if (inner) return inner;
    if (!el.children.length) return el;
    warn(this, 'no [data-text] element inside "' + el.getAttribute('data-target') + '"');
    return null;
  };
  Scene.prototype.textOf = function (key) {
    // source text is read from the rendered elements so every language animates correctly
    var el = this.el.querySelector('[data-content="' + key + '"]') || this.find(key, true);
    if (!el) { warn(this, 'no rendered text for source "' + key + '"'); return ''; }
    var t = this.textEl(el);
    if (!t) return '';
    return (this.textOrig.has(t) ? this.textOrig.get(t) : t.textContent).replace(/\s+/g, ' ').trim();
  };
  Scene.prototype.remember = function (el) {
    if (el && !this.textOrig.has(el)) this.textOrig.set(el, el.textContent);
  };

  // ---------- states ----------
  Scene.prototype.buildStates = function () {
    var self = this;
    this.states = {};
    this.stateOrder = [];
    (this.cfg.states || []).forEach(function (s) {
      self.states[s.id] = s;
      self.stateOrder.push(s.id);
    });
    this.finalState = this.el.getAttribute('data-final-state') ||
      (this.cfg.states || []).filter(function (s) { return s.final; }).map(function (s) { return s.id; })[0] ||
      this.stateOrder[this.stateOrder.length - 1] || null;
    this.initialState = this.cfg.initialState || this.stateOrder[0] || null;
    var all = Array.prototype.slice.call(this.el.querySelectorAll('[data-target]'));
    this.managed = all.filter(function (e) { return e.getAttribute('data-target').indexOf('.') < 0; });
    this.setupCam();
  };
  // Camera layer: only created when the timeline zooms. Wraps the stage content so a zoom
  // moves everything (cursor included) in one compositor-only transform.
  Scene.prototype.setupCam = function () {
    var uses = (this.cfg.timeline || []).some(function (s) { return s.do === 'zoom' || s.do === 'zoom-out'; });
    var stage = this.el.querySelector('.pu-stage');
    this.cam = null;
    if (!uses || !stage) return;
    var cam = stage.querySelector(':scope > .pu-cam');
    if (!cam) {
      cam = document.createElement('div');
      cam.className = 'pu-cam';
      while (stage.firstChild) cam.appendChild(stage.firstChild);
      stage.appendChild(cam);
    }
    this.cam = cam;
    this.camState = { tx: 0, ty: 0, k: 1 };
  };
  // An element is visible in a state if it, or any descendant component, is listed.
  Scene.prototype.hiddenSet = function (stateId) {
    var st = this.states[stateId];
    var hidden = new Set();
    if (!st) return hidden;
    var listed = new Set(st.visible || []);
    var byId = {};
    this.managed.forEach(function (e) { byId[e.getAttribute('data-target')] = e; });
    this.managed.forEach(function (e) {
      var id = e.getAttribute('data-target');
      var vis = listed.has(id);
      if (!vis) {
        var kids = e.querySelectorAll('[data-target]');
        for (var i = 0; i < kids.length; i++) if (listed.has(kids[i].getAttribute('data-target'))) { vis = true; break; }
      }
      if (!vis) hidden.add(e);
    });
    return hidden;
  };
  Scene.prototype.setHidden = function (el, on) {
    if (on) el.setAttribute('data-hidden', ''); else el.removeAttribute('data-hidden');
  };

  // ---------- timeline resolution ----------
  function P(k, at, dur, extra) {
    var p = { k: k, at: at, dur: dur || 0, done: false };
    for (var key in extra) p[key] = extra[key];
    p.end = p.at + p.dur;
    return p;
  }

  Scene.prototype.resolve = function () {
    var self = this;
    var steps = (this.cfg.timeline || []).slice();
    var res = {};
    this.prims = [];
    this.loop = null;
    this._cursorRevealed = false;
    var n = 0;
    steps.forEach(function (s) { if (!s.id) s.id = 'step-' + (++n); });
    var pending = steps.slice();
    while (pending.length) {
      var progressed = false;
      for (var i = 0; i < pending.length; i++) {
        var s = pending[i];
        var base;
        if (typeof s.at === 'number') base = s.at;
        else if (s.after && res[s.after]) base = res[s.after].end;
        else if (s.with && res[s.with]) base = res[s.with].start;
        else continue;
        var start = base + (s.delay || 0);
        if (s.do === 'loop') {
          this.loop = { at: start, count: s.count || 3 };
          res[s.id] = { start: start, end: start };
        } else {
          var ps = this.expand(s, start);
          var end = start;
          ps.forEach(function (p) { if (p.end > end) end = p.end; self.prims.push(p); });
          res[s.id] = { start: start, end: end };
        }
        pending.splice(i, 1); i--; progressed = true;
      }
      if (!progressed) { warn(this, 'timeline has unresolved references: ' + pending.map(function (s) { return s.id; }).join(', ')); break; }
    }
    this.prims.sort(function (a, b) { return a.at - b.at; });
    this.total = this.prims.reduce(function (m, p) { return Math.max(m, p.end); }, 0);
    this.dataDur = this.total;
  };

  // helpers building primitives
  Scene.prototype.mkReveal = function (el, eff, at, dur, from) {
    return el ? P('reveal', at, dur == null ? DUR.base : dur, { el: el, eff: eff || 'fade-up', from: from || 'end', ease: 'out' }) : null;
  };
  Scene.prototype.mkHide = function (el, at, dur) {
    return el ? P('hide', at, dur == null ? DUR.fast : dur, { el: el, ease: 'in' }) : null;
  };
  Scene.prototype.mkHl = function (el, at, dur) { return el ? P('highlight', at, dur || DUR.slow, { el: el }) : null; };
  Scene.prototype.mkPress = function (el, at) { return el ? P('press', at, DUR.fast, { el: el }) : null; };
  Scene.prototype.mkFlag = function (el, attr, on, at) { return el ? P('flag', at, 0, { el: el, attr: attr, on: on }) : null; };
  Scene.prototype.mkCount = function (el, at, dur) {
    return el ? P('count', at, dur || DUR.deliberate, { el: el, ease: 'out' }) : null;
  };
  Scene.prototype.mkDraw = function (el, at, dur) {
    return el ? P('draw', at, dur || DUR.deliberate, { el: el, ease: 'out' }) : null;
  };
  Scene.prototype.mkType = function (el, full, at, cps, seed, mirror, caret) {
    if (!el) return null;
    this.remember(el);
    var units = segments(full, 'grapheme');
    var r = rng(seed || 'type');
    var base = 1000 / (cps || 26);
    var cum = [], t = 0;
    for (var i = 0; i < units.length; i++) { t += base * (0.7 + 0.6 * r()); cum.push(t); }
    var dur = Math.min(t, 6000);
    if (t > 0 && dur < t) cum = cum.map(function (c) { return c * dur / t; });
    return P('type', at, dur, { el: el, units: units, cum: cum, mirror: !!mirror, caret: !!caret, ease: 'linear' });
  };
  Scene.prototype.mkStream = function (el, full, at, unit, dur) {
    if (!el) return null;
    this.remember(el);
    var units = segments(full, unit || 'word');
    var d = dur || Math.min(3000, Math.max(300, units.length * 45));
    return P('stream', at, d, { el: el, units: units, ease: 'linear' });
  };
  Scene.prototype.mkMove = function (cursor, to, at, dur) {
    return cursor && to ? P('move', at, dur || DUR.deliberate, { el: cursor, to: to, ease: 'in-out' }) : null;
  };
  Scene.prototype.revealCursor = function (cursor, at) {
    if (!cursor || this._cursorRevealed) return null;
    this._cursorRevealed = true;
    return this.mkReveal(cursor, 'fade', at, DUR.fast);
  };
  // the element itself if it matches, otherwise its matching descendants
  Scene.prototype.within = function (el, sel) {
    if (!el) return [];
    if (el.matches(sel)) return [el];
    return Array.prototype.slice.call(el.querySelectorAll(sel));
  };
  Scene.prototype.partsOf = function (el) {
    // direct component children (nearest data-target ancestor is `el`)
    return Array.prototype.filter.call(el.querySelectorAll('[data-target]'), function (c) {
      var p = c.parentElement && c.parentElement.closest('[data-target]');
      return p === el && c.getAttribute('data-target').indexOf('.') < 0;
    });
  };

  Scene.prototype.expand = function (s, start) {
    var self = this, out = [], add = function (p) { if (p) out.push(p); return p; };
    var el = s.target && typeof s.target === 'string' ? this.find(s.target) : null;
    var t = start;
    switch (s.do) {
      case 'enter-state':
        if (!this.states[s.state]) { warn(this, 'unknown state "' + s.state + '"'); break; }
        add(P('state', start, s.duration == null ? DUR.base : s.duration, { id: s.state, ease: 'out' }));
        break;

      case 'reveal':
        arr(s.target).forEach(function (id, i) {
          add(self.mkReveal(self.find(id), s.effect, start + i * (s.each || (s.stagger ? 60 : 0)), s.duration, s.from));
        });
        break;
      case 'hide':
        arr(s.target).forEach(function (id) { add(self.mkHide(self.find(id), start, s.duration)); });
        break;
      case 'type': {
        var mirror = s.source && s.source !== s.target;
        var tEl = this.textEl(mirror ? (el && (el.querySelector('[data-input]') || el)) : el);
        var full = mirror ? this.textOf(s.source) : (tEl ? tEl.textContent : '');
        if (tEl) add(this.mkType(tEl, full, start, s.cps, s.id, mirror, s.caret !== false));
        break;
      }
      case 'stream': {
        var sEl = this.textEl(el);
        if (sEl) add(this.mkStream(sEl, s.source ? this.textOf(s.source) : sEl.textContent, start, s.unit, s.duration));
        break;
      }
      case 'count':
        this.within(el, '[data-count-to]').forEach(function (c) { add(self.mkCount(c, start, s.duration)); });
        break;
      case 'draw':
        this.within(el, '[data-draw]').forEach(function (d) { add(self.mkDraw(d, start, s.duration)); });
        break;
      case 'highlight':
        add(this.mkHl(el, start, s.duration)); break;
      case 'press':
        add(this.mkPress(el, start)); break;
      case 'wait':
        add(P('wait', start, s.duration || 0, {})); break;
      case 'zoom':
      case 'zoom-out': {
        if (!this.cam) break;
        var zt = s.do === 'zoom' ? this.find(s.to || s.target) : null;
        add(P('zoom', start, s.duration == null ? DUR.deliberate : s.duration, { to: zt, zk: s.scale || 1.6, ease: 'in-out' }));
        break;
      }
      case 'move':
      case 'cursor-moves': {
        var cur = this.find(s.cursor || 'cur');
        var to = this.find(s.to || s.target);
        add(this.revealCursor(cur, start));
        add(this.mkMove(cur, to, start + (this._cursorRevealed ? 0 : 0), s.duration));
        break;
      }
      case 'click':
        add(this.mkFlag(el, 'data-pressed', true, start));
        add(this.mkPress(el, start));
        add(this.mkHl(el, start, DUR.base));
        add(this.mkFlag(el, 'data-pressed', false, start + DUR.fast));
        break;
      case 'hover':
        add(this.mkFlag(el, 'data-hover', true, start));
        add(this.mkReveal(this.find(s.target + '.tip', true), 'fade', start, DUR.fast));
        break;
      case 'select':
        add(this.mkFlag(el, 'data-selected', true, start)); break;

      // ---- product interaction recipes ----
      case 'user-types': {
        if (!el) break;
        var input = el.querySelector('[data-input]') || el;
        var text = this.textOf(s.source);
        if (!text) break;
        add(this.mkHl(el, t, DUR.fast)); t += DUR.fast;
        var ty = add(this.mkType(input, text, t, s.cps || 26, s.id, true, true));
        t += ty ? ty.dur : 0;
        var send = this.find(s.target + '.send', true);
        if (send) { t += 120; add(this.mkPress(send, t)); t += DUR.fast; }
        var msg = this.find(s.source, true);
        if (msg) { add(this.mkReveal(msg, 'fade-up', t, DUR.base)); t += DUR.base; }
        break;
      }
      case 'system-processes': {
        if (!el) break;
        var d = Math.max(600, s.duration || 1000);
        add(this.mkReveal(el, 'fade', t, DUR.fast)); t += DUR.fast;
        add(this.mkFlag(el, 'data-active', true, t));
        t += d;
        add(this.mkFlag(el, 'data-active', false, t));
        add(this.mkHide(el, t, DUR.fast));
        break;
      }
      case 'response-streams': {
        if (!el) break;
        var tx = this.textEl(el);
        add(this.mkReveal(el, 'fade', t, DUR.fast)); t += DUR.fast;
        if (tx) add(this.mkStream(tx, tx.textContent, t, s.unit || 'word', s.duration));
        break;
      }
      case 'data-updates': {
        if (!el) break;
        add(this.mkReveal(el, 'fade', t, DUR.fast));
        var st = t + DUR.fast;
        var counts = Array.prototype.slice.call(el.querySelectorAll('[data-count-to]'));
        if (el.hasAttribute('data-count-to')) counts.unshift(el);
        counts.forEach(function (c) { add(self.mkCount(c, st, s.duration)); });
        Array.prototype.forEach.call(el.querySelectorAll('[data-draw]'), function (d2) { add(self.mkDraw(d2, st, s.duration)); });
        Array.prototype.slice.call(el.querySelectorAll('[data-changed]'), 0, 4).forEach(function (c, i) {
          add(self.mkHl(c, st + DUR.deliberate + i * 60, DUR.slow));
        });
        break;
      }
      case 'notification-arrives':
        if (!el) break;
        add(this.mkReveal(el, 'slide', t, DUR.base, s.from || 'end'));
        if (s.hold) { add(this.mkHide(el, t + DUR.base + s.hold, DUR.fast)); }
        break;
      case 'recommendation-appears': {
        if (!el) break;
        add(this.mkReveal(el, 'fade-up', t, DUR.base)); t += DUR.base;
        this.partsOf(el).slice(0, MAX_CONCURRENT_NOTE).forEach(function (part, i) {
          add(self.mkReveal(part, 'fade-up', t + i * 70, DUR.base));
        });
        var key = el.querySelector('[data-key]');
        if (key) add(this.mkHl(key, t + 6 * 70 + DUR.base, DUR.slow));
        break;
      }
      case 'approval-clicked': {
        if (!el) break;
        var confirm = this.find(s.target + '.confirm', true) || el.querySelector('button');
        var cursor = this.find(s.cursor || 'cur', true);
        if (cursor && confirm) {
          add(this.revealCursor(cursor, t));
          var mv = add(this.mkMove(cursor, confirm, t, DUR.deliberate)); t += mv ? mv.dur : 0;
        }
        add(this.mkFlag(confirm, 'data-hover', true, t)); t += 250;
        add(this.mkFlag(confirm, 'data-pressed', true, t));
        add(this.mkPress(confirm, t)); add(this.mkHl(confirm, t, DUR.base)); t += DUR.fast;
        add(this.mkFlag(confirm, 'data-pressed', false, t));
        add(this.mkFlag(confirm, 'data-hover', false, t));
        Array.prototype.forEach.call(el.querySelectorAll('[data-alt]'), function (a) { add(self.mkFlag(a, 'data-disabled', true, t)); });
        break;
      }
      case 'success-state': {
        if (!el) break;
        add(this.mkReveal(el, 'scale', t, DUR.base)); t += DUR.base;
        Array.prototype.forEach.call(el.querySelectorAll('[data-draw]'), function (d3) { add(self.mkDraw(d3, t, DUR.slow)); });
        var k2 = el.querySelector('[data-key]');
        if (k2) add(this.mkHl(k2, t + DUR.slow, DUR.slow));
        break;
      }
      case 'switch-tab':
      case 'scroll':
        warn(this, 'recipe "' + s.do + '" is not implemented yet; step skipped');
        break;
      default:
        warn(this, 'unknown verb "' + s.do + '"');
    }
    return out;
  };

  // ---------- rendering ----------
  Scene.prototype.touch = function (el) { this.touched.add(el); };
  Scene.prototype.clearInline = function (el) {
    el.style.opacity = ''; el.style.transform = ''; el.style.willChange = '';
    el.style.strokeDasharray = ''; el.style.strokeDashoffset = '';
    if (el.getAttribute('style') === '') el.removeAttribute('style');
  };
  Scene.prototype.rootPoint = function (el, fx, fy) {
    var ref = this.cam || this.el.querySelector('.pu-stage') || this.el;
    var rr = ref.getBoundingClientRect();
    var sc = ref.offsetWidth ? rr.width / ref.offsetWidth : 1;
    var r = el.getBoundingClientRect();
    return { x: (r.left - rr.left + r.width * fx) / sc, y: (r.top - rr.top + r.height * fy) / sc };
  };
  Scene.prototype.fmt = function (el, v) {
    var d = el.dataset, f = d.countFormat || 'number', dec = parseInt(d.countDecimals || '0', 10);
    var opts = { minimumFractionDigits: dec, maximumFractionDigits: dec };
    if (d.countSign === 'always') opts.signDisplay = 'always';
    try {
      if (f === 'percent') { opts.style = 'percent'; v = v / 100; }
      else if (f.indexOf('currency:') === 0) { opts.style = 'currency'; opts.currency = f.split(':')[1]; }
      return new Intl.NumberFormat(lang(el), opts).format(v);
    } catch (e) { return String(Math.round(v)); }
  };

  Scene.prototype.render = function (p, prog) {
    var e = (EASE[p.ease] || EASE.out)(prog), el = p.el, dir;
    switch (p.k) {
      case 'reveal': {
        if (p._skip === undefined) p._skip = !el.hasAttribute('data-hidden');
        if (p._skip) return;
        this.touch(el);
        if (prog > 0) {
          this.setHidden(el, false);
          var anc = el.parentElement && el.parentElement.closest('[data-target]');
          while (anc && this.el.contains(anc)) { this.setHidden(anc, false); anc = anc.parentElement && anc.parentElement.closest('[data-target]'); }
        }
        if (prog >= 1) { this.clearInline(el); return; }
        el.style.opacity = String(e);
        el.style.willChange = 'opacity, transform';
        var inv = 1 - e;
        if (p.eff === 'fade-up') el.style.transform = 'translateY(' + (inv * 10) + 'px)';
        else if (p.eff === 'scale') el.style.transform = 'scale(' + (0.96 + 0.04 * e) + ')';
        else if (p.eff === 'slide') {
          dir = getComputedStyle(this.el).direction === 'rtl' ? -1 : 1;
          var f = p.from;
          var tr = f === 'top' ? 'translateY(' + (-inv * 20) + 'px)' : f === 'bottom' ? 'translateY(' + (inv * 20) + 'px)' :
            f === 'start' ? 'translateX(' + (-dir * inv * 20) + 'px)' : 'translateX(' + (dir * inv * 20) + 'px)';
          el.style.transform = tr;
        }
        return;
      }
      case 'hide':
        if (p._skip === undefined) p._skip = el.hasAttribute('data-hidden');
        if (p._skip) return;
        this.touch(el);
        if (prog >= 1) { this.setHidden(el, true); this.clearInline(el); }
        else el.style.opacity = String(1 - e);
        return;
      case 'state': {
        if (!p._els) {
          var hid = this.hiddenSet(p.id), self = this;
          p._els = { show: [], hide: [] };
          this.managed.forEach(function (m) {
            var isHid = m.hasAttribute('data-hidden');
            if (hid.has(m) && !isHid) p._els.hide.push(m);
            else if (!hid.has(m) && isHid) p._els.show.push(m);
          });
          this.el.setAttribute('data-state', p.id);
        }
        var s2 = this;
        p._els.show.forEach(function (m) {
          s2.touch(m);
          if (prog > 0) s2.setHidden(m, false);
          if (prog >= 1) s2.clearInline(m);
          else { m.style.opacity = String(e); m.style.transform = 'translateY(' + ((1 - e) * 10) + 'px)'; }
        });
        p._els.hide.forEach(function (m) {
          s2.touch(m);
          if (prog >= 1) { s2.setHidden(m, true); s2.clearInline(m); } else m.style.opacity = String(1 - e);
        });
        return;
      }
      case 'type':
      case 'stream': {
        this.touch(el);
        var n = p.units.length, count;
        if (p.k === 'type') {
          var tt = prog * p.dur;
          count = 0;
          while (count < n && p.cum[count] <= tt) count++;
        } else count = Math.floor(e * n + 1e-9);
        if (prog >= 1) {
          if (p.mirror) el.textContent = this.textOrig.get(el);
          else el.textContent = p.units.join('');
          return;
        }
        if (p._cnt === count) return;
        p._cnt = count;
        setPartial(el, p.units, count, p.k === 'type' && p.caret);
        return;
      }
      case 'count': {
        this.touch(el);
        var to = parseFloat(el.getAttribute('data-count-to')), from = parseFloat(el.getAttribute('data-count-from') || '0');
        if (isNaN(to)) return;
        if (!this.textOrig.has(el)) this.remember(el);
        if (prog >= 1) { el.textContent = this.textOrig.get(el); return; }
        el.textContent = this.fmt(el, lerp(from, to, e));
        return;
      }
      case 'draw': {
        this.touch(el);
        if (typeof el.getTotalLength === 'function') {
          var len = el.getTotalLength();
          el.style.strokeDasharray = String(len);
          el.style.strokeDashoffset = String(len * (1 - e));
          if (prog >= 1) this.clearInline(el);
        } else {
          var axis = el.getAttribute('data-draw') === 'x' ? 'x' : 'y';
          el.style.transformOrigin = axis === 'x' ? '0 50%' : '50% 100%';
          el.style.transform = prog >= 1 ? '' : (axis === 'x' ? 'scaleX(' + e + ')' : 'scaleY(' + e + ')');
          if (prog >= 1) { el.style.transformOrigin = ''; this.clearInline(el); }
        }
        return;
      }
      case 'highlight': {
        if (!p._ring) {
          if (getComputedStyle(el).position === 'static') { el.style.position = 'relative'; this.rings.push({ el: el, pos: true }); }
          var ring = document.createElement('span');
          ring.className = 'pu-ring'; ring.setAttribute('aria-hidden', 'true');
          el.appendChild(ring); p._ring = ring; this.rings.push({ ring: ring });
        }
        p._ring.style.opacity = prog >= 1 ? '0' : String(Math.sin(Math.PI * prog));
        p._ring.style.transform = 'scale(' + (0.98 + 0.05 * prog) + ')';
        return;
      }
      case 'press':
        this.touch(el);
        el.style.transform = prog >= 1 ? '' : 'scale(' + (1 - 0.04 * Math.sin(Math.PI * prog)) + ')';
        if (prog >= 1) this.clearInline(el);
        return;
      case 'flag':
        if (prog >= 1 && p._on !== true) {
          p._on = true;
          if (p.on) el.setAttribute(p.attr, ''); else el.removeAttribute(p.attr);
          this.flags.push([el, p.attr]);
        }
        return;
      case 'zoom': {
        var cam = this.cam, W = cam.offsetWidth, H = cam.offsetHeight;
        if (!p._from) p._from = { tx: this.camState.tx, ty: this.camState.ty, k: this.camState.k };
        if (!p._to) {
          if (!p.to) p._to = { tx: 0, ty: 0, k: 1 };
          else {
            // Frame the target: the largest scale at which the whole element (plus a margin) stays
            // in view, capped at the requested scale. If that is barely more than 1, the element
            // is already big enough to read, so the camera stays where it is.
            var tl = this.rootPoint(p.to, 0, 0), br = this.rootPoint(p.to, 1, 1);
            var tw = Math.max(1, br.x - tl.x), th = Math.max(1, br.y - tl.y), pad = 0.06;
            var fitK = Math.min(W / (tw * (1 + 2 * pad)), H / (th * (1 + 2 * pad)));
            var kk = Math.min(p.zk, fitK);
            if (kk < 1.25) p._to = { tx: p._from.tx, ty: p._from.ty, k: p._from.k };
            else {
              var cx = (tl.x + br.x) / 2, cy = (tl.y + br.y) / 2;
              var tx = Math.min(0, Math.max(W - W * kk, W / 2 - cx * kk));
              var ty = Math.min(0, Math.max(H - H * kk, H / 2 - cy * kk));
              p._to = { tx: tx, ty: ty, k: kk };
            }
          }
        }
        var cs = { tx: lerp(p._from.tx, p._to.tx, e), ty: lerp(p._from.ty, p._to.ty, e), k: lerp(p._from.k, p._to.k, e) };
        this.camState = cs;
        cam.style.willChange = prog >= 1 ? '' : 'transform';
        cam.style.transform = (cs.k === 1 && cs.tx === 0 && cs.ty === 0) ? '' : 'translate3d(' + cs.tx + 'px,' + cs.ty + 'px,0) scale(' + cs.k + ')';
        return;
      }
      case 'move': {
        this.touch(el);
        if (!p._from) p._from = this.cursorPos || this.defaultCursor();
        if (!p._to) p._to = this.rootPoint(p.to, 0.6, 0.6);
        var x = lerp(p._from.x, p._to.x, e), y = lerp(p._from.y, p._to.y, e);
        el.style.transform = 'translate(' + x + 'px,' + y + 'px)';
        if (prog >= 1) this.cursorPos = { x: p._to.x, y: p._to.y };
        return;
      }
      default:
    }
  };
  Scene.prototype.defaultCursor = function () {
    var ref = this.cam || this.el.querySelector('.pu-stage') || this.el;
    return { x: ref.offsetWidth * 0.85, y: ref.offsetHeight * 0.85 };
  };

  // ---------- lifecycle ----------
  Scene.prototype.resetVisuals = function () {
    var self = this;
    this.touched.forEach(function (el) { self.clearInline(el); el.style.transformOrigin = ''; });
    this.touched.clear();
    this.rings.forEach(function (r) {
      if (r.ring && r.ring.parentNode) r.ring.parentNode.removeChild(r.ring);
      if (r.pos) r.el.style.position = '';
    });
    this.rings = [];
    this.flags.forEach(function (f) { f[0].removeAttribute(f[1]); });
    this.flags = [];
    this.textOrig.forEach(function (txt, el) { el.textContent = txt; });
    this.prims.forEach(function (p) { p.done = false; p._els = null; p._from = null; p._to = null; p._skip = undefined; p._ring = null; p._on = undefined; p._cnt = undefined; });
    this.cursorPos = null;
    if (this.cam) { this.cam.style.transform = ''; this.cam.style.willChange = ''; this.camState = { tx: 0, ty: 0, k: 1 }; }
  };
  Scene.prototype.applyInitial = function () {
    var self = this;
    var hid = this.initialState ? this.hiddenSet(this.initialState) : null;
    this.managed.forEach(function (m) {
      if (hid) self.setHidden(m, hid.has(m));
    });
    // elements that appear through a reveal step start hidden
    this.prims.forEach(function (p) { if (p.k === 'reveal') self.setHidden(p.el, true); });
    if (this.initialState) this.el.setAttribute('data-state', this.initialState);
    // initial poses for values that animate from a start value
    // text that types or streams starts empty, so an element never shows its full text before its animation begins
    this.prims.forEach(function (p) { if (p.k === 'count' || p.k === 'draw' || p.k === 'type' || p.k === 'stream') self.render(p, 0); });
  };
  Scene.prototype.finalize = function () {
    var self = this;
    this.resetVisuals();
    this.managed.forEach(function (m) { self.setHidden(m, self.finalHidden.has(m)); });
    this.prims.forEach(function (p) { if (p.k === 'reveal' || p.k === 'hide') self.setHidden(p.el, self.finalHidden.has(p.el)); });
    if (this.finalState) this.el.setAttribute('data-state', this.finalState);
    this.el.classList.remove('pu-resetting');
  };
  Scene.prototype.reset = function () {
    this.resetVisuals();
    this.applyInitial();
    this.t = -START_DELAY;
    this.cycle = 0;
    this.finished = false;
  };

  Scene.prototype.update = function () {
    var i, p, prog;
    for (i = 0; i < this.prims.length; i++) {
      p = this.prims[i];
      if (p.at > this.t) break;
      if (p.done) continue;
      prog = p.dur > 0 ? clamp01((this.t - p.at) / p.dur) : 1;
      this.render(p, prog);
      if (prog >= 1) p.done = true;
    }
    var endAt = this.loop ? this.loop.at : this.total;
    if (this.t >= endAt) this.onEnd();
  };
  Scene.prototype.onEnd = function () {
    var self = this;
    if (this.loop && this.cycle + 1 < this.loop.count) {
      this.cycle++;
      this._resetting = true;
      this.el.classList.add('pu-resetting');
      var cyc = this.cycle;
      setTimeout(function () {
        if (!self._resetting) return;
        self._resetting = false;
        self.resetVisuals(); self.applyInitial();
        self.t = -START_DELAY / 2; self.cycle = cyc;
        self.el.classList.remove('pu-resetting');
      }, reducedQuery.matches ? 0 : 200);
      return;
    }
    this.stop(true);
  };
  Scene.prototype.stop = function (complete) {
    this.playing = false;
    cancelAnimationFrame(this._raf);
    if (complete) {
      this.finished = true;
      this.finalize();
      this.el.dispatchEvent(new CustomEvent('scene:complete', { bubbles: true, detail: { id: this.id } }));
    }
    this.syncControls();
  };
  Scene.prototype.frame = function (ts) {
    if (!this.playing) return;
    var dt = this._last ? Math.min(100, ts - this._last) : 0;
    this._last = ts;
    if (!this._resetting) {
      this.t += dt * this.speed;
      this.update();
    }
    if (this.playing) this._raf = requestAnimationFrame(this.frame.bind(this));
  };
  Scene.prototype.run = function () {
    if (this.playing || this.finished || !this.ready) return;
    if (reducedQuery.matches) return;
    this.playing = true; this._last = 0;
    this._raf = requestAnimationFrame(this.frame.bind(this));
    this.syncControls();
  };

  // public controls
  Scene.prototype.play = function () {
    this.userPaused = false;
    if (this.finished) return this.replay();
    if (this.trigger === 'click') this.trigger = 'started';
    if (this.autoPaused && !this.visible && this.trigger === 'view') { /* waits for view */ }
    this.autoPaused = false;
    this.run();
  };
  Scene.prototype.pause = function () {
    this.userPaused = true;
    this._hoverPaused = false;
    this.playing = false; cancelAnimationFrame(this._raf);
    this.syncControls();
  };
  Scene.prototype.suspend = function () {
    if (this.playing) { this.playing = false; cancelAnimationFrame(this._raf); this.syncControls(); }
    this.autoPaused = true;
  };
  Scene.prototype.resume = function () {
    if (this.userPaused || this.finished) return;
    this.autoPaused = false;
    this.run();
  };
  Scene.prototype.replay = function () {
    if (reducedQuery.matches) return this.goToState(this.stateOrder[0]);
    this._resetting = false;
    cancelAnimationFrame(this._raf); this.playing = false;
    this.userPaused = false; this.autoPaused = false;
    this.reset();
    this.run();
  };
  Scene.prototype.seek = function (ms) {
    this._resetting = false;
    cancelAnimationFrame(this._raf); this.playing = false;
    this.resetVisuals(); this.applyInitial();
    this.finished = false; this.cycle = 0;
    this.t = ms;
    for (var i = 0; i < this.prims.length; i++) {
      var p = this.prims[i];
      if (p.at > ms) break;
      var prog = p.dur > 0 ? clamp01((ms - p.at) / p.dur) : 1;
      this.render(p, prog);
      if (prog >= 1) p.done = true;
    }
    this.syncControls();
  };
  Scene.prototype.setSpeed = function (x) { this.speed = x > 0 ? x : 1; };
  Scene.prototype.goToState = function (id) {
    if (!this.states[id]) return;
    var self = this;
    this.stop(false);
    this.resetVisuals();
    var hid = this.hiddenSet(id);
    this.managed.forEach(function (m) { self.setHidden(m, hid.has(m)); });
    this.el.setAttribute('data-state', id);
  };
  Scene.prototype.step = function (dir) {
    var i = this.stateOrder.indexOf(this.el.getAttribute('data-state'));
    var j = Math.max(0, Math.min(this.stateOrder.length - 1, (i < 0 ? this.stateOrder.length - 1 : i) + dir));
    this.goToState(this.stateOrder[j]);
  };
  Scene.prototype.syncControls = function () {
    var self = this;
    Array.prototype.forEach.call(this.el.querySelectorAll('[data-action="toggle"]'), function (b) {
      b.setAttribute('aria-pressed', (self.playing || self._hoverPaused) ? 'true' : 'false');
    });
  };

  Scene.prototype.bindControls = function () {
    var self = this;
    this.el.addEventListener('click', function (ev) {
      var b = ev.target.closest && ev.target.closest('[data-action]');
      if (!b || !self.el.contains(b)) return;
      var a = b.getAttribute('data-action');
      if (a === 'play') self.play();
      else if (a === 'pause') self.pause();
      else if (a === 'toggle') { (self.playing || self._hoverPaused) ? self.pause() : self.play(); }
      else if (a === 'replay') self.replay();
      else if (a === 'next') self.step(1);
      else if (a === 'prev') self.step(-1);
    });
    // Hover and focus used to pause a looping scene. Turned off with data-no-hover-pause
    // so the loop runs uninterrupted while the pointer is over it. Scenes still suspend
    // when scrolled out of view or when the tab is hidden - that is cost, not control.
    if ((this.loop || this.el.hasAttribute('data-loop')) && !this.el.hasAttribute('data-no-hover-pause')) {
      var pauseIn = function () { if (self.playing) { self._hoverPaused = true; self.suspend(); } };
      var resumeOut = function () { if (self._hoverPaused && !self.el.matches(':hover') && !self.el.contains(document.activeElement)) { self._hoverPaused = false; self.resume(); } };
      this.el.addEventListener('mouseenter', pauseIn);
      this.el.addEventListener('mouseleave', resumeOut);
      this.el.addEventListener('focusin', pauseIn);
      this.el.addEventListener('focusout', resumeOut);
    }
  };

  Scene.prototype.setup = function () {
    var self = this;
    this.buildStates();
    // authored hidden set = the final state as rendered
    Array.prototype.forEach.call(this.el.querySelectorAll('[data-hidden]'), function (e) { self.finalHidden.add(e); });
    this.resolve();
    if (this.el.hasAttribute('data-loop')) {
      var raw = (this.el.getAttribute('data-loop') || '').trim().toLowerCase();
      var endless = raw === 'infinite' || raw === 'loop' || raw === '0';
      var count = endless ? Infinity : (parseInt(raw, 10) || 3);
      var gap = parseInt(this.el.getAttribute('data-loop-gap'), 10);
      if (isNaN(gap)) gap = LOOP_GAP;
      if (!this.loop) this.loop = { at: this.total + gap, count: count };
      else { this.loop.count = count; this.loop.at = this.loop.at || this.total + gap; }
    }
    // dev-time check: does the final state match the authored markup?
    if (this.finalState && this.states[this.finalState]) {
      var want = this.hiddenSet(this.finalState);
      this.managed.forEach(function (m) {
        if (want.has(m) !== m.hasAttribute('data-hidden')) warn(self, 'authored markup for "' + m.getAttribute('data-target') + '" does not match final state "' + self.finalState + '"');
      });
    }
    this.el.setAttribute('data-final-state', this.finalState || '');
    this.el.setAttribute('data-duration', String(Math.round(this.total)));
    this.bindControls();
    this.ready = true;
    this.applyMode();
    this.el.classList.add('pu-ready');
  };
  Scene.prototype.applyMode = function () {
    if (reducedQuery.matches) {
      this.el.classList.add('pu-reduced');
      this.stop(false);
      this.finalize();
      this.finished = true;
      return;
    }
    this.el.classList.remove('pu-reduced');
    if (!this.finished || this.t === 0) { this.reset(); this.finished = false; }
  };

  // ---------- manager ----------
  var scenes = [];
  var io = null;
  function manage() {
    var candidates = scenes.filter(function (s) {
      return s.ready && s.visible && !s.finished && !s.userPaused && s.trigger !== 'click' && !document.hidden && !s._hoverPaused && !s.el.closest('.pu-rv-pending');
    }).sort(function (a, b) { return b.ratio - a.ratio; });
    var chosen = candidates[0] || null;
    scenes.forEach(function (s) {
      if (s === chosen) s.resume();
      else if (s.playing) s.suspend();
    });
  }
  function observe(scene) {
    if (scene.trigger === 'load') { scene.visible = true; scene.ratio = 1; return; }
    if (!('IntersectionObserver' in global)) { scene.visible = true; scene.ratio = 1; return; }
    if (!io) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          var sc = en.target.__scene;
          if (!sc) return;
          var need = Math.min(0.5, 0.5 * (global.innerHeight / Math.max(1, en.boundingClientRect.height)));
          sc.ratio = en.intersectionRatio;
          sc.visible = en.isIntersecting && en.intersectionRatio >= need - 1e-6;
        });
        manage();
      }, { threshold: [0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 1] });
    }
    io.observe(scene.el);
  }

  function initOne(el) {
    if (el.__scene) return el.__scene;
    var sc = new Scene(el);
    el.__scene = sc;
    scenes.push(sc);
    sc.load(function () {
      sc.setup();
      observe(sc);
      manage();
    });
    return sc;
  }
  function init(scope) {
    var list = (scope || document).querySelectorAll('[data-scene]');
    return Array.prototype.map.call(list, initOne);
  }

  document.addEventListener('visibilitychange', manage);
  if (reducedQuery.addEventListener) {
    reducedQuery.addEventListener('change', function () {
      scenes.forEach(function (s) { if (s.ready) s.applyMode(); });
      manage();
    });
  }


  // ---------- fit a scene to its page slot ----------
  // <figure class="product-ui pu-fit" data-fit-from="1024" data-fit-width="900" data-fit-height="320" ...>
  // At viewports >= data-fit-from the stage is laid out at data-fit-width, then scaled down (never up)
  // to fit the slot's width and data-fit-height. Controls and caption stay full size below the stage.
  // Below data-fit-from the scene stays fully responsive. Uses transform only.
  function fitOne(fig) {
    var st = fig.querySelector('.pu-stage');
    if (!st) return;
    var from = +fig.getAttribute('data-fit-from') || 0;
    if (global.innerWidth < from) {
      st.style.width = ''; st.style.transform = ''; st.style.margin = '';
      return;
    }
    var dw = +fig.getAttribute('data-fit-width'), mh = +fig.getAttribute('data-fit-height') || 1e9;
    var w = fig.clientWidth;
    st.style.margin = '0'; st.style.transformOrigin = '0 0'; st.style.transform = 'none'; st.style.width = dw + 'px';
    var h = st.offsetHeight;
    // offsetHeight is rounded to an integer; the real box is fractional. Snapping against
    // the rounded value leaves the scaled stage off-grid anyway, so measure precisely.
    var hExact = st.getBoundingClientRect().height || h;
    var k = Math.min(1, w / dw, mh / h);
    // Below this the scene is not "fitted", it is shrunk: text drops under the 11px floor
    // in responsive.md and fine detail stops resolving. The answer is a narrower design
    // width with less in it, not a smaller scale, so say so loudly at build time.
    // Only judge the fit where the slot is at full width. Between breakpoints the column
    // is legitimately narrower and a smaller scale is the correct answer, so warning there
    // would be crying wolf.
    if (k < MIN_FIT_SCALE && global.innerWidth >= FIT_JUDGE_FROM) {
      warnFit(fig, k, dw, w);
    }
    // Snap so the scaled stage ends on a whole pixel. An arbitrary factor leaves the
    // stage 0.5-0.9px tall at the bottom, so the border is antialiased into a grey smear
    // and every baseline sits off-grid - which reads as "blurry" even at a good scale.
    if (k < 1 && hExact > 0) {
      var snapped = Math.floor(hExact * k) / hExact;
      if (snapped > 0 && Math.abs(snapped - k) < 0.02) k = snapped;
    }
    if (k < 1) st.setAttribute('data-scaled', ''); else st.removeAttribute('data-scaled');
    st.style.transform = 'scale(' + k + ')';
    st.style.marginLeft = Math.max(0, (w - dw * k) / 2) + 'px';
    st.style.marginBottom = (-(h * (1 - k))) + 'px';
    st.style.marginRight = (-(dw * (1 - k))) + 'px';
  }
  function fitAll(scope) {
    var list = (scope || document).querySelectorAll('.pu-fit');
    Array.prototype.forEach.call(list, function (f) {
      fitOne(f);
      if (global.ResizeObserver && !f.__fit) {
        f.__fit = new ResizeObserver(function () { fitOne(f); });
        f.__fit.observe(f.parentElement || f);
      }
    });
  }
  global.addEventListener('resize', function () { fitAll(); });

  // ---------- section reveal on scroll ----------
  // [data-reveal] blocks that start below the fold fade up once, the first time they are scrolled into
  // view (optional data-reveal-delay in ms, so an image can follow its text). Blocks already in view on
  // load are never hidden, so the first screen is complete. A scene inside a pending block waits for it.
  // Once revealed, the observer lets go: it never repeats.
  function revealInit(scope) {
    var list = (scope || document).querySelectorAll('[data-reveal]');
    if (!list.length || reducedQuery.matches || !('IntersectionObserver' in global)) return;
    var vh = global.innerHeight;
    var rv = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, d = +el.getAttribute('data-reveal-delay') || 0;
        rv.unobserve(el);
        setTimeout(function () {
          el.classList.remove('pu-rv-pending');
          el.classList.add('pu-rv-in');
          setTimeout(function () { el.classList.remove('pu-rv-in'); manage(); }, 700);
          setTimeout(manage, 350);
        }, d);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    Array.prototype.forEach.call(list, function (el) {
      if (el.__rv) return;
      el.__rv = true;
      if (el.getBoundingClientRect().top < vh * 0.85) return;
      el.classList.add('pu-rv-pending');
      rv.observe(el);
    });
  }

  global.ProductScenes = {
    fit: fitAll,
    reveal: revealInit,
    version: '0.1.0',
    init: init,
    scenes: scenes,
    get: function (x) {
      var el = typeof x === 'string' ? document.querySelector('[data-scene="' + x + '"]') : x;
      return el && el.__scene || null;
    }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { fitAll(); revealInit(); init(); });
  else { fitAll(); revealInit(); init(); }
})(window);
