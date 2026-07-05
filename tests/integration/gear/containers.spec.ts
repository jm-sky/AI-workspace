import { expect, test } from '../fixtures/api'
import { createContainer, deleteItem, getItem, getItems, updateItem } from '../fixtures/test-data'

test.describe('API - Containers', () => {
  test('should create container via API', async ({ apiContext }) => {
    const container = await createContainer(apiContext, {
      name: 'Test Backpack',
      containerType: 'backpack',
    })

    expect(container).toHaveProperty('id')
    expect(container.itemType).toBe('container')
    expect(container.name).toBe('Test Backpack')
    expect(container.containerType).toBe('backpack')

    // Cleanup
    await deleteItem(apiContext, container.id)
  })

  test('should list containers via API', async ({ apiContext }) => {
    // Create test containers
    const container1 = await createContainer(apiContext, {
      name: 'Container 1',
      containerType: 'backpack',
    })
    const container2 = await createContainer(apiContext, {
      name: 'Container 2',
      containerType: 'bag',
    })

    // Get all containers
    const containers = await getItems(apiContext, { itemType: 'container' })

    expect(containers.length).toBeGreaterThanOrEqual(2)
    const foundContainer1 = containers.find((c: { id: string }) => c.id === container1.id)
    const foundContainer2 = containers.find((c: { id: string }) => c.id === container2.id)

    expect(foundContainer1).toBeDefined()
    expect(foundContainer2).toBeDefined()
    expect(foundContainer1?.name).toBe('Container 1')
    expect(foundContainer2?.name).toBe('Container 2')

    // Cleanup
    await deleteItem(apiContext, container1.id)
    await deleteItem(apiContext, container2.id)
  })

  test('should get container details via API', async ({ apiContext }) => {
    const container = await createContainer(apiContext, {
      name: 'Detail Test Container',
      containerType: 'backpack',
      description: 'Test description',
    })

    const details = await getItem(apiContext, container.id)

    expect(details.id).toBe(container.id)
    expect(details.name).toBe('Detail Test Container')
    expect(details.description).toBe('Test description')
    expect(details.itemType).toBe('container')

    // Cleanup
    await deleteItem(apiContext, container.id)
  })

  test('should update container via API', async ({ apiContext }) => {
    const container = await createContainer(apiContext, {
      name: 'Original Name',
      containerType: 'backpack',
    })

    // Update container
    const updated = await updateItem(apiContext, container.id, {
      name: 'Updated Name',
      description: 'Updated description',
    })

    expect(updated.name).toBe('Updated Name')
    expect(updated.description).toBe('Updated description')

    // Cleanup
    await deleteItem(apiContext, container.id)
  })

  test('should delete container via API', async ({ apiContext }) => {
    const container = await createContainer(apiContext, {
      name: 'To Be Deleted',
      containerType: 'backpack',
    })

    // Delete container
    await deleteItem(apiContext, container.id)

    // Verify it's deleted
    const response = await apiContext.get(`/api/gear/v2/items/${container.id}`)
    expect(response.status()).toBe(404)
  })
})
