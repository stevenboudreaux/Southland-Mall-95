// Unit tests for the CLAW machine rules (prototypes/godot-mall/play/claw/logic.js).
// Run: node tests/unit/claw/logic.test.js
'use strict';
const assert = require('assert');
const CL = require('../../../prototypes/godot-mall/play/claw/logic.js');
const C = CL.CONFIG;
let n = 0;
function t(name, f) { f(); n++; console.log('ok ' + name); }

t('a fresh fill holds every kind, the slammer once and at the bottom, nothing over the chute', () => {
  const items = CL.fill(1);
  const total = CL.FILL.reduce((s, f) => s + f[1], 0);
  assert.strictEqual(items.length, total);
  assert.strictEqual(items.filter(i => i.kind === 'slammer').length, 1);
  assert.strictEqual(items[0].kind, 'slammer');
  assert.ok(Math.abs(items[0].y - C.deckY) < 1e-9);
  items.forEach(i => assert.ok(!CL.inChute(i.x - CL.KINDS[i.kind].r, i.z - CL.KINDS[i.kind].r), 'over the chute: ' + i.kind));
  for (const k of Object.keys(CL.KINDS)) assert.ok(items.some(i => i.kind === k), 'missing ' + k);
});

t('fills are deterministic for a seed', () => {
  const a = CL.fill(7), b = CL.fill(7);
  assert.deepStrictEqual(a, b);
  assert.notDeepStrictEqual(CL.fill(7), CL.fill(8));
});

t('settle stacks an item on the ones under it', () => {
  const items = CL.settle([{ kind: 't75', x: 0, z: 0.5, y: 0 }, { kind: 't100', x: 0.01, z: 0.5, y: 0 }, { kind: 'gator', x: 0.25, z: 0.7, y: 0 }]);
  assert.ok(Math.abs(items[0].y - C.deckY) < 1e-9);
  assert.ok(items[1].y > C.deckY + 0.05);
  assert.ok(Math.abs(items[2].y - C.deckY) < 1e-9);
});

t('the claw meets the highest item within reach, nothing if none is near', () => {
  const items = CL.settle([{ kind: 'gator', x: 0, z: 0.5, y: 0 }, { kind: 't75', x: 0.02, z: 0.5, y: 0 }]);
  const tg = CL.target(items, 0.01, 0.5);
  assert.strictEqual(tg.item.kind, 't75');
  assert.strictEqual(CL.target(items, 0.25, 0.75), null);
});

t('the grip is full on every strongEvery-th play and weak otherwise', () => {
  const r = CL.rng(3);
  assert.strictEqual(CL.grip(C.strongEvery, r), 1);
  assert.strictEqual(CL.grip(2 * C.strongEvery, r), 1);
  for (let i = 1; i < C.strongEvery; i++) { const g = CL.grip(i, r); assert.ok(g >= C.weakMin && g <= C.weakMax); }
});

t('a strong, centred grab on a capsule wins; a weak grab on the big plush does not even lift', () => {
  const items = CL.settle([{ kind: 't200', x: 0, z: 0.5, y: 0 }]);
  const res = CL.judge(CL.target(items, 0, 0.5), 1.0);
  assert.ok(res.lifted && res.carry >= 1);
  const out = CL.resolve(items, 0, 0.5, res);
  assert.strictEqual(out.won.kind, 't200');
  assert.strictEqual(out.items.length, 0);
  const big = CL.settle([{ kind: 'rougarou', x: 0, z: 0.5, y: 0 }]);
  const weak = CL.judge(CL.target(big, 0.05, 0.5), C.weakMin);
  assert.strictEqual(weak.lifted, false);
  assert.strictEqual(CL.resolve(big, 0.05, 0.5, weak).won, null);
});

t('a weak grab on a capsule lifts it and drops it part way home (it moves in the pile)', () => {
  const items = CL.settle([{ id: 'a', kind: 't75', x: 0.2, z: 0.7, y: 0, rot: 0 }]);
  const res = CL.judge(CL.target(items, 0.2, 0.7), 0.42);
  assert.ok(res.lifted && res.carry > 0 && res.carry < 1, JSON.stringify(res));
  const out = CL.resolve(items, 0.2, 0.7, res);
  assert.strictEqual(out.won, null);
  assert.ok(out.moved && out.moved.x < 0.2 && out.moved.z < 0.7);
  assert.strictEqual(out.items.length, 1);
});

t('a slipped prize that lands over the chute is still won', () => {
  const items = CL.settle([{ id: 'a', kind: 't75', x: -0.22, z: 0.36, y: 0, rot: 0 }]);
  const out = CL.resolve(items, -0.22, 0.36, { lifted: true, carry: 0.5, item: items[0] });
  assert.ok(out.won && out.fellIn);
});

t('the gantry stays inside its limits and the joystick is normalised', () => {
  let p = [0, 0.5];
  for (let i = 0; i < 100; i++) p = CL.move(p, 1, 1, 0.1);
  assert.ok(Math.abs(p[0] - C.xMax) < 1e-9 && Math.abs(p[1] - C.zMax) < 1e-9);
  const q = CL.move([0, 0.5], 1, 1, 1);
  assert.ok(Math.abs(Math.hypot(q[0], q[1] - 0.5) - C.speed) < 1e-9);
});

t('inventory records carry tickets and pogs', () => {
  const r1 = CL.record({ id: 'x', kind: 't100' }, 2, 123);
  assert.strictEqual(r1.tickets, 100); assert.strictEqual(r1.from, 'claw2');
  const r2 = CL.record({ id: 'y', kind: 'slammer' }, 1, 5);
  assert.ok(r2.rare && r2.pogs.length === 1);
});
console.log(n + ' passed');
