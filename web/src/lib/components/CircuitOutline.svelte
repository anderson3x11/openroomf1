<script lang="ts">
	import type { Circuit } from '#lib/types.ts';

	let { circuit, label }: { circuit: Circuit; label: string } = $props();

	const points = $derived(circuit.path.map(([x, y]) => `${x},${y}`).join(' '));
</script>

<svg viewBox="0 0 {circuit.w} {circuit.h}" role="img" aria-label={label}>
	<polygon {points} />
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: 100%;
	}
	polygon {
		fill: none;
		stroke: var(--ink);
		stroke-width: 10;
		stroke-linejoin: round;
		opacity: 0.9;
	}
</style>
