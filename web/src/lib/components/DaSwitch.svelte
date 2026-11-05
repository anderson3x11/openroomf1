<script lang="ts">
	// Art directions under test, on this branch only.
	import { setDa, ui, type Da } from '#lib/ui.svelte.ts';

	const OPTIONS: { id: Da; label: string }[] = [
		{ id: 'livery', label: 'Livery' },
		{ id: 'hub', label: 'Race Hub' },
		{ id: 'tower', label: 'Tower' },
		{ id: '', label: 'Current' }
	];
</script>

<div class="switch" role="group" aria-label="Art direction">
	{#each OPTIONS as o (o.id)}
		<button aria-pressed={ui.da === o.id} onclick={() => setDa(o.id)}>{o.label}</button>
	{/each}
</div>

<style>
	.switch {
		position: fixed;
		z-index: 50;
		right: 16px;
		bottom: 16px;
		display: flex;
		gap: 2px;
		padding: 4px;
		border-radius: 999px;
		background: #0b0b0f;
		box-shadow: 0 4px 16px rgb(0 0 0 / 40%);
	}
	button {
		font: 600 13px/1 system-ui, sans-serif;
		color: #c8c8d0;
		background: none;
		border: none;
		border-radius: 999px;
		padding: 8px 14px;
		cursor: pointer;
	}
	button[aria-pressed='true'] {
		color: #0b0b0f;
		background: #fff;
	}
</style>
