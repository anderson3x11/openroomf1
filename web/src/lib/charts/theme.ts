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

/** Reading ui.theme here makes every chart option depend on the theme. */
export const tokens = () => (ui.theme === 'light' ? LIGHT : DARK);

export function base() {
	const t = tokens();
	return {
		animation: false,
		textStyle: { fontFamily: MONO, color: t.muted, fontSize: 12 },
		tooltip: {
			backgroundColor: t.tooltip,
			borderColor: t.rule,
			borderRadius: 0,
			textStyle: { color: t.ink, fontFamily: MONO, fontSize: 12 }
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
