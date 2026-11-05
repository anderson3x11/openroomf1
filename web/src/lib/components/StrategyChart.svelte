<script lang="ts">
	import { strategyRows } from '#lib/strategy.ts';
	import { tyreColor } from '#lib/tyres.ts';
	import type { Driver, Stint } from '#lib/types.ts';

	let {
		drivers,
		stints,
		laps,
		compounds,
		legend,
		stops
	}: {
		drivers: Driver[];
		stints: Stint[];
		laps: [number, number];
		compounds: Set<string>; // selected: the others are dimmed, the row keeps its shape
		legend: string[];
		stops: number;
	} = $props();

	const rows = $derived(strategyRows(drivers, stints, laps));
	const lastName = (name: string) => name.split(' ').slice(1).join(' ') || name;
	const tyre = (s: Stint) => (s.new === null ? 'age unknown' : s.new ? 'new' : `used, ${s.age} laps`);
	const pad = (lap: number | null) => (lap === null ? '' : String(lap).padStart(2, '0'));
</script>

<ol class="rows">
	{#each rows as { driver, segments, marks, last }, i (driver.drv)}
		<li style:--i={i}>
			<span class="name" title={driver.name}
				><span class="full">{lastName(driver.name)}</span><span class="code">{driver.drv}</span></span
			>
			<span class="track">
				{#each segments as { stint: s, left, width } (s.stint)}
					<span
						class="bar"
						class:used={s.new === false}
						class:off={!compounds.has(s.cmp)}
						style:left="{left}%"
						style:width="{width}%"
						style:--tyre={tyreColor(s.cmp)}
						title="{s.cmp}, {tyre(s)}, laps {s.from} to {s.to}"
					></span>
				{/each}
				{#each marks as m (m.lap)}
					<span class="disc" style:left="{m.x}%">{m.lap}</span>
				{/each}
			</span>
			<span class="end">{pad(last)}</span>
		</li>
	{/each}
</ol>

<div class="foot">
	<div class="keys label">
		<span class="key" style:--tyre="var(--ink-muted)"><span class="sample used"></span>Used</span>
		<span class="key" style:--tyre="var(--ink-muted)"><span class="sample"></span>New</span>
		{#each legend as c (c)}
			<span class="key" style:--tyre={tyreColor(c)}><span class="sample"></span>{c}</span>
		{/each}
	</div>
	<p class="total"><span class="label">Total pit stops</span><b>{stops}</b></p>
</div>

<style>
	.rows {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	li {
		display: grid;
		grid-template-columns: 11.5rem minmax(0, 1fr) 2.75rem;
		align-items: center;
		height: 32px;
	}
	.name,
	.end,
	.disc,
	.total b {
		font-family: var(--sans);
		font-weight: 700;
	}
	.name {
		font-size: 14px;
		font-weight: 800;
		text-transform: uppercase;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.code {
		display: none;
	}
	.track {
		position: relative;
		height: 100%;
		margin: 0 14px;
		animation: sweep 650ms var(--ease-out) backwards;
		animation-delay: calc(var(--i) * 22ms);
	}
	/* The race runs from left to right, one driver after the other. */
	@keyframes sweep {
		from {
			clip-path: inset(-16px 100% -16px -16px);
		}
		to {
			clip-path: inset(-16px -16px -16px -16px);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.track {
			animation: none;
		}
	}
	.bar {
		position: absolute;
		top: calc(50% - 4px);
		height: 8px;
		background: var(--tyre);
	}
	.used {
		background: repeating-linear-gradient(-45deg, var(--tyre) 0 3px, transparent 3px 6px);
	}
	.off {
		opacity: 0.15;
	}
	/* The stop sits on the line, in a disc of the panel color that cuts the two stints apart. */
	.disc {
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
		display: grid;
		place-items: center;
		width: 28px;
		height: 28px;
		font-size: 11px;
		background: var(--panel);
		border-radius: 50%;
	}
	.end {
		font-size: 12px;
		text-align: right;
	}
	.foot {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 12px 32px;
		margin-top: 14px;
		padding-top: 14px;
		border-top: 1px solid var(--rule);
	}
	.keys {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 22px;
	}
	.key {
		display: inline-flex;
		align-items: center;
		gap: 8px;
	}
	.sample {
		display: inline-block;
		width: 28px;
		height: 8px;
		background: var(--tyre);
	}
	.sample.used {
		background: repeating-linear-gradient(-45deg, var(--tyre) 0 3px, transparent 3px 6px);
	}
	.total {
		display: flex;
		align-items: center;
		gap: 14px;
		margin: 0;
	}
	.total b {
		font-size: 40px;
		font-weight: 800;
		line-height: 1;
	}
	@media (max-width: 700px) {
		li {
			grid-template-columns: 2.6rem minmax(0, 1fr) 1.9rem;
			height: 28px;
		}
		.full {
			display: none;
		}
		.code {
			display: inline;
		}
		.name {
			font-size: 11px;
		}
		.track {
			margin: 0 10px;
		}
		.disc {
			width: 21px;
			height: 21px;
			font-size: 9px;
		}
		.end {
			font-size: 10px;
		}
		.total b {
			font-size: 30px;
		}
	}
</style>
