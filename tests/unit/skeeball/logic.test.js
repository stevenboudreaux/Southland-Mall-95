// Unit tests for the SKEE-BALL rules and ball physics (prototypes/godot-mall/play/skeeball/logic.js).
// Run: node tests/unit/skeeball/logic.test.js
'use strict';
const assert = require('assert');
const SK = require('../../../prototypes/godot-mall/play/skeeball/logic.js');
const C = SK.CONFIG;
let n = 0;
function t(name, f) { f(); n++; console.log('ok ' + name); }

t('a game is 9 balls (video)', () => assert.strictEqual(C.balls, 9));

t('the meter fills in meterUpMs, then falls back and rises again', () => {
  assert.strictEqual(SK.meter(0), 0);
  assert.ok(Math.abs(SK.meter(C.meterUpMs / 2) - 0.5) < 1e-9);
  assert.ok(Math.abs(SK.meter(C.meterUpMs) - 1) < 1e-9);
  assert.ok(Math.abs(SK.meter(C.meterUpMs * 1.25) - 0.75) < 1e-9);
  assert.ok(Math.abs(SK.meter(C.meterUpMs * 2) - 0) < 1e-9);
  assert.ok(Math.abs(SK.meter(C.meterUpMs * 2.5) - 0.5) < 1e-9);
});

t('release speed spans vMin..vMax and is clamped', () => {
  assert.strictEqual(SK.speedFor(0), C.vMin);
  assert.strictEqual(SK.speedFor(1), C.vMax);
  assert.strictEqual(SK.speedFor(2), C.vMax);
  assert.strictEqual(SK.speedFor(-1), C.vMin);
});

t('board coordinates round-trip', () => {
  const p = SK.fromBoard(0.2, 0.5, 0.03), b = SK.toBoard(p);
  assert.ok(Math.abs(b.u - 0.2) < 1e-9 && Math.abs(b.v - 0.5) < 1e-9 && Math.abs(b.h - 0.03) < 1e-9);
});

t('every roll ends with a real value, and a hole roll ends in that hole', () => {
  for (let p = 0; p <= 1.0001; p += 0.1) for (let x = -0.28; x <= 0.28; x += 0.07) {
    const r = SK.roll(x, p, 0);
    assert.ok([0, 10, 20, 30, 40, 50, 100].indexOf(r.value) >= 0, 'value ' + r.value);
    if (r.where === 'hole') assert.strictEqual(r.value, SK.HOLES[r.hole][0]);
    assert.ok(r.path.length > 5 && r.t <= C.maxT + C.dt);
  }
});

t('rolls are deterministic for the same seed', () => {
  const a = SK.roll(0.1, 0.4, 1234), b = SK.roll(0.1, 0.4, 1234);
  assert.strictEqual(a.value, b.value);
  assert.strictEqual(a.path.length, b.path.length);
});

t('a soft roll up the middle scores 10 or 20; up the middle a little harder reaches 30 or 40', () => {
  assert.ok([10, 20].indexOf(SK.roll(0, 0.05, 0).value) >= 0);
  assert.ok([30, 40].indexOf(SK.roll(0, 0.36, 0).value) >= 0);
});

t('a hard roll up the middle can reach the 50; a hard roll up the side can reach a 100 pocket', () => {
  let got50 = false, got100 = false;
  for (let p = 0.6; p <= 1.0001; p += 0.02) {
    if (SK.roll(0, p, 0).value === 50) got50 = true;
    for (const x of [-0.26, -0.25, 0.25, 0.26]) if (SK.roll(x, p, 0).value === 100) got100 = true;
  }
  assert.ok(got50 && got100);
});

t('100 pockets are rare over all rolls (under 6 %), 10 is the most common', () => {
  const cnt = {}; let N = 0;
  for (let p = 0; p <= 1.0001; p += 0.04) for (let x = -0.28; x <= 0.2801; x += 0.02) {
    const r = SK.roll(x, p, 1 + N); cnt[r.value] = (cnt[r.value] || 0) + 1; N++;
  }
  assert.ok((cnt[100] || 0) / N < 0.06, '100s ' + (cnt[100] / N));
  const most = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a])[0];
  assert.strictEqual(most, '10');
});

t('tickets: points / pointsPerTicket, plus the bonus per 100 pocket', () => {
  assert.strictEqual(SK.tickets(250, 0), Math.floor(250 / C.pointsPerTicket));
  assert.strictEqual(SK.tickets(300, 2), Math.floor(300 / C.pointsPerTicket) + 2 * C.pocketBonus);
  const ft = SK.feedTimes(5);
  assert.strictEqual(ft.length, 5);
  assert.strictEqual(ft[4], 5 * C.ticketMs);
});
console.log(n + ' passed');
