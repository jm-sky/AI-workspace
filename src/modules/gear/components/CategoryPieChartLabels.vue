<script setup lang="ts" generic="Data extends { category: string, labelX: number, labelY: number, percentage: number }">

defineProps<{
  chartData: Data[]
  centerX?: number
  centerY?: number
  labelRadius?: number
  showHelperCircle?: boolean
}>()
</script>

<template>
  <svg
    class="absolute inset-0 pointer-events-none"
    viewBox="0 0 430 300"
    preserveAspectRatio="xMidYMid meet"
  >
    <g transform="translate(30, 30)">
      <!-- Helper circle to visualize label positions -->
      <g v-if="showHelperCircle && centerX !== undefined && centerY !== undefined && labelRadius !== undefined">
        <circle
          :cx="centerX"
          :cy="centerY"
          :r="labelRadius"
          fill="none"
          stroke="rgba(255, 0, 0, 0.3)"
          stroke-width="1"
          stroke-dasharray="2,2"
        />
        <!-- Center point -->
        <circle
          :cx="centerX"
          :cy="centerY"
          r="2"
          fill="rgba(255, 0, 0, 0.5)"
        />
      </g>
      <g
        v-for="data in chartData"
        :key="data.category"
        class="chart-label"
      >
        <text
          :x="data.labelX"
          :y="data.labelY"
          text-anchor="middle"
          dominant-baseline="middle"
          class="fill-foreground text-sm font-semibold"
        >
          {{ data.percentage.toFixed(1) }}%
        </text>
      </g>
    </g>
  </svg>
</template>
