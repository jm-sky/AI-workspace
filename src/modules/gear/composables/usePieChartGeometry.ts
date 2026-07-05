import { computed } from 'vue'

export interface ChartGeometry {
  margin: number
  arcWidth: number
  svgWidth: number
  svgHeight: number
  chartAreaSize: number
  centerX: number
  centerY: number
  outerRadius: number
  innerRadius: number
  arcMiddleRadius: number
  labelRadius: number
}

export interface CategoryData {
  category: string
  weight: number
  quantity: number
  price?: number
  priority?: string
  percentage: number
  value: number
}

export interface ChartDataPoint extends Record<string, number | string | undefined> {
  category: string
  value: number
  percentage: number
  weight: number
  quantity: number
  price?: number
  priority?: string
  labelX: number
  labelY: number
}

interface UsePieChartGeometryOptions {
  svgWidth?: number
  svgHeight?: number
  margin?: number
  arcWidth?: number
  padAngle?: number
  labelDistance?: number // Distance from arc middle to label (increases distance from center)
}

export function usePieChartGeometry(options: UsePieChartGeometryOptions = {}) {
  const {
    svgWidth = 430,
    svgHeight = 300,
    margin = 30,
    arcWidth = 60,
    padAngle = 0.02,
    labelDistance = 25, // Increased default to place labels further from center
  } = options

  const chartGeometry = computed<ChartGeometry>(() => {
    // Chart area after margins
    const chartAreaWidth = svgWidth - 2 * margin // 370
    const chartAreaHeight = svgHeight - 2 * margin // 240
    // Donut is circular, so radius is based on the smaller dimension
    const chartAreaSize = Math.min(chartAreaWidth, chartAreaHeight) // 240
    // Donut center in SVG coordinates (before translate)
    const donutCenterXInSvg = svgWidth / 2 // 215 (centered horizontally in 430px width)
    const donutCenterYInSvg = svgHeight / 2 // 150 (centered vertically in 300px height)
    // Center relative to transformed coordinates (after translate(30,30))
    // After translate(30,30), we're in chart area coordinates, so subtract margin
    const centerX = donutCenterXInSvg - margin // 185 (center of donut in chart area)
    const centerY = donutCenterYInSvg - margin // 120 (center of donut in chart area)
    // For circular donut, radius is based on the smaller dimension
    const outerRadius = chartAreaSize / 2 // 120
    const innerRadius = outerRadius - arcWidth // 60
    const arcMiddleRadius = (outerRadius + innerRadius) / 2 // 90
    // Calculate label radius: middle of arc + distance from arc to label
    // Increase labelDistance to place labels further from center
    const labelRadius = arcMiddleRadius + labelDistance

    return {
      margin,
      arcWidth,
      svgWidth,
      svgHeight,
      chartAreaSize,
      centerX,
      centerY,
      outerRadius,
      innerRadius,
      arcMiddleRadius,
      labelRadius,
    }
  })

  const calculateLabelPositions = (
    categoryData: readonly CategoryData[],
    mode: 'weight' | 'quantity' | 'price' | 'priority' | 'weight-breakdown',
  ): ChartDataPoint[] => {
    const geometry = chartGeometry.value
    let currentAngle = -90 // Start from top (12 o'clock)

    // Calculate total pad angle in degrees (padAngle is applied between each segment)
    const numSegments = categoryData.length
    const totalPadAngleDeg = padAngle * numSegments * (180 / Math.PI)
    const availableAngle = 360 - totalPadAngleDeg
    const padAngleDeg = padAngle * (180 / Math.PI) // Convert single pad angle to degrees

    return categoryData.map((data) => {
      let value: number
      if (mode === 'weight' || mode === 'weight-breakdown') {
        value = data.weight
      } else if (mode === 'price') {
        value = data.price ?? 0
      } else {
        value = data.quantity
      }
      // Calculate angle proportionally to available space (accounting for pad-angle)
      const angle = (data.percentage / 100) * availableAngle
      const midAngle = currentAngle + angle / 2
      // Convert angle to radians and calculate position
      const angleRad = (midAngle * Math.PI) / 180
      const labelX = geometry.centerX + Math.cos(angleRad) * geometry.labelRadius
      const labelY = geometry.centerY + Math.sin(angleRad) * geometry.labelRadius

      // Move to next segment, accounting for pad-angle
      currentAngle += angle + padAngleDeg

      return {
        [data.category]: value,
        category: data.category,
        value: data.value,
        percentage: data.percentage,
        weight: data.weight,
        quantity: data.quantity,
        price: data.price,
        priority: data.priority,
        labelX,
        labelY,
      }
    })
  }

  return {
    chartGeometry,
    calculateLabelPositions,
  }
}

