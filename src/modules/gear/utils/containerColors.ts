import type { TContainerColor } from '../types/gear.types'

export const CONTAINER_COLORS: TContainerColor[] = [
  'default',
  'coyote',
  'khaki',
  'olive',
  'forestGreen',
  'tan',
  'brown',
  'black',
  'navy',
  'jeans',
  'gray',
  'orange',
]

export const COLOR_CLASSES: Record<TContainerColor, string> = {
  default: 'bg-gray-100 border-gray-300 text-gray-800 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200',
  coyote: 'bg-amber-100 border-amber-300 text-amber-900 dark:bg-amber-900 dark:border-amber-700 dark:text-amber-200',
  khaki: 'bg-yellow-50 border-yellow-200 text-yellow-900 dark:bg-yellow-900 dark:border-yellow-700 dark:text-yellow-200',
  olive: 'bg-lime-100 border-lime-300 text-lime-900 dark:bg-lime-900 dark:border-lime-700 dark:text-lime-200',
  forestGreen: 'bg-green-100 border-green-400 text-green-900 dark:bg-green-900 dark:border-green-600 dark:text-green-200',
  tan: 'bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-950 dark:border-amber-800 dark:text-amber-200',
  brown: 'bg-amber-200 border-amber-400 text-amber-950 dark:bg-amber-950 dark:border-amber-800 dark:text-amber-100',
  black: 'bg-gray-800 border-gray-600 text-gray-100 dark:bg-gray-950 dark:border-gray-700 dark:text-gray-100',
  navy: 'bg-blue-900 border-blue-700 text-blue-100 dark:bg-blue-950 dark:border-blue-800 dark:text-blue-100',
  jeans: 'bg-blue-100 border-blue-400 text-blue-900 dark:bg-blue-900 dark:border-blue-600 dark:text-blue-200',
  gray: 'bg-gray-200 border-gray-400 text-gray-900 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200',
  orange: 'bg-orange-100 border-orange-300 text-orange-900 dark:bg-orange-900 dark:border-orange-700 dark:text-orange-200',
}

export const COLOR_BORDER_CLASSES: Record<TContainerColor, string> = {
  default: 'border-gray-300',
  coyote: 'border-amber-700',
  khaki: 'border-yellow-400',
  olive: 'border-lime-700',
  forestGreen: 'border-green-700',
  tan: 'border-amber-300',
  brown: 'border-amber-800',
  black: 'border-gray-800',
  navy: 'border-blue-900',
  jeans: 'border-blue-600',
  gray: 'border-gray-500',
  orange: 'border-orange-500',
}

export const COLOR_TEXT_CLASSES: Record<TContainerColor, string> = {
  default: 'text-gray-400',
  coyote: 'text-amber-800',
  khaki: 'text-yellow-800',
  olive: 'text-lime-800',
  forestGreen: 'text-green-800',
  tan: 'text-amber-700',
  brown: 'text-amber-900',
  black: 'text-gray-900',
  navy: 'text-blue-900',
  jeans: 'text-blue-700',
  gray: 'text-gray-700',
  orange: 'text-orange-700',
}

export const COLOR_DOT_CLASSES: Record<TContainerColor, string> = {
  default: 'bg-gray-400',
  coyote: 'bg-[#8B6F47]',
  khaki: 'bg-[#C3B091]',
  olive: 'bg-[#556B2F]',
  forestGreen: 'bg-[#006B3C]',
  tan: 'bg-[#D2B48C]',
  brown: 'bg-[#8B4513]',
  black: 'bg-[#111111]',
  navy: 'bg-[#000080]',
  jeans: 'bg-[#4B6FA8]',
  gray: 'bg-[#808080]',
  orange: 'bg-[#FFA500]',
}
