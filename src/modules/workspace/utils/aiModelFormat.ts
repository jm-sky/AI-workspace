import type { AiModelTier, IAiModel } from '@/modules/workspace/types/workspaceConfig'

export type SortKey = 'recommended' | 'power' | 'price' | 'context' | 'name'

export const SORT_KEYS: SortKey[] = ['recommended', 'power', 'price', 'context', 'name']

/** Strongest first, so tier can drive descending "power" order directly. */
export const TIER_RANK: Record<AiModelTier, number> = { frontier: 0, balanced: 1, fast: 2 }

export const TIER_VARIANT: Record<AiModelTier, 'premium' | 'secondary' | 'outline'> = {
  frontier: 'premium',
  balanced: 'secondary',
  fast: 'outline',
}

/** Blended per-1M price: outputs are the minority of tokens, so weight inputs higher. */
export const blendedPrice = (model: IAiModel) =>
  model.cost_per_1m_input * 0.75 + model.cost_per_1m_output * 0.25

export const formatContext = (tokens: number) => {
  if (tokens >= 1_000_000) return `${Math.round(tokens / 100_000) / 10}M`
  return `${Math.round(tokens / 1000)}K`
}

export const formatPrice = (usd: number) => (usd < 0.1 ? `$${usd.toFixed(3)}` : `$${usd.toFixed(2)}`)

/** Returns a new array; callers pass computed props that must not be mutated. */
export const sortModels = (models: IAiModel[], key: SortKey): IAiModel[] => {
  const sorted = [...models]
  switch (key) {
    case 'context':
      return sorted.sort((a, b) => b.context_length - a.context_length)
    case 'name':
      return sorted.sort((a, b) => a.name.localeCompare(b.name))
    case 'power':
      return sorted.sort(
        (a, b) => TIER_RANK[a.tier] - TIER_RANK[b.tier] || blendedPrice(b) - blendedPrice(a),
      )
    case 'price':
      return sorted.sort((a, b) => blendedPrice(a) - blendedPrice(b))
    default:
      return sorted.sort(
        (a, b) =>
          Number(b.recommended) - Number(a.recommended) ||
          TIER_RANK[a.tier] - TIER_RANK[b.tier] ||
          blendedPrice(a) - blendedPrice(b),
      )
  }
}

export interface IModelFilters {
  search: string
  /** Empty means every provider. */
  providers: string[]
  requireVision: boolean
  requireTools: boolean
  requireReasoning: boolean
  recommendedOnly: boolean
  /** Max $/1M output tokens; null means no ceiling. */
  maxOutputCost: number | null
  /** Min context window in tokens; null means no floor. */
  minContext: number | null
}

export const createDefaultFilters = (): IModelFilters => ({
  search: '',
  providers: [],
  requireVision: false,
  requireTools: false,
  requireReasoning: false,
  recommendedOnly: false,
  maxOutputCost: null,
  minContext: null,
})

/**
 * Slider stops for the output-cost ceiling. Prices span $0–$600/1M with a $1.50
 * median, so a linear scale would bunch almost every model into the first pixel.
 */
export const COST_STEPS: (number | null)[] = [0, 0.5, 1, 2, 5, 10, 20, 50, 100, null]

/** Slider stops for the context floor. `null` (index 0) means no floor. */
export const CONTEXT_STEPS: (number | null)[] = [
  null,
  32_000,
  128_000,
  200_000,
  500_000,
  1_000_000,
]

const matchesSearch = (model: IAiModel, needle: string) =>
  model.name.toLowerCase().includes(needle) ||
  model.id.toLowerCase().includes(needle) ||
  model.provider.toLowerCase().includes(needle)

export const filterModels = (models: IAiModel[], filters: IModelFilters): IAiModel[] => {
  const needle = filters.search.trim().toLowerCase()
  const providers = new Set(filters.providers)

  return models.filter((model) => {
    if (needle && !matchesSearch(model, needle)) return false
    if (providers.size > 0 && !providers.has(model.provider)) return false
    if (filters.requireVision && !model.supports_vision) return false
    if (filters.requireTools && !model.supports_tools) return false
    if (filters.requireReasoning && !model.supports_reasoning) return false
    if (filters.recommendedOnly && !model.recommended) return false
    if (filters.maxOutputCost !== null && model.cost_per_1m_output > filters.maxOutputCost) {
      return false
    }
    if (filters.minContext !== null && model.context_length < filters.minContext) return false
    return true
  })
}

/** Providers present in the catalog, most models first, then alphabetical. */
export const providerCounts = (models: IAiModel[]): { provider: string; count: number }[] => {
  const counts = new Map<string, number>()
  for (const model of models) {
    counts.set(model.provider, (counts.get(model.provider) ?? 0) + 1)
  }
  return [...counts.entries()]
    .map(([provider, count]) => ({ provider, count }))
    .sort((a, b) => b.count - a.count || a.provider.localeCompare(b.provider))
}
