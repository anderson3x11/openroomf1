import type { RaceEvents } from '#lib/types.ts';
import { tokens } from './theme.ts';

const LABELS = { sc: 'SC', vsc: 'VSC', red: 'RED FLAG' };

/** Shaded lap ranges for safety car, VSC and red flag, attached to one series. */
export function neutralMarkArea(spans: RaceEvents['neutral']) {
	const t = tokens();
	return {
		silent: true,
		itemStyle: { color: t.neutral },
		label: { color: t.muted, fontSize: 11, position: 'insideTop' },
		data: spans.map((s) => [{ xAxis: s.from - 1, name: LABELS[s.kind] }, { xAxis: s.to }])
	};
}
