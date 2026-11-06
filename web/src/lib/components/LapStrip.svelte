<script lang="ts">
	// One cell per lap: press on a lap and drag to another to pick a range, a simple click
	// isolates one lap. Neutralised laps (SC, VSC, red flag) are marked.
	import type { RaceEvents } from '#lib/types.ts';

	let {
		laps = $bindable(),
		total,
		neutral
	}: { laps: [number, number]; total: number; neutral: RaceEvents['neutral'] } = $props();

	let anchor: number | null = $state(null);

	const cells = $derived(Array.from({ length: total }, (_, i) => i + 1));
	const isNeutral = (lap: number) => neutral.some((s) => lap >= s.from && lap <= s.to);
	const pick = (a: number, b: number) => (laps = [Math.min(a, b), Math.max(a, b)]);

	function down(e: PointerEvent, lap: number) {
		// Touch captures the pointer on the first cell: release it so the other cells get
		// pointerenter while the finger moves.
		(e.currentTarget as HTMLElement).releasePointerCapture?.(e.pointerId);
		anchor = lap;
		pick(lap, lap);
	}
</script>

<svelte:window onpointerup={() => (anchor = null)} onpointercancel={() => (anchor = null)} />

<div class="strip" role="group" aria-label="Lap range">
	{#each cells as lap (lap)}
		<button
			class="cell"
			class:in={lap >= laps[0] && lap <= laps[1]}
			class:sc={isNeutral(lap)}
			title="Lap {lap}{isNeutral(lap) ? ' (SC, VSC or red flag)' : ''}"
			aria-label="Lap {lap}"
			onpointerdown={(e) => down(e, lap)}
			onpointerenter={() => anchor !== null && pick(anchor, lap)}
			onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && pick(lap, lap)}
		></button>
	{/each}
</div>
<div class="ticks label" aria-hidden="true">
	{#each cells.filter((l) => l === 1 || l === total || (l % 20 === 0 && total - l >= 8)) as lap (lap)}
		<span style:left="{((lap - 0.5) / total) * 100}%">{lap}</span>
	{/each}
</div>

<style>
	.strip {
		display: flex;
		height: 32px;
		overflow: hidden;
		border-radius: 8px;
		touch-action: none; /* dragging selects laps instead of scrolling the page */
		user-select: none;
	}
	.cell {
		flex: 1;
		min-width: 0;
		padding: 0;
		border: 0;
		background: var(--rule);
		border-radius: 0;
		cursor: pointer;
		transition: none;
	}
	.cell.in {
		background: var(--accent);
	}
	/* Neutralised laps, the same yellow in both themes. */
	.cell.sc {
		background: color-mix(in srgb, #ffd12e 45%, var(--rule));
	}
	.cell.sc.in {
		background: #ffd12e;
	}
	@media (hover: hover) {
		.cell:hover,
		.cell.in:hover {
			background: var(--ink);
		}
	}
	.ticks {
		position: relative;
		height: 16px;
		margin-top: 4px;
	}
	.ticks span {
		position: absolute;
		transform: translateX(-50%);
	}
</style>
