// Chart tokens per theme, mirrored from src/app.css.
import { ui } from '#lib/ui.svelte.ts';

const DARK = {
	ink: '#EAEAEA',
	muted: '#8A8A8A',
	rule: '#2A2A2A',
	grid: '#1A1A1A',
	surface: '#0A0A0A', // panel background: stint gaps are drawn in this color
	tooltip: '#141414',
	neutral: 'rgba(255, 209, 46, 0.08)',
	gain: '#4AF626',
	loss: '#E61919',
	// Lap time heatmap: one hue, bright = fast, dark = slow. Flagged laps are gray.
	heat: ['#FF4D4D', '#7A1414', '#2A0A0A'],
	flagged: '#262626'
};
const LIGHT = {
	ink: '#111111',
	muted: '#5E5E5A',
	rule: '#CFCDC6',
	grid: '#E2E0DA',
	surface: '#F4F4F0',
	tooltip: '#FFFFFF',
	neutral: 'rgba(154, 116, 0, 0.12)',
	gain: '#1D7A1D',
	loss: '#E61919',
	heat: ['#B30F0F', '#F08080', '#FBE3E3'],
	flagged: '#DAD8D2'
};

export const MONO = "'JetBrains Mono', ui-monospace, monospace";

// What each art direction under test changes in the charts: type, grounds, line and bar shapes.
const DA = {
	'': { font: MONO, line: 2, bar: 0, dot: 0 },
	livery: {
		font: "'Figtree', sans-serif",
		line: 3,
		bar: 6,
		dot: 7,
		dark: { rule: '#34343E', grid: '#23232B', surface: '#191920', tooltip: '#23232B' },
		light: { rule: '#D6D4CE', grid: '#E7E5E0', surface: '#FFFFFF', tooltip: '#FFFFFF' }
	},
	hub: {
		font: "'Titillium Web', sans-serif",
		line: 2.5,
		bar: 4,
		dot: 0,
		dark: { rule: '#303037', grid: '#25252E', surface: '#1C1C25', tooltip: '#25252E' },
		light: { rule: '#D5D5DC', grid: '#E6E6EB', surface: '#FFFFFF', tooltip: '#FFFFFF' }
	},
	tower: {
		font: "'Saira', sans-serif",
		line: 2.5,
		bar: 8,
		dot: 6,
		dark: { rule: '#2C2F3A', grid: '#1F222B', surface: '#14161D', tooltip: '#1F222B' },
		light: { rule: '#CDD0D8', grid: '#E2E4EA', surface: '#FFFFFF', tooltip: '#FFFFFF' }
	}
} as const;

/** Reading ui.theme and ui.da here makes every chart option depend on them. */
export const tokens = () => {
	const da = DA[ui.da];
	const theme = ui.theme === 'light' ? LIGHT : DARK;
	return { ...theme, ...('dark' in da ? da[ui.theme] : {}), font: da.font, line: da.line, bar: da.bar, dot: da.dot };
};

export function base() {
	const t = tokens();
	return {
		animation: false,
		textStyle: { fontFamily: t.font, color: t.muted, fontSize: 12 },
		tooltip: {
			backgroundColor: t.tooltip,
			borderColor: t.rule,
			borderRadius: 0,
			textStyle: { color: t.ink, fontFamily: t.font, fontSize: 12 }
		}
	};
}

export function axis() {
	const t = tokens();
	return {
		axisLine: { lineStyle: { color: t.rule } },
		axisTick: { show: false },
		axisLabel: { color: t.muted },
		splitLine: { lineStyle: { color: t.grid } }
	};
}
