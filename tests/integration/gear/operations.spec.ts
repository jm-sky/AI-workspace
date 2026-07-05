import { expect, test } from '../fixtures/api'
import { createContainer, createItem, deleteItem, getItems } from '../fixtures/test-data'

test.describe('API - Operations', () => {
  test('should move item between containers', async ({ apiContext }) => {
    // Create containers
    const container1 = await createContainer(apiContext, {
      name: 'Container 1',
      containerType: 'backpack',
    })
    const container2 = await createContainer(apiContext, {
      name: 'Container 2',
      containerType: 'bag',
    })

    // Create item in container1
    const item = await createItem(apiContext, {
      name: 'Movable Item',
      parentItemId: container1.id,
      category: 'tools',
    })

    // Move item to container2
    const response = await apiContext.patch(`/api/gear/v2/items/${item.id}/move?targetParentId=${container2.id}`)

    expect(response.ok()).toBeTruthy()
    const moved = await response.json()

    expect(moved.parentItemId).toBe(container2.id)

    // Verify item is in container2
    const itemsInContainer2 = await getItems(apiContext, {
      itemType: 'item',
      parentItemId: container2.id,
    })

    const foundItem = itemsInContainer2.find((i: { id: string }) => i.id === item.id)
    expect(foundItem).toBeDefined()

    // Cleanup
    await deleteItem(apiContext, item.id)
    await deleteItem(apiContext, container1.id)
    await deleteItem(apiContext, container2.id)
  })

  test('should delete container with items (cascade)', async ({ apiContext }) => {
    // Create container
    const container = await createContainer(apiContext, {
      name: 'Container with Items',
      containerType: 'backpack',
    })

    // Create items in container
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

    // Delete container
    await deleteItem(apiContext, container.id)

    // Verify container is deleted
    const containerResponse = await apiContext.get(`/api/gear/v2/items/${container.id}`)
    expect(containerResponse.status()).toBe(404)

    // Verify items are also deleted (cascade)
    const item1Response = await apiContext.get(`/api/gear/v2/items/${item1.id}`)
    expect(item1Response.status()).toBe(404)

    const item2Response = await apiContext.get(`/api/gear/v2/items/${item2.id}`)
    expect(item2Response.status()).toBe(404)
  })

  test('should prevent moving container to itself', async ({ apiContext }) => {
    // Create container
    const container = await createContainer(apiContext, {
      name: 'Self Container',
      containerType: 'backpack',
    })

    // Try to move container to itself (should fail)
    const response = await apiContext.patch(`/api/gear/v2/items/${container.id}/move?targetParentId=${container.id}`)

    // Should return error (400 or 422)
    expect([400, 422]).toContain(response.status())

    // Cleanup
    await deleteItem(apiContext, container.id)
  })
})
