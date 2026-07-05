import { expect, test } from '../fixtures/api'
import { createContainer, createItem, deleteItem, getItem, getItems, updateItem } from '../fixtures/test-data'

test.describe('API - Items', () => {
  test('should create item in container via API', async ({ apiContext }) => {
    // Create container first
    const container = await createContainer(apiContext, {
      name: 'Test Container',
      containerType: 'backpack',
    })

    // Create item in container
    const item = await createItem(apiContext, {
      name: 'Test Item',
      parentItemId: container.id,
      category: 'tools',
    })

    expect(item).toHaveProperty('id')
    expect(item.itemType).toBe('item')
    expect(item.name).toBe('Test Item')
    expect(item.parentItemId).toBe(container.id)
    expect(item.category).toBe('tools')

    // Cleanup
    await deleteItem(apiContext, item.id)
    await deleteItem(apiContext, container.id)
  })

  test('should list items in container via API', async ({ apiContext }) => {
    // Create container
    const container = await createContainer(apiContext, {
      name: 'Container for Items',
      containerType: 'backpack',
    })

    // Create items
    const item1 = await createItem(apiContext, {
      name: 'Item 1',
      parentItemId: container.id,
      category: 'tools',
    })
    const item2 = await createItem(apiContext, {
      name: 'Item 2',
      parentItemId: container.id,
      category: 'water',
    })

    // Get items in container
    const items = await getItems(apiContext, {
      itemType: 'item',
      parentItemId: container.id,
    })

    expect(items.length).toBeGreaterThanOrEqual(2)
    const foundItem1 = items.find((i: { id: string }) => i.id === item1.id)
    const foundItem2 = items.find((i: { id: string }) => i.id === item2.id)

    expect(foundItem1).toBeDefined()
    expect(foundItem2).toBeDefined()
    expect(foundItem1?.name).toBe('Item 1')
    expect(foundItem2?.name).toBe('Item 2')

    // Cleanup
    await deleteItem(apiContext, item1.id)
    await deleteItem(apiContext, item2.id)
    await deleteItem(apiContext, container.id)
  })

  test('should get item details via API', async ({ apiContext }) => {
    // Create container
    const container = await createContainer(apiContext, {
      name: 'Container',
      containerType: 'backpack',
    })

    // Create item
    const item = await createItem(apiContext, {
      name: 'Detail Test Item',
      parentItemId: container.id,
      category: 'tools',
      quantity: 2,
      weight: 100,
      weightUnit: 'g',
    })

    const details = await getItem(apiContext, item.id)

    expect(details.id).toBe(item.id)
    expect(details.name).toBe('Detail Test Item')
    expect(details.category).toBe('tools')
    expect(details.quantity).toBe(2)
    expect(details.weight).toBe(100)
    expect(details.weightUnit).toBe('g')

    // Cleanup
    await deleteItem(apiContext, item.id)
    await deleteItem(apiContext, container.id)
  })

  test('should update item via API', async ({ apiContext }) => {
    // Create container
    const container = await createContainer(apiContext, {
      name: 'Container',
      containerType: 'backpack',
    })

    // Create item
    const item = await createItem(apiContext, {
      name: 'Original Item Name',
      parentItemId: container.id,
      category: 'tools',
    })

    // Update item
    const updated = await updateItem(apiContext, item.id, {
      name: 'Updated Item Name',
      quantity: 3,
      status: 'toBuy',
    })

    expect(updated.name).toBe('Updated Item Name')
    expect(updated.quantity).toBe(3)
    expect(updated.status).toBe('toBuy')

    // Cleanup
    await deleteItem(apiContext, item.id)
    await deleteItem(apiContext, container.id)
  })

  test('should delete item via API', async ({ apiContext }) => {
    // Create container
    const container = await createContainer(apiContext, {
      name: 'Container',
      containerType: 'backpack',
    })

    // Create item
    const item = await createItem(apiContext, {
      name: 'To Be Deleted',
      parentItemId: container.id,
      category: 'tools',
    })

    // Delete item
    await deleteItem(apiContext, item.id)

    // Verify it's deleted
    const response = await apiContext.get(`/api/gear/v2/items/${item.id}`)
    expect(response.status()).toBe(404)

    // Cleanup
    await deleteItem(apiContext, container.id)
  })

  test('should filter items by status', async ({ apiContext }) => {
    // Create container
    const container = await createContainer(apiContext, {
      name: 'Container',
      containerType: 'backpack',
    })

    // Create items with different statuses
    const ownedItem = await createItem(apiContext, {
      name: 'Owned Item',
      parentItemId: container.id,
      category: 'tools',
      status: 'owned',
    })
    const toBuyItem = await createItem(apiContext, {
      name: 'To Buy Item',
      parentItemId: container.id,
      category: 'water',
      status: 'toBuy',
    })

    // Get items with status filter
    const response = await apiContext.get(
      `/api/gear/v2/items?itemType=item&parentItemId=${container.id}&status=owned`,
    )
    const ownedItems = await response.json()

    const foundOwned = ownedItems.find((i: { id: string }) => i.id === ownedItem.id)
    const foundToBuy = ownedItems.find((i: { id: string }) => i.id === toBuyItem.id)

    expect(foundOwned).toBeDefined()
    expect(foundToBuy).toBeUndefined()

    // Cleanup
    await deleteItem(apiContext, ownedItem.id)
    await deleteItem(apiContext, toBuyItem.id)
    await deleteItem(apiContext, container.id)
  })
})
