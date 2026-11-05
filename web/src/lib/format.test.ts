// Run with: node --experimental-strip-types src/lib/format.test.ts
import assert from 'node:assert/strict';
import { inkOn, officialTitle, shortCircuit, shortName } from './format.ts';

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
assert.equal(inkOn('#FFD12E'), '#0B0B0F'); // dark ink on a light team color
assert.equal(inkOn('#1E2A6B'), '#FFFFFF');
assert.equal(inkOn(null), '#FFFFFF');

console.log('format ok');
