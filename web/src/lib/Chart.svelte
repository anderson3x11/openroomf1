<script lang="ts">
	import { BarChart, BoxplotChart, HeatmapChart, LineChart, ScatterChart } from 'echarts/charts';
	import {
		AriaComponent,
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
	import { SVGRenderer } from 'echarts/renderers';

	echarts.use([
		LineChart,
		BarChart,
		BoxplotChart,
		HeatmapChart,
		ScatterChart,
		VisualMapComponent,
		AriaComponent,
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

	// Filters rebuild the option: replace it without recreating the chart.
	$effect(() => {
		chart?.setOption(option, { notMerge: true });
	});
</script>

<div bind:this={el} style:height="{height}px"></div>
