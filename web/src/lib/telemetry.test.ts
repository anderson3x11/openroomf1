// Run with: node --experimental-strip-types src/lib/telemetry.test.ts
import assert from 'node:assert/strict';
import { delta, distinctColors, miniSectors, smooth } from './telemetry.ts';
import type { Driver, TelemetryLap } from './types.ts';

const lap = (t: number[]) => ({ t }) as TelemetryLap;
const fast = lap([0, 1000, 2000, 3000, 4000]);
const slow = lap([0, 1200, 2200, 3100, 4300]); // lost in the first quarter, gains in the third

assert.deepEqual(delta(fast, slow), [0, 0.2, 0.2, 0.1, 0.3]);

const sectors = miniSectors([fast, slow], 4);
assert.deepEqual(
	sectors.map((s) => [s.from, s.to]),
	[[0, 1], [1, 2], [2, 3], [3, 4]]
);
assert.deepEqual(sectors.map((s) => s.best), [0, 0, 1, 0]);

const drv = (code: string, team: string, color: string | null) => ({ drv: code, team, color }) as Driver;
assert.deepEqual(distinctColors([drv('VER', 'RB', '#3671C6'), drv('LAW', 'RB', '#3671C6'), drv('LEC', 'Ferrari', null)]), {
	VER: '#3671C6',
	LAW: '#FFFFFF',
	LEC: '#B07CFF'
});
assert.deepEqual(smooth([0, 0, 3, 0, 0], 1), [0, 1, 1, 1, 0]); // a GPS spike flattened
assert.deepEqual(smooth([1, 2, 3], 1), [1.5, 2, 2.5]); // shorter window at the ends
console.log('telemetry ok');
