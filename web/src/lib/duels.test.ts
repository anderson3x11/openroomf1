// Run with: node --experimental-strip-types src/lib/duels.test.ts
import assert from 'node:assert/strict';
import { teamDuels } from './duels.ts';
import type { ResultRow } from './types.ts';

const row = (drv: string, team: string, pos: number) =>
	({ drv, team, pos, num: '', name: drv, tid: team, color: null, grid: pos, cls: String(pos), status: 'Finished', pts: 0, gain: 0 }) as ResultRow;
const results = [row('RUS', 'Mercedes', 1), row('VER', 'Red Bull', 2), row('ANT', 'Mercedes', 3)];
const positions = { laps: 3, pos: { RUS: [1, 2, 1, 1], ANT: [3, 1, 3, 3], VER: [2, 3, 2, 2] } };
const laptimes = { RUS: [[2, 100], [3, 102]] as [number, number][], ANT: [[2, 101]] as [number, number][] };
const speeds = { RUS: { top: 320, s: [], ideal: null, best: 99 }, ANT: { top: 325, s: [], ideal: null, best: 98 } };

const duels = teamDuels(results, positions, laptimes, speeds);
assert.equal(duels.length, 1); // Red Bull has a single driver here: no duel
const [d] = duels;
assert.equal(d.a.r.drv, 'RUS');
assert.deepEqual([d.a.ahead, d.b.ahead], [2, 1]); // ANT led him on lap 1
assert.deepEqual([d.a.pace, d.b.pace], [101, 101]);
assert.deepEqual([d.a.top, d.b.best], [320, 98]);
console.log('duels ok');
