import { describe, expect, it } from 'vitest'
import type { IModelFilters } from './aiModelFormat'
import {
  blendedPrice,
  createDefaultFilters,
  filterModels,
  formatContext,
  formatPrice,
  providerCounts,
  sortModels,
} from './aiModelFormat'
import type { IAiModel } from '@/modules/workspace/types/workspaceConfig'

const model = (overrides: Partial<IAiModel> & Pick<IAiModel, 'id'>): IAiModel => ({
  name: overrides.id,
  provider: 'Acme',
  description: null,
  context_length: 128_000,
  cost_per_1m_input: 1,
  cost_per_1m_output: 4,
  tier: 'balanced',
  supports_vision: false,
  supports_tools: false,
  supports_reasoning: false,
  recommended: false,
  ...overrides,
})

/** Mirrors the user's headline query: vision + tools, output ≤ $10, cheapest first. */
const CHEAP_VISION_TOOLS = model({
  id: 'openai/gpt-4o-mini',
  name: 'GPT-4o Mini',
  provider: 'OpenAI',
  supports_vision: true,
  supports_tools: true,
  cost_per_1m_input: 0.15,
  cost_per_1m_output: 0.6,
  tier: 'fast',
})

const PRICEY_VISION_TOOLS = model({
  id: 'anthropic/claude-opus-4.8',
  name: 'Claude Opus 4.8',
  provider: 'Anthropic',
  supports_vision: true,
  supports_tools: true,
  cost_per_1m_input: 5,
  cost_per_1m_output: 25,
  tier: 'frontier',
})

const MID_VISION_TOOLS = model({
  id: 'google/gemini-2.5-flash',
  name: 'Gemini 2.5 Flash',
  provider: 'Google',
  supports_vision: true,
  supports_tools: true,
  cost_per_1m_input: 0.3,
  cost_per_1m_output: 2.5,
  recommended: true,
})

const TEXT_ONLY = model({
  id: 'deepseek/deepseek-v4-flash',
  name: 'DeepSeek V4 Flash',
  provider: 'DeepSeek',
  supports_tools: true,
  supports_reasoning: true,
  cost_per_1m_input: 0.09,
  cost_per_1m_output: 0.18,
  context_length: 1_048_576,
  tier: 'fast',
})

const ALL = [PRICEY_VISION_TOOLS, TEXT_ONLY, MID_VISION_TOOLS, CHEAP_VISION_TOOLS]

const withFilters = (overrides: Partial<IModelFilters>): IModelFilters => ({
  ...createDefaultFilters(),
  ...overrides,
})

describe('filterModels', () => {
  it('returns everything with default filters', () => {
    expect(filterModels(ALL, createDefaultFilters())).toHaveLength(4)
  })

  it('answers the vision + tools + max $10 output query', () => {
    const result = filterModels(
      ALL,
      withFilters({ requireVision: true, requireTools: true, maxOutputCost: 10 }),
    )

    expect(result.map((m) => m.id)).toEqual([MID_VISION_TOOLS.id, CHEAP_VISION_TOOLS.id])
  })

  it('treats maxOutputCost as inclusive', () => {
    const exactly = model({ id: 'edge/ten', cost_per_1m_output: 10 })
    expect(filterModels([exactly], withFilters({ maxOutputCost: 10 }))).toHaveLength(1)
    expect(filterModels([exactly], withFilters({ maxOutputCost: 5 }))).toHaveLength(0)
  })

  it('filters by capability flags', () => {
    expect(filterModels(ALL, withFilters({ requireReasoning: true }))).toEqual([TEXT_ONLY])
    expect(filterModels(ALL, withFilters({ recommendedOnly: true }))).toEqual([MID_VISION_TOOLS])
  })

  it('filters by provider, with an empty list meaning all providers', () => {
    expect(filterModels(ALL, withFilters({ providers: ['Google', 'OpenAI'] }))).toEqual([
      MID_VISION_TOOLS,
      CHEAP_VISION_TOOLS,
    ])
    expect(filterModels(ALL, withFilters({ providers: [] }))).toHaveLength(4)
  })

  it('filters by minimum context', () => {
    expect(filterModels(ALL, withFilters({ minContext: 1_000_000 }))).toEqual([TEXT_ONLY])
  })

  it('searches name, id, and provider case-insensitively', () => {
    expect(filterModels(ALL, withFilters({ search: 'gemini' }))).toEqual([MID_VISION_TOOLS])
    expect(filterModels(ALL, withFilters({ search: 'ANTHROPIC/' }))).toEqual([PRICEY_VISION_TOOLS])
    expect(filterModels(ALL, withFilters({ search: '  deepseek  ' }))).toEqual([TEXT_ONLY])
  })

  it('combines every predicate conjunctively', () => {
    const result = filterModels(
      ALL,
      withFilters({ requireVision: true, providers: ['OpenAI'], maxOutputCost: 1 }),
    )
    expect(result).toEqual([CHEAP_VISION_TOOLS])
  })
})

