<script lang="ts">
	import type { Circuit } from '#lib/types.ts';

	let { circuit, label }: { circuit: Circuit; label: string } = $props();

	const points = $derived(circuit.path.map(([x, y]) => `${x},${y}`).join(' '));
</script>

<svg viewBox="0 0 {circuit.w} {circuit.h}" preserveAspectRatio="xMaxYMid meet" role="img" aria-label={label}>
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
		stroke: currentcolor;
		stroke-width: 4px;
		stroke-linejoin: round;
		vector-effect: non-scaling-stroke;
	}
</style>
