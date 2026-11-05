<script lang="ts">
	import { BarChart, BoxplotChart, HeatmapChart, LineChart, ScatterChart } from 'echarts/charts';
	import {
		GridComponent,
		LegendComponent,
		TooltipComponent,
		AxisPointerComponent,
		DataZoomComponent,
		MarkAreaComponent,
		MarkLineComponent,
		VisualMapComponent
	} from 'echarts/components';
	import * as echarts from 'echarts/core';
	import { capture } from '#lib/capture.svelte.ts';
	import { SVGRenderer } from 'echarts/renderers';

	echarts.use([
		LineChart,
		BarChart,
		BoxplotChart,
		HeatmapChart,
		ScatterChart,
		VisualMapComponent,
		MarkLineComponent,
		MarkAreaComponent,
		DataZoomComponent,
		GridComponent,
		LegendComponent,
		TooltipComponent,
		AxisPointerComponent,
		SVGRenderer
	]);

	let { option, height = 480 }: { option: echarts.EChartsCoreOption; height?: number } = $props();
	let el: HTMLDivElement;

	let chart: echarts.ECharts | undefined = $state();

	$effect(() => {
		const c = echarts.init(el, null, { renderer: 'svg' });
		const ro = new ResizeObserver(() => c.resize());
		ro.observe(el);
		chart = c;
		return () => {
			ro.disconnect();
			c.dispose();
		};
	});

	// Filters rebuild the option: replace it without recreating the chart. The lines draw
	// themselves when the chart opens only: a filter must not replay it.
	let opened = false;
	$effect(() => {
		if (!chart) return;
		const reveal = !opened && !matchMedia('(prefers-reduced-motion: reduce)').matches;
		chart.setOption(
			reveal ? { ...option, animation: true, animationDuration: 700, animationEasing: 'cubicOut' } : option,
			{ notMerge: true }
		);
		opened = true;
	});

	// Screenshots: no zoom slider, but the zoom itself is kept (merged, not replaced).
	$effect(() => {
		const show = !capture.on;
		const zooms = (chart?.getOption()?.dataZoom ?? []) as { type: string }[];
		if (!chart || !zooms.some((z) => z.type === 'slider')) return;
		chart.setOption({ dataZoom: zooms.map((z) => (z.type === 'slider' ? { show } : {})) });
		chart.getZr().flush();
	});
</script>

<div bind:this={el} style:height="{height}px"></div>
