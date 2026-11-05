// Run with: node --experimental-strip-types src/lib/format.test.ts
import assert from 'node:assert/strict';
import { joinNeutralSpans, officialTitle, shortCircuit, shortName } from './format.ts';

const cases: [string, string][] = [
	['Circuit Park Zandvoort', 'Zandvoort'],
	['Circuit de Spa-Francorchamps', 'Spa-Francorchamps'],
	['Autodromo Nazionale di Monza', 'Monza'],
	['Albert Park Grand Prix Circuit', 'Albert Park'],
	['Sepang International Circuit', 'Sepang'],
	['Miami International Autodrome', 'Miami'],
	['Baku City Circuit', 'Baku'],
	['Marina Bay Street Circuit', 'Marina Bay'],
	['Silverstone Circuit', 'Silverstone'],
	['Red Bull Ring', 'Red Bull Ring'],
	['Hungaroring', 'Hungaroring'],
	['Circuit Gilles Villeneuve', 'Montreal'],
	['Circuit of the Americas', 'Austin'],
	['Autódromo José Carlos Pace', 'Interlagos'],
	['Autódromo Hermanos Rodríguez', 'Mexico City'],
	['Autodromo Enzo e Dino Ferrari', 'Imola'],
	['Jeddah Corniche Circuit', 'Jeddah'],
	['Bahrain International Circuit', 'Sakhir'],
	['Las Vegas Strip Street Circuit', 'Las Vegas'],
	['Lusail International Circuit', 'Lusail'],
	['Yas Marina Circuit', 'Yas Marina']
];
for (const [full, short] of cases) assert.equal(shortCircuit(full), short, full);
assert.equal(shortCircuit(null), null);
assert.equal(shortName('Dutch Grand Prix'), 'Dutch');
assert.equal(officialTitle('FORMULA 1 HEINEKEN DUTCH GRAND PRIX 2026', 'x'), 'HEINEKEN DUTCH GRAND PRIX');

console.log('format ok');

assert.deepEqual(
	joinNeutralSpans([
		{ kind: 'vsc', from: 7, to: 8 },
		{ kind: 'sc', from: 44, to: 44 },
		{ kind: 'red', from: 45, to: 46 }
	]),
	[
		{ from: 7, to: 8, label: 'VSC' },
		{ from: 44, to: 46, label: 'SC / RED FLAG' }
	]
);
