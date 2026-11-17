// Localz TV loop — Christmas overlay.
// Garland + twinkling lights across the top of every slide, with a different
// set of hanging ornaments on each slide. Injected into deploy/loop.html by
// tools/add_christmas.py. Turns itself off after XMAS_END, or with ?xmas=0.
(function () {
  var XMAS_END = new Date('2027-01-07T00:00:00');
  if (new Date() >= XMAS_END || /[?&]xmas=0/.test(location.search)) return;

  var FRAME = 0.93;
  var NS = 'http://www.w3.org/2000/svg';
  var W = 1920, H = 1080;

  var css = document.createElement('style');
  css.textContent =
    '#xmas{position:fixed;inset:0;z-index:40;pointer-events:none;}' +
    // TVs crop the outer few % of the picture (overscan), so the whole frame is pulled in
    // to FRAME of the screen; the slides are shrunk to match (SAFE in add_christmas.py).
    '#xmas svg{width:100%;height:100%;display:block;overflow:visible;transform:scale(' + FRAME + ');transform-origin:50% 50%;}' +
    '.xm-orn{opacity:0;transition:opacity 1.2s ease;}' +
    '.xm-orn.on{opacity:1;}' +
    '.xm-sway{transform-box:view-box;animation:xmSway 5s ease-in-out infinite alternate;}' +
    '@keyframes xmSway{from{transform:rotate(-4deg)}to{transform:rotate(4deg)}}' +
    '.xm-glow{animation:xmTw 2.4s ease-in-out infinite alternate;}' +
    '.xm-bulb{animation:xmTwB 2.4s ease-in-out infinite alternate;}' +
    '@keyframes xmTw{0%{opacity:.15}60%{opacity:.85}100%{opacity:1}}' +
    '@keyframes xmTwB{0%{opacity:.55}60%{opacity:.95}100%{opacity:1}}';
  document.head.appendChild(css);

  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  // Seeded random so the garland looks the same every reload.
  var seed = 7;
  function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }

  var wrap = document.createElement('div');
  wrap.id = 'xmas';
  var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, preserveAspectRatio: 'xMidYMid meet' });
  wrap.appendChild(svg);

  // ── Gradients ──
  var defs = el('defs', {}, svg);
  function radial(id, stops, cx, cy) {
    var g = el('radialGradient', { id: id, cx: cx || '35%', cy: cy || '30%', r: '70%' }, defs);
    stops.forEach(function (s) { el('stop', { offset: s[0], 'stop-color': s[1], 'stop-opacity': s[2] == null ? 1 : s[2] }, g); });
  }
  radial('xg-red',    [['0%', '#ff8a7a'], ['45%', '#d0141f'], ['100%', '#5a0008']]);
  radial('xg-gold',   [['0%', '#fff1b8'], ['45%', '#f2af32'], ['100%', '#7a4e05']]);
  radial('xg-green',  [['0%', '#9be7a0'], ['45%', '#178a3a'], ['100%', '#063d17']]);
  radial('xg-silver', [['0%', '#ffffff'], ['45%', '#c9d3de'], ['100%', '#5d6b7a']]);
  radial('xg-blue',   [['0%', '#b9dcff'], ['45%', '#2f6fd6'], ['100%', '#0c2340']]);
  radial('xg-ice',    [['0%', '#ffffff'], ['50%', '#bfe6ff'], ['100%', '#4c8fc4']]);
  ['#ff3b3b', '#2ee86b', '#3d8bff', '#ffc93c', '#fff4d6', '#ff7ad9'].forEach(function (c, i) {
    radial('xg-l' + i, [['0%', c, 0.95], ['35%', c, 0.45], ['100%', c, 0]], '50%', '50%');
  });

  // ── Garland path: four swags across the top ──
  var JOINS = [-30, 465, 960, 1455, 1950];
  var TOP = 14, DIP = 14;
  function swagY(x, top, dip) {
    for (var i = 0; i < JOINS.length - 1; i++) {
      if (x >= JOINS[i] && x <= JOINS[i + 1]) {
        var t = (x - JOINS[i]) / (JOINS[i + 1] - JOINS[i]);
        var c = 2 * dip - top;
        return (1 - t) * (1 - t) * top + 2 * t * (1 - t) * c + t * t * top;
      }
    }
    return top;
  }
  function swagPath(top, dip) {
    var d = '';
    for (var i = 0; i < JOINS.length - 1; i++) {
      var a = JOINS[i], b = JOINS[i + 1];
      d += (i ? ' ' : 'M' + a + ' ' + top) + ' Q' + (a + b) / 2 + ' ' + (2 * dip - top) + ' ' + b + ' ' + top;
    }
    return d;
  }
  var gY = function (x) { return swagY(x, TOP, DIP); };

  // Generic swag along any span: joins = break points, edge = rest offset, dip = sag offset.
  function sag(v, joins, edge, dip) {
    for (var i = 0; i < joins.length - 1; i++) {
      if (v >= joins[i] && v <= joins[i + 1]) {
        var t = (v - joins[i]) / (joins[i + 1] - joins[i]);
        return (1 - t) * (1 - t) * edge + 2 * t * (1 - t) * (2 * dip - edge) + t * t * edge;
      }
    }
    return edge;
  }
  var JV = [-20, 360, 720, 1100];                 // left/right edges: three swags
  var JB = [-30, 480, 960, 1440, 1950];           // bottom: four swags
  // Each side as a point function over its own axis. Sides sag inward only a little
  // so the slides stay readable; the top keeps its deeper swags.
  var SIDES = [
    { name: 'top',    from: 8, to: 1912, pt: function (v) { return [v, sag(v, JOINS, TOP, DIP)]; },            rot: 0 },
    { name: 'left',   from: 10, to: 1070, pt: function (v) { return [12, v]; },                 rot: 90 },
    { name: 'right',  from: 10, to: 1070, pt: function (v) { return [W - 12, v]; },             rot: -90 },
    { name: 'bottom', from: 8, to: 1912, pt: function (v) { return [v, H - 12]; },             rot: 0 }
  ];
  var LIGHT = {   // the light wire sits a touch further in than the bough
    top:    function (v) { return [v, 22]; },
    // sides and bottom: the wire runs through the bough and bulbs point OUT toward
    // the screen edge, so nothing covers slide text
    left:   function (v) { return [14, v]; },
    right:  function (v) { return [W - 14, v]; },
    bottom: function (v) { return [v, H - 14]; }
  };
  function pathFor(fn, from, to) {
    var d = '';
    for (var v = from; v <= to; v += 8) { var p = fn(v); d += (d ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }
    return d;
  }

  var lights = el('g', {}, svg);   // behind the garland, so the wire tucks in
  var garland = el('g', {}, svg);
  var bows = el('g', {}, svg);
  var ornLayer = el('g', {}, svg);

  var greens = ['#0e4a22', '#17692f', '#1f7f3a', '#2a9147', '#0a3a1a', '#3aa457'];
  var byColor = {};
  // Draw the sides first so the top garland lays over them at the corners.
  [SIDES[1], SIDES[2], SIDES[3], SIDES[0]].forEach(function (side) {
    var d = pathFor(side.pt, side.from, side.to);
    el('path', { d: d, fill: 'none', stroke: '#0b3d1c', 'stroke-width': 34, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, garland);
    el('path', { d: d, fill: 'none', stroke: '#145a2a', 'stroke-width': 22, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, garland);
    for (var v = side.from; v <= side.to; v += 4) {
      var p = side.pt(v);
      for (var n = 0; n < 5; n++) {
        var ang = rnd() * Math.PI * 2, len = 12 + rnd() * 16;
        var ox = (rnd() - 0.5) * 14, oy = (rnd() - 0.5) * 14;
        var c = greens[Math.floor(rnd() * greens.length)];
        byColor[c] = (byColor[c] || '') + 'M' + (p[0] + ox).toFixed(1) + ' ' + (p[1] + oy).toFixed(1) +
          'l' + (Math.cos(ang) * len).toFixed(1) + ' ' + (Math.sin(ang) * len).toFixed(1);
      }
    }
  });
  for (var col in byColor) el('path', { d: byColor[col], stroke: col, 'stroke-width': 3, 'stroke-linecap': 'round', fill: 'none' }, garland);
  // Pinecones and berries tucked in all the way around
  SIDES.forEach(function (side) {
    var count = Math.round((side.to - side.from) / 42);
    for (var b = 0; b < count; b++) {
      var p = side.pt(side.from + 40 + rnd() * (side.to - side.from - 80));
      var bx = p[0] + (rnd() - 0.5) * 16, by = p[1] + (rnd() - 0.5) * 16;
      if (rnd() < 0.35) {
        el('ellipse', { cx: bx, cy: by, rx: 7, ry: 11, fill: '#6b3f1d', transform: 'rotate(' + (rnd() * 180) + ' ' + bx + ' ' + by + ')' }, garland);
      } else {
        el('circle', { cx: bx, cy: by, r: 5.5, fill: '#d0141f' }, garland);
        el('circle', { cx: bx - 1.5, cy: by - 1.5, r: 1.8, fill: '#ff9b9b' }, garland);
      }
    }
  });

  // ── Lights all the way around, bulbs pointing in toward the slide ──
  var BULB_COLORS = ['#ff3b3b', '#2ee86b', '#3d8bff', '#ffc93c', '#fff4d6', '#ff7ad9'];
  var li = 0;
  SIDES.forEach(function (side) {
    var fn = LIGHT[side.name];
    el('path', { d: pathFor(fn, side.from, side.to), fill: 'none', stroke: '#0d2a14', 'stroke-width': 3 }, lights);
    var start = side.name === 'top' || side.name === 'bottom' ? 20 : 90;
    var stop = side.name === 'top' || side.name === 'bottom' ? 1920 : 1000;
    for (var v = start; v < stop; v += 58) {
      var p = fn(v);
      var tilt = side.rot + (rnd() - 0.5) * 30;
      var g = el('g', { transform: 'translate(' + p[0].toFixed(1) + ' ' + p[1].toFixed(1) + ') rotate(' + tilt.toFixed(1) + ')' }, lights);
      var ci = li % 6;
      var delay = (-rnd() * 2.4).toFixed(2) + 's', dur = (1.6 + rnd() * 1.8).toFixed(2) + 's';
      var glow = el('circle', { cx: 0, cy: 18, r: side.name === 'top' ? 34 : 24, fill: 'url(#xg-l' + ci + ')', class: 'xm-glow' }, g);
      glow.style.animationDelay = delay; glow.style.animationDuration = dur;
      el('rect', { x: -5, y: 0, width: 10, height: 9, rx: 2, fill: '#1c3a22' }, g);
      var bulb = el('path', { d: 'M-7 9 C-11 20 -7 32 0 34 C7 32 11 20 7 9 Z', fill: BULB_COLORS[ci], class: 'xm-bulb' }, g);
      bulb.style.animationDelay = delay; bulb.style.animationDuration = dur;
      el('ellipse', { cx: -2.5, cy: 17, rx: 2, ry: 5, fill: '#fff', opacity: 0.6 }, g);
      li++;
    }
  });

  // ── Bows at each swag join, all four sides ──
  function bow(x, y, s, r) {
    var g = el('g', { transform: 'translate(' + x + ' ' + y + ') rotate(' + (r || 0) + ') scale(' + s + ')' }, bows);
    el('path', { d: 'M-4 4 L-16 46 L-6 40 L-2 50 Z', fill: '#a60d16' }, g);
    el('path', { d: 'M4 4 L16 46 L6 40 L2 50 Z', fill: '#a60d16' }, g);
    el('path', { d: 'M0 0 C-12 -26 -44 -22 -38 -2 C-34 12 -12 8 0 0 Z', fill: '#d0141f' }, g);
    el('path', { d: 'M0 0 C12 -26 44 -22 38 -2 C34 12 12 8 0 0 Z', fill: '#d0141f' }, g);
    el('path', { d: 'M-4 -4 C-14 -16 -30 -14 -30 -4', stroke: '#ff6b6b', 'stroke-width': 3, fill: 'none', opacity: 0.7 }, g);
    el('path', { d: 'M4 -4 C14 -16 30 -14 30 -4', stroke: '#ff6b6b', 'stroke-width': 3, fill: 'none', opacity: 0.7 }, g);
    el('circle', { cx: 0, cy: 0, r: 9, fill: '#b5101a' }, g);
    el('circle', { cx: -2, cy: -2, r: 3, fill: '#ff8080', opacity: 0.6 }, g);
  }
  [465, 960, 1455].forEach(function (x) { bow(x, TOP + 2, 1); });
  [480, 960, 1440].forEach(function (x) { bow(x, H - 14, 0.9, 0); });
  [360, 720].forEach(function (y) { bow(14, y, 0.9, 90); bow(W - 14, y, 0.9, -90); });
  // big corner bows
  bow(34, 30, 1.15, -45); bow(W - 34, 30, 1.15, 45);
  bow(34, H - 30, 1.15, 45); bow(W - 34, H - 30, 1.15, -45);

  // ── Ornament shapes (hook at 0,0, hanging down) ──
  function cap(g, w) {
    el('rect', { x: -w / 2, y: 0, width: w, height: 10, rx: 2, fill: 'url(#xg-gold)' }, g);
  }
  function shine(g, cx, cy, r) {
    el('ellipse', { cx: cx - r * 0.35, cy: cy - r * 0.4, rx: r * 0.22, ry: r * 0.32, fill: '#fff', opacity: 0.55,
      transform: 'rotate(-30 ' + (cx - r * 0.35) + ' ' + (cy - r * 0.4) + ')' }, g);
  }
  var SHAPES = {
    ball: function (g, grad, r) {
      cap(g, 16);
      el('circle', { cx: 0, cy: 10 + r, r: r, fill: 'url(#' + grad + ')' }, g);
      el('path', { d: 'M' + (-r * 0.92) + ' ' + (10 + r * 0.8) + ' Q0 ' + (10 + r * 1.25) + ' ' + (r * 0.92) + ' ' + (10 + r * 0.8),
        stroke: 'rgba(255,255,255,.35)', 'stroke-width': 3, fill: 'none' }, g);
      shine(g, 0, 10 + r, r);
    },
    star: function (g, grad, r) {
      el('circle', { cx: 0, cy: 4, r: 4, fill: 'none', stroke: '#f2af32', 'stroke-width': 2 }, g);
      var pts = [], cy = 8 + r;
      for (var i = 0; i < 10; i++) {
        var a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r;
        pts.push((Math.cos(a) * rr).toFixed(1) + ',' + (cy + Math.sin(a) * rr).toFixed(1));
      }
      el('polygon', { points: pts.join(' '), fill: 'url(#' + grad + ')', stroke: '#fff3c4', 'stroke-width': 2, 'stroke-linejoin': 'round' }, g);
      el('circle', { cx: -r * 0.2, cy: cy - r * 0.25, r: r * 0.12, fill: '#fff', opacity: 0.7 }, g);
    },
    cane: function (g, _grad, r) {
      var s = r / 34;
      var d = 'M' + (-26 * s) + ' ' + (22 * s) + ' A' + (16 * s) + ' ' + (16 * s) + ' 0 0 1 ' + (6 * s) + ' ' + (22 * s) + ' L' + (6 * s) + ' ' + (130 * s);
      el('path', { d: d, stroke: '#7a0b12', 'stroke-width': 17 * s, fill: 'none', 'stroke-linecap': 'round', transform: 'translate(0 -6)' }, g);
      el('path', { d: d, stroke: '#ffffff', 'stroke-width': 14 * s, fill: 'none', 'stroke-linecap': 'round', transform: 'translate(0 -6)' }, g);
      el('path', { d: d, stroke: '#d0141f', 'stroke-width': 14 * s, fill: 'none', 'stroke-dasharray': (9 * s) + ' ' + (11 * s), transform: 'translate(0 -6)' }, g);
      el('path', { d: 'M' + (2 * s) + ' ' + (30 * s) + ' L' + (2 * s) + ' ' + (118 * s), stroke: '#fff', 'stroke-width': 2.5 * s, opacity: 0.5, fill: 'none', 'stroke-linecap': 'round' }, g);
    },
    flake: function (g, _grad, r) {
      var cy = 6 + r;
      el('circle', { cx: 0, cy: 3, r: 3, fill: 'none', stroke: '#dff3ff', 'stroke-width': 2 }, g);
      var d = '';
      for (var i = 0; i < 6; i++) {
        var a = i * Math.PI / 3 - Math.PI / 2, ca = Math.cos(a), sa = Math.sin(a);
        d += 'M0 ' + cy + 'l' + (ca * r).toFixed(1) + ' ' + (sa * r).toFixed(1);
        [0.45, 0.72].forEach(function (f) {
          var px = ca * r * f, py = cy + sa * r * f, bl = r * (f < 0.6 ? 0.3 : 0.2);
          [-1, 1].forEach(function (sg) {
            var b2 = a + sg * Math.PI / 4;
            d += 'M' + px.toFixed(1) + ' ' + py.toFixed(1) + 'l' + (Math.cos(b2) * bl).toFixed(1) + ' ' + (Math.sin(b2) * bl).toFixed(1);
          });
        });
      }
      el('path', { d: d, stroke: '#4c8fc4', 'stroke-width': 7, 'stroke-linecap': 'round', fill: 'none', opacity: 0.55 }, g);
      el('path', { d: d, stroke: '#ffffff', 'stroke-width': 4, 'stroke-linecap': 'round', fill: 'none' }, g);
      el('circle', { cx: 0, cy: cy, r: r * 0.14, fill: 'url(#xg-ice)', stroke: '#fff', 'stroke-width': 2 }, g);
    },
    bell: function (g, grad, r) {
      var s = r / 34;
      el('circle', { cx: 0, cy: 4 * s, r: 5 * s, fill: 'none', stroke: '#f2af32', 'stroke-width': 3 }, g);
      el('path', { d: 'M0 ' + (8 * s) + ' C' + (-22 * s) + ' ' + (8 * s) + ' ' + (-26 * s) + ' ' + (40 * s) + ' ' + (-30 * s) + ' ' + (62 * s) +
        ' L' + (-38 * s) + ' ' + (70 * s) + ' L' + (38 * s) + ' ' + (70 * s) + ' L' + (30 * s) + ' ' + (62 * s) +
        ' C' + (26 * s) + ' ' + (40 * s) + ' ' + (22 * s) + ' ' + (8 * s) + ' 0 ' + (8 * s) + ' Z', fill: 'url(#' + grad + ')' }, g);
      el('circle', { cx: 0, cy: 74 * s, r: 7 * s, fill: '#7a4e05' }, g);
      el('path', { d: 'M' + (-10 * s) + ' ' + (22 * s) + ' C' + (-14 * s) + ' ' + (34 * s) + ' ' + (-16 * s) + ' ' + (46 * s) + ' ' + (-20 * s) + ' ' + (58 * s),
        stroke: '#fff', 'stroke-width': 4 * s, opacity: 0.5, fill: 'none', 'stroke-linecap': 'round' }, g);
      el('path', { d: 'M0 ' + (10 * s) + ' C' + (-10 * s) + ' ' + (-2 * s) + ' ' + (-22 * s) + ' ' + (2 * s) + ' ' + (-18 * s) + ' ' + (12 * s) + ' Z M0 ' + (10 * s) + ' C' + (10 * s) + ' ' + (-2 * s) + ' ' + (22 * s) + ' ' + (2 * s) + ' ' + (18 * s) + ' ' + (12 * s) + ' Z',
        fill: '#d0141f' }, g);
    },
    drop: function (g, grad, r) {
      cap(g, 12);
      var s = r / 34, top = 10;
      el('path', { d: 'M0 ' + top + ' C' + (34 * s) + ' ' + (top + 34 * s) + ' ' + (30 * s) + ' ' + (top + 70 * s) + ' 0 ' + (top + 120 * s) +
        ' C' + (-30 * s) + ' ' + (top + 70 * s) + ' ' + (-34 * s) + ' ' + (top + 34 * s) + ' 0 ' + top + ' Z', fill: 'url(#' + grad + ')' }, g);
      el('path', { d: 'M' + (-22 * s) + ' ' + (top + 40 * s) + ' Q0 ' + (top + 52 * s) + ' ' + (22 * s) + ' ' + (top + 40 * s) +
        ' M' + (-18 * s) + ' ' + (top + 64 * s) + ' Q0 ' + (top + 76 * s) + ' ' + (18 * s) + ' ' + (top + 64 * s),
        stroke: '#fff', 'stroke-width': 3, opacity: 0.45, fill: 'none' }, g);
      el('ellipse', { cx: -8 * s, cy: top + 38 * s, rx: 4 * s, ry: 12 * s, fill: '#fff', opacity: 0.55 }, g);
    }
  };

  // One theme per slide, cycling: [shape, gradient] for each of the 3 hanging spots per side.
  var THEMES = [
    [['ball', 'xg-red'],    ['ball', 'xg-gold'],   ['ball', 'xg-green']],
    [['star', 'xg-gold'],   ['star', 'xg-gold'],   ['star', 'xg-gold']],
    [['cane'],              ['cane'],              ['cane']],
    [['flake'],             ['flake'],             ['flake']],
    [['ball', 'xg-silver'], ['ball', 'xg-blue'],   ['ball', 'xg-silver']],
    [['bell', 'xg-gold'],   ['bell', 'xg-gold'],   ['bell', 'xg-gold']],
    [['drop', 'xg-ice'],    ['drop', 'xg-red'],    ['drop', 'xg-ice']],
    [['ball', 'xg-red'],    ['star', 'xg-gold'],   ['cane']]
  ];
  // Hanging spots: x positions near each corner, and string length.
  var SPOTS = [
    { x: 92,  len: 34, r: 30 }, { x: 178, len: 92, r: 36 }, { x: 262, len: 44, r: 27 }
  ];

  function buildTheme(theme) {
    var layer = el('g', { class: 'xm-orn' }, ornLayer);
    [1, -1].forEach(function (side) {
      SPOTS.forEach(function (sp, i) {
        var x = side === 1 ? sp.x : W - sp.x;
        var y = gY(x) + 8;
        var sway = el('g', { class: 'xm-sway' }, layer);
        sway.style.transformOrigin = x + 'px ' + y + 'px';
        sway.style.animationDuration = (4 + i * 0.9) + 's';
        sway.style.animationDelay = (-(i + (side > 0 ? 0 : 1.7))) + 's';
        el('line', { x1: x, y1: y, x2: x, y2: y + sp.len, stroke: '#e8c56a', 'stroke-width': 2 }, sway);
        var g = el('g', { transform: 'translate(' + x + ' ' + (y + sp.len) + ')' }, sway);
        var t = theme[side === 1 ? i : 2 - i];
        SHAPES[t[0]](g, t[1], sp.r);
      });
    });
    return layer;
  }

  var current = null, idx = Math.floor(Math.random() * THEMES.length);
  function next() {
    idx = (idx + 1) % THEMES.length;
    var layer = buildTheme(THEMES[idx]);
    void layer.getBoundingClientRect();
    requestAnimationFrame(function () { layer.classList.add('on'); });
    var old = current;
    current = layer;
    if (old) {
      old.classList.remove('on');
      setTimeout(function () { if (old.parentNode) old.parentNode.removeChild(old); }, 1400);
    }
  }

  document.body.appendChild(wrap);
  window.__xmas = { next: next };
  next();
})();
