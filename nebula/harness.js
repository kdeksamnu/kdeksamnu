/* Headless harness: runs demo.html's inline script against a stub DOM + canvas
   so runtime errors surface here instead of in the user's browser.          */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const html = fs.readFileSync(path.join(__dirname, 'demo.html'), 'utf8');
const coreSrc = fs.readFileSync(path.join(__dirname, 'core.js'), 'utf8');
const inline = html.match(/<script>([\s\S]*?)<\/script>/)[1];

/* ------------------------------------------------------------- DOM stubs */
let elCount = 0;
function makeEl(id) {
  const listeners = {};
  const el = {
    id, tagName: 'DIV', _id: ++elCount,
    style: new Proxy({}, { set: () => true, get: () => '' }),
    dataset: {}, children: [], firstChild: null,
    textContent: '', innerHTML: '', value: '0', checked: true,
    className: '', scrollTop: 0, scrollHeight: 0,
    appendChild(c) { this.children.push(c); this.firstChild = this.children[0]; return c; },
    removeChild(c) { const i = this.children.indexOf(c); if (i >= 0) this.children.splice(i, 1); this.firstChild = this.children[0] || null; return c; },
    addEventListener(t, f) { (listeners[t] = listeners[t] || []).push(f); },
    removeEventListener() {},
    dispatch(t, ev) { (listeners[t] || []).forEach(f => f(ev)); },
    setPointerCapture() {}, releasePointerCapture() {},
    getBoundingClientRect() { return { left: 0, top: 0, width: 512, height: 320 }; },
    click() { if (this.onclick) this.onclick({ target: this }); },
    getContext(kind) { return kind === '2d' ? makeCtx(this) : null; },
    _listeners: listeners
  };
  return el;
}
function makeCtx(canvas) {
  return {
    canvas,
    fillStyle: '', strokeStyle: '', lineWidth: 1, globalAlpha: 1,
    createImageData(w, h) { return { width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }; },
    getImageData(x, y, w, h) { return this.createImageData(w, h); },
    putImageData() { putImageDataCalls++; },
    fillRect() { drawCalls++; }, beginPath() {}, arc() {}, stroke() { drawCalls++; },
    save() {}, restore() {}, clearRect() {}, translate() {}, scale() {}
  };
}
let putImageDataCalls = 0, drawCalls = 0;

const registry = new Map();
const defaults = {
  radius: '6', strength: '45', dir: '35', speed: '2', macroRate: '4', chanSel: '-1', styleSel: 'vanilla'
};
const checkboxes = { agentsOn: true, negotiateOn: true, overlayOn: true, naiveOn: true };

function getEl(id) {
  if (!registry.has(id)) {
    const el = makeEl(id);
    if (id in defaults) el.value = defaults[id];
    if (id in checkboxes) el.checked = checkboxes[id];
    registry.set(id, el);
  }
  return registry.get(id);
}

const document = {
  getElementById: getEl,
  createElement: t => makeEl('#' + t),
  body: makeEl('body'),
  addEventListener() {}
};

/* ------------------------------------------------------- frame scheduler */
let rafQueue = [];
let now = 0;
const performance = { now: () => now };
function requestAnimationFrame(cb) { rafQueue.push(cb); return rafQueue.length; }

const windowObj = { document, performance, requestAnimationFrame, console, __lc: 0 };
windowObj.window = windowObj;

const sandbox = vm.createContext(Object.assign(windowObj, {
  document, performance, requestAnimationFrame, console,
  Math, Date, Float32Array, Uint8Array, Uint8ClampedArray, Float64Array, Int32Array,
  Set, Map, Array, Object, JSON, Number, String, Boolean, isFinite, isNaN, Promise,
  parseInt, parseFloat, setTimeout, clearTimeout
}));

/* load core first (it attaches window.NEBULA) */
vm.runInContext(coreSrc, sandbox, { filename: 'core.js' });
if (!sandbox.NEBULA) throw new Error('core.js did not attach NEBULA');

/* ------------------------------------------------------------- run demo */
vm.runInContext(inline, sandbox, { filename: 'demo-inline.js' });

