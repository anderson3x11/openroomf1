<script lang="ts">
	import type { RaceEvents } from '#lib/types.ts';

	let { events }: { events: RaceEvents } = $props();

	const KIND_LABELS: Record<string, string> = {
		sc: 'SC',
		vsc: 'VSC',
		red: 'RED FLAG',
		finish: 'FINISH',
		penalty: 'PENALTY',
		investigation: 'INQUIRY'
	};
</script>

<ol>
	{#each events.msgs as m, i (i)}
		<li class:alert={m.kind === 'penalty' || m.kind === 'red'}>
			<span class="label lap">L{String(m.lap).padStart(2, '0')}</span>
			<span class="label kind kind-{m.kind}">[ {KIND_LABELS[m.kind]} ]</span>
			<span class="msg">{m.msg}</span>
		</li>
	{/each}
</ol>

<style>
	ol {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	li {
		display: grid;
		grid-template-columns: 3.5em 11em 1fr;
		gap: 8px;
		padding: 6px 0;
		border-bottom: 1px solid var(--rule-soft);
		font-size: 13px;
	}
	.kind {
		white-space: nowrap;
	}
	.msg {
		color: var(--ink-muted);
	}
	.alert .msg,
	.alert .kind {
		color: var(--accent);
	}
	.kind-sc,
	.kind-vsc {
		color: var(--sc);
	}
</style>
