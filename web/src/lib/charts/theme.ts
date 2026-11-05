// Chart tokens per theme, mirrored from src/app.css.
import { ui } from '#lib/ui.svelte.ts';

const DARK = {
	ink: '#F4F4F6',
	muted: '#A2A2AE',
	rule: '#34343E',
	grid: '#23232B',
	surface: '#191920', // panel background
	tooltip: '#23232B',
	neutral: 'rgba(255, 209, 46, 0.08)',
	gain: '#4AF626',
	loss: '#FF5B55',
	// Lap time heatmap: one hue, bright = fast, dark = slow. Flagged laps are gray.
	heat: ['#FF4D4D', '#7A1414', '#2A0A0A'],
	flagged: '#2A2A32'
};
const LIGHT = {
	ink: '#14141A',
	muted: '#5C5C66',
	rule: '#D6D4CE',
	grid: '#E7E5E0',
	surface: '#FFFFFF',
	tooltip: '#FFFFFF',
	neutral: 'rgba(154, 116, 0, 0.12)',
	gain: '#1D7A1D',
	loss: '#C70812',
	heat: ['#B30F0F', '#F08080', '#FBE3E3'],
	flagged: '#E2E0DA'
};

const FONT = "'Figtree', sans-serif";

/** Reading ui.theme here makes every chart option depend on the theme. */
export const tokens = () => (ui.theme === 'light' ? LIGHT : DARK);

export function base() {
	const t = tokens();
	return {
		animation: false,
		textStyle: { fontFamily: FONT, color: t.muted, fontSize: 12 },
		tooltip: {
			backgroundColor: t.tooltip,
			borderColor: t.rule,
			borderRadius: 0,
			textStyle: { color: t.ink, fontFamily: FONT, fontSize: 12 }
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
