import { expect, test } from '../fixtures/api'
import { createContainer, createItem, deleteItem, getItems } from '../fixtures/test-data'

test.describe('API - Nesting', () => {
  test('should nest container in container (backpack → box)', async ({ apiContext }) => {
    // Create parent container (backpack)
    const backpack = await createContainer(apiContext, {
      name: 'Backpack',
      containerType: 'backpack',
    })

    // Create nested container (box)
    const box = await createContainer(apiContext, {
      name: 'Box',
      containerType: 'box',
      parentItemId: backpack.id,
    })

    expect(box.parentItemId).toBe(backpack.id)
    expect(box.itemType).toBe('container')

    // Verify nesting via API
    const children = await getItems(apiContext, {
      itemType: 'container',
      parentItemId: backpack.id,
    })

    const foundBox = children.find((c: { id: string }) => c.id === box.id)
    expect(foundBox).toBeDefined()
    expect(foundBox?.name).toBe('Box')

    // Cleanup
    await deleteItem(apiContext, box.id)
    await deleteItem(apiContext, backpack.id)
  })

  test('should nest item in container (backpack → cup)', async ({ apiContext }) => {
    // Create container (backpack)
    const backpack = await createContainer(apiContext, {
      name: 'Backpack',
      containerType: 'backpack',
    })

    // Create item in container (cup)
    const cup = await createItem(apiContext, {
      name: 'Cup',
      parentItemId: backpack.id,
      category: 'tools',
    })

    expect(cup.parentItemId).toBe(backpack.id)
    expect(cup.itemType).toBe('item')

    // Verify nesting via API
    const items = await getItems(apiContext, {
      itemType: 'item',
      parentItemId: backpack.id,
    })

    const foundCup = items.find((i: { id: string }) => i.id === cup.id)
    expect(foundCup).toBeDefined()
    expect(foundCup?.name).toBe('Cup')

    // Cleanup
    await deleteItem(apiContext, cup.id)
    await deleteItem(apiContext, backpack.id)
  })

  test('should nest item in nested container (backpack → box → matches)', async ({ apiContext }) => {
    // Create parent container (backpack)
    const backpack = await createContainer(apiContext, {
      name: 'Backpack',
      containerType: 'backpack',
    })

    // Create nested container (box) in backpack
    const box = await createContainer(apiContext, {
      name: 'Box',
      containerType: 'box',
      parentItemId: backpack.id,
    })

    // Create item (matches) in box
    const matches = await createItem(apiContext, {
      name: 'Matches',
      parentItemId: box.id,
      category: 'tools',
    })

    expect(matches.parentItemId).toBe(box.id)
    expect(box.parentItemId).toBe(backpack.id)

    // Verify nesting structure
    const boxItems = await getItems(apiContext, {
      itemType: 'item',
      parentItemId: box.id,
    })

    const foundMatches = boxItems.find((i: { id: string }) => i.id === matches.id)
    expect(foundMatches).toBeDefined()
    expect(foundMatches?.name).toBe('Matches')

    // Cleanup
    await deleteItem(apiContext, matches.id)
    await deleteItem(apiContext, box.id)
    await deleteItem(apiContext, backpack.id)
  })
})
