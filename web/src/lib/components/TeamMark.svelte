<script lang="ts">
	// Team logo, or the team color swatch when the logo is missing.
	let { src, color, team }: { src?: string; color?: string | null; team: string } = $props();
</script>

{#if src}<img {src} alt={team} />{:else}<span class="swatch" style:background={color}></span>{/if}

<style>
	img {
		height: 20px;
		width: 20px;
		object-fit: contain;
		margin-right: 8px;
		vertical-align: -4px;
	}
</style>
