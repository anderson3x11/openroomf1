<script lang="ts">
	import type { Circuit } from '#lib/types.ts';

	let { circuit, label }: { circuit: Circuit; label: string } = $props();

	const points = $derived(circuit.path.map(([x, y]) => `${x},${y}`).join(' '));
</script>

<svg viewBox="0 0 {circuit.w} {circuit.h}" role="img" aria-label={label}>
	{#key points}<polygon {points} pathLength="1" />{/key}
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: 100%;
	}
	polygon {
		fill: none;
		stroke: currentcolor;
		stroke-width: 10;
		stroke-linejoin: round;
		opacity: 0.9;
		stroke-dasharray: 1;
		animation: draw 1100ms var(--ease-in-out) both;
	}
	/* Arriving on a Grand Prix: the track draws itself, once. */
	@keyframes draw {
		from {
			stroke-dashoffset: 1;
		}
		to {
			stroke-dashoffset: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		polygon {
			animation: none;
		}
	}
</style>