const FRAMES = 260;
(async function pump() {
  let f = 0;
  const t0 = Date.now();
  while (f < FRAMES) {
    const q = rafQueue; rafQueue = [];
    if (!q.length) { await new Promise(r => setImmediate(r)); continue; }
    now += 16.7;
    for (const cb of q) cb(now);
    f++;

    // drive some interactions mid-run so the edit path is exercised
    if (f === 60) simulatePaint('raise', 40, 30);
    if (f === 70) { getEl('radius').value = '9'; simulatePaint('carve', 42, 32); }
    if (f === 80) simulatePaint('afforest', 80, 50);
    if (f === 90) simulatePaint('deforest', 82, 52);
    if (f === 100) simulatePaint('build', 95, 40);
    if (f === 110) { getEl('styleSel').value = 'neon'; getEl('styleSel').onchange && getEl('styleSel').onchange(); }
    if (f === 130) getEl('conflictBtn').click();
    if (f === 150) getEl('redeliverBtn').click();
    if (f === 170) getEl('replayBtn').click();
    if (f === 190) { getEl('chanSel').value = '0'; }
    if (f === 200) { getEl('speed').value = '6'; }
    if (f === 220) simulatePaint('erode', 60, 40);
    if (f === 240) { getEl('stepBtn').click(); }
  }

  function simulatePaint(toolId, cx, cy) {
    // select the tool button
    const tools = getEl('tools');
    const btn = tools.children.find(c => c.dataset && c.dataset.id === toolId);
    if (btn && btn.onclick) btn.onclick();
    const cv = getEl('cvMain');
    const rect = cv.getBoundingClientRect();
    const px = (cx / 128) * rect.width + rect.left;
    const py = (cy / 80) * rect.height + rect.top;
    cv.dispatch('pointerdown', { clientX: px, clientY: py, pointerId: 1 });
    cv.dispatch('pointermove', { clientX: px + 3, clientY: py + 2, pointerId: 1 });
    cv.dispatch('pointerup', { clientX: px, clientY: py, pointerId: 1 });
  }

  // ---- assertions on final state
  const app = sandbox;
  console.log(`\nran ${f} frames in ${Date.now() - t0}ms  (putImageData=${putImageDataCalls}, drawCalls=${drawCalls})`);

  const bootVisible = getEl('boot').style.display;
  const appVisible = getEl('app').style.display;
  console.log(`boot display="${bootVisible}"  app display="${appVisible}"`);

  const hudVals = {};
  for (const k of ['fps', 'micro', 'macro', 'decisions', 'hifi', 'queue', 'decode', 'events', 'fp', 'mass', 'costc', 'costn']) {
    hudVals[k] = strip(getEl('hud-' + k).innerHTML);
  }
  console.log('\nHUD:');
  for (const [k, v] of Object.entries(hudVals)) console.log(`  ${k.padEnd(10)} ${v}`);

  const logLines = getEl('log').children.map(c => c.textContent);
  console.log(`\nevent log: ${logLines.length} entries; last 14:`);
  logLines.slice(-14).forEach(l => console.log('  ' + l));

  console.log(`\nnaive panel: rmse=${getEl('nvRmse').textContent} drift=${getEl('nvDrift').textContent}`);
  console.log(`cost panel:\n${strip(getEl('cost').innerHTML).split('\n').map(s => '  ' + s).join('\n')}`);

  function strip(h) { return String(h).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(); }

  // hard failures
  let bad = 0;
  if (appVisible !== 'grid') { console.log('\nFAIL: app never became visible (init did not complete)'); bad++; }
  if (!/^\w+$/.test(hudVals.fp)) { console.log('FAIL: no fingerprint'); bad++; }
  if (+hudVals.micro.split(' ')[0].replace(/,/g, '') < 50) { console.log('FAIL: micro sim barely ran'); bad++; }
  if (logLines.length < 10) { console.log('FAIL: event log suspiciously empty'); bad++; }
  if (putImageDataCalls < 100) { console.log('FAIL: canvas never rendered'); bad++; }
  if (!logLines.some(l => /canyon cells/.test(l))) { console.log('FAIL: conflict test did not run'); bad++; }
  if (!logLines.some(l => /replayed .* events/.test(l))) { console.log('FAIL: replay probe did not run'); bad++; }
  if (!logLines.some(l => /redelivered/.test(l))) { console.log('FAIL: redeliver probe did not run'); bad++; }
  if (!logLines.some(l => /IDENTICAL/.test(l))) { console.log('FAIL: replay did not verify idempotency'); bad++; }
  console.log(bad ? `\n${bad} HARD FAILURES` : '\nno hard failures');
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error('HARNESS ERROR:', e); process.exit(1); });