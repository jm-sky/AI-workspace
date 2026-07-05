import type { APIRequestContext } from '@playwright/test'

export interface CreateContainerData {
  name: string
  containerType?: string
  description?: string
  weight?: number
  weightUnit?: 'g' | 'kg' | 'oz' | 'lb'
  parentItemId?: string | null
}

export interface CreateItemData {
  name: string
  parentItemId: string
  category?: string
  quantity?: number
  weight?: number
  weightUnit?: 'g' | 'kg' | 'oz' | 'lb'
  status?: 'owned' | 'missing' | 'toBuy'
  priority?: 'low' | 'medium' | 'high'
}

/**
 * Create a container via API
 */
export async function createContainer(api: APIRequestContext, data: CreateContainerData) {
  const response = await api.post('/api/gear/v2/items', {
    data: {
      itemType: 'container',
      name: data.name,
      containerType: data.containerType || 'backpack',
      description: data.description,
      weight: data.weight,
      weightUnit: data.weightUnit,
      parentItemId: data.parentItemId === null ? null : data.parentItemId,
    },
  })

  if (!response.ok()) {
    const errorText = await response.text()
    throw new Error(`Failed to create container: ${response.status()} ${errorText}`)
  }

  return await response.json()
}

/**
 * Create an item via API
 */
export async function createItem(api: APIRequestContext, data: CreateItemData) {
  const response = await api.post('/api/gear/v2/items', {
    data: {
      itemType: 'item',
      name: data.name,
      parentItemId: data.parentItemId,
      category: data.category || 'tools',
      quantity: data.quantity || 1,
      weight: data.weight,
      weightUnit: data.weightUnit,
      status: data.status || 'owned',
      priority: data.priority || 'medium',
    },
  })

  if (!response.ok()) {
    const errorText = await response.text()
    throw new Error(`Failed to create item: ${response.status()} ${errorText}`)
  }

  return await response.json()
}

/**
 * Update an item via API
 */
export async function updateItem(api: APIRequestContext, itemId: string, data: Partial<CreateContainerData & CreateItemData>) {
  const response = await api.patch(`/api/gear/v2/items/${itemId}`, {
    data,
  })

  if (!response.ok()) {
    const errorText = await response.text()
    throw new Error(`Failed to update item: ${response.status()} ${errorText}`)
  }

  return await response.json()
}

/**
 * Delete an item via API
 */
export async function deleteItem(api: APIRequestContext, itemId: string) {
  const response = await api.delete(`/api/gear/v2/items/${itemId}`)

  if (!response.ok()) {
    const errorText = await response.text()
    throw new Error(`Failed to delete item: ${response.status()} ${errorText}`)
  }

  return response.status() === 204 ? null : await response.json()
}

/**
 * Get items with optional filters
 */
export async function getItems(
  api: APIRequestContext,
  filters?: {
    itemType?: 'container' | 'item' | 'all'
    parentItemId?: string | null
    isPublic?: boolean
    favorite?: boolean
  },
) {
  const params = new URLSearchParams()

  if (filters?.itemType) {
    params.append('itemType', filters.itemType)
  }
  if (filters?.parentItemId !== undefined) {
    params.append('parentItemId', filters.parentItemId === null ? 'null' : filters.parentItemId)
  }
  if (filters?.isPublic !== undefined) {
    params.append('isPublic', String(filters.isPublic))
  }
  if (filters?.favorite !== undefined) {
    params.append('favorite', String(filters.favorite))
  }

  const response = await api.get(`/api/gear/v2/items?${params.toString()}`)

  if (!response.ok()) {
    const errorText = await response.text()
    throw new Error(`Failed to get items: ${response.status()} ${errorText}`)
  }

  return await response.json()
}

/**
 * Get item by ID
 */
export async function getItem(api: APIRequestContext, itemId: string) {
  const response = await api.get(`/api/gear/v2/items/${itemId}`)

  if (!response.ok()) {
    const errorText = await response.text()
    throw new Error(`Failed to get item: ${response.status()} ${errorText}`)
  }

  return await response.json()
}
