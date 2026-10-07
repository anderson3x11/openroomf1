import { ui } from '#lib/ui.svelte.ts';

// Usual tyre code: soft red, medium yellow, hard white, intermediate green, wet blue.
const COLORS: Record<string, string> = {
	SOFT: '#E8002D',
	MEDIUM: '#FFD12E',
	HARD: '#F0F0EC',
	INTERMEDIATE: '#43B02A',
	WET: '#0067FF',
	UNKNOWN: '#5A5A5A'
};

/** The white hard tyre disappears on the light theme: a light gray stands for it. */
export const tyreColor = (cmp: string) =>
	cmp === 'HARD' && ui.theme === 'light' ? '#B9B8B1' : (COLORS[cmp] ?? COLORS.UNKNOWN);