describe('sortModels', () => {
  it('does not mutate its input', () => {
    const input = [...ALL]
    sortModels(input, 'name')
    expect(input).toEqual(ALL)
  })

  it('sorts by blended price ascending', () => {
    const ids = sortModels(ALL, 'price').map((m) => m.id)
    expect(ids[0]).toBe(TEXT_ONLY.id)
    expect(ids.at(-1)).toBe(PRICEY_VISION_TOOLS.id)
  })

  it('sorts by power: tier first, then blended price descending', () => {
    const ids = sortModels(ALL, 'power').map((m) => m.id)
    expect(ids[0]).toBe(PRICEY_VISION_TOOLS.id)
    // Both remaining are 'fast'; the pricier one wins the tie-break.
    expect(ids.slice(2)).toEqual([CHEAP_VISION_TOOLS.id, TEXT_ONLY.id])
  })

  it('sorts by context descending', () => {
    expect(sortModels(ALL, 'context')[0]).toBe(TEXT_ONLY)
  })

  it('sorts by name alphabetically', () => {
    // localeCompare is case-insensitive, so "Gemini" precedes "GPT-4o".
    expect(sortModels(ALL, 'name').map((m) => m.name)).toEqual([
      'Claude Opus 4.8',
      'DeepSeek V4 Flash',
      'Gemini 2.5 Flash',
      'GPT-4o Mini',
    ])
  })

  it('puts recommended models first by default', () => {
    expect(sortModels(ALL, 'recommended')[0]).toBe(MID_VISION_TOOLS)
  })
})

describe('formatPrice', () => {
  it('uses three decimals below ten cents', () => {
    expect(formatPrice(0.048)).toBe('$0.048')
    expect(formatPrice(0)).toBe('$0.000')
  })

  it('uses two decimals from ten cents up', () => {
    expect(formatPrice(0.1)).toBe('$0.10')
    expect(formatPrice(25)).toBe('$25.00')
  })
})

describe('formatContext', () => {
  it('renders millions with one decimal', () => {
    expect(formatContext(1_048_576)).toBe('1M')
    expect(formatContext(1_500_000)).toBe('1.5M')
  })

  it('renders thousands below a million', () => {
    expect(formatContext(128_000)).toBe('128K')
    expect(formatContext(999_999)).toBe('1000K')
  })
})

describe('blendedPrice', () => {
  it('weights input tokens at 75%', () => {
    expect(blendedPrice(model({ id: 'x', cost_per_1m_input: 4, cost_per_1m_output: 8 }))).toBe(5)
  })
})

describe('providerCounts', () => {
  it('orders by count desc, then name', () => {
    const models = [
      model({ id: 'a', provider: 'Zeta' }),
      model({ id: 'b', provider: 'Alpha' }),
      model({ id: 'c', provider: 'Alpha' }),
      model({ id: 'd', provider: 'Beta' }),
    ]
    expect(providerCounts(models)).toEqual([
      { provider: 'Alpha', count: 2 },
      { provider: 'Beta', count: 1 },
      { provider: 'Zeta', count: 1 },
    ])
  })
})
