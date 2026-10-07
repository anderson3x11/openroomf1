<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		title,
		desc,
		wide = false,
		actions,
		children
	}: { title: string; desc?: string; wide?: boolean; actions?: Snippet; children: Snippet } = $props();
</script>

<section class="panel" class:wide>
	<header>
		<div>
			<h2>// {title}</h2>
			{#if desc}<p>{desc}</p>{/if}
		</div>
		{#if actions}<div class="actions">{@render actions()}</div>{/if}
	</header>
	{@render children()}
</section>

<style>
	.panel {
		background: var(--bg);
		padding: 20px;
		min-width: 0;
	}
	.wide {
		grid-column: 1 / -1;
	}
	header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 16px;
		flex-wrap: wrap;
		margin-bottom: 16px;
	}
	h2 {
		font: 700 14px/1.2 var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		margin: 0;
	}
	p {
		font: 13px/1.45 var(--mono);
		color: var(--ink-muted);
		margin: 6px 0 0;
		max-width: 90ch;
	}
</style>
