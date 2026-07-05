import { expect, test } from '../fixtures/auth'

test.describe('E2E - Items', () => {
  // Helper to create a container first (items need a parent container)
  async function createContainer(page: typeof test extends (typeof test)['_type'] ? never : Parameters<Parameters<typeof test>[1]>[0]['authenticatedPage']) {
    await page.goto('/gear/new')
    const containerName = `E2E Item Test Container ${Date.now()}`
    await page.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', containerName)
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/gear\/[^/]+$/, { timeout: 10000 })

    // Extract container ID from URL
    const url = page.url()
    const containerId = url.split('/gear/')[1]?.split('/')[0]?.split('?')[0]
    return { containerName, containerId }
  }

  test('should create item in container via form', async ({ authenticatedPage }) => {
    // Create container first
    const { containerId } = await createContainer(authenticatedPage)

    // Click add item button
    await authenticatedPage.click('button:has-text("Add Item"), button:has-text("Dodaj"), a[href*="/items/new"]')

    // Wait for item form
    await authenticatedPage.waitForURL(`**/gear/${containerId}/items/new`, { timeout: 5000 })

    // Fill item form
    const itemName = `E2E Test Item ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', itemName)

    // Submit form
    await authenticatedPage.click('button[type="submit"]')

    // Wait for redirect to item detail
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/items\/[^/]+$/, { timeout: 10000 })

    // Verify item name is displayed
    await expect(authenticatedPage.locator(`text=${itemName}`)).toBeVisible({ timeout: 5000 })
  })

  test('should edit item via form', async ({ authenticatedPage }) => {
    // Create container and item first
    const { containerId } = await createContainer(authenticatedPage)

    // Create item
    await authenticatedPage.click('button:has-text("Add Item"), button:has-text("Dodaj"), a[href*="/items/new"]')
    await authenticatedPage.waitForURL(`**/gear/${containerId}/items/new`, { timeout: 5000 })

    const originalName = `E2E Edit Item ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', originalName)
    await authenticatedPage.click('button[type="submit"]')

    // Wait for item detail page
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/items\/[^/]+$/, { timeout: 10000 })

    // Click edit button
    await authenticatedPage.click('button:has-text("Edit"), button:has-text("Edytuj"), a[href*="/edit"]')

    // Wait for edit form
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/items\/[^/]+\/edit/, { timeout: 5000 })

    // Update name
    const updatedName = `${originalName} - Updated`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', updatedName)

    // Submit form
    await authenticatedPage.click('button[type="submit"]')

    // Wait for redirect back to detail page
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/items\/[^/]+$/, { timeout: 10000 })

    // Verify updated name is displayed
    await expect(authenticatedPage.locator(`text=${updatedName}`)).toBeVisible({ timeout: 5000 })
  })

  test('should delete item with confirmation', async ({ authenticatedPage }) => {
    // Create container and item first
    const { containerId } = await createContainer(authenticatedPage)

    // Create item
    await authenticatedPage.click('button:has-text("Add Item"), button:has-text("Dodaj"), a[href*="/items/new"]')
    await authenticatedPage.waitForURL(`**/gear/${containerId}/items/new`, { timeout: 5000 })

    const itemName = `E2E Delete Item ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', itemName)
    await authenticatedPage.click('button[type="submit"]')

    // Wait for item detail page
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/items\/[^/]+$/, { timeout: 10000 })

    // Click delete button
    await authenticatedPage.click('button:has-text("Delete"), button:has-text("Usuń")')

    // Wait for and confirm deletion dialog
    await authenticatedPage.waitForSelector('[role="alertdialog"], [role="dialog"]', { timeout: 5000 })
    await authenticatedPage.click(
      'button:has-text("Delete"), button:has-text("Confirm"), button:has-text("Usuń"), button:has-text("Potwierdź")',
    )

    // Wait for redirect to container detail
    await authenticatedPage.waitForURL(`**/gear/${containerId}`, { timeout: 10000 })

    // Verify item is no longer visible
    await expect(authenticatedPage.locator(`text=${itemName}`)).not.toBeVisible({ timeout: 5000 })
  })

  test('should display items in container detail page', async ({ authenticatedPage }) => {
    // Create container and multiple items
    const { containerId } = await createContainer(authenticatedPage)

    // Create first item
    await authenticatedPage.click('button:has-text("Add Item"), button:has-text("Dodaj"), a[href*="/items/new"]')
    await authenticatedPage.waitForURL(`**/gear/${containerId}/items/new`, { timeout: 5000 })
    const item1Name = `E2E List Item 1 ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', item1Name)
    await authenticatedPage.click('button[type="submit"]')
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/items\/[^/]+$/, { timeout: 10000 })

    // Go back to container
    await authenticatedPage.goto(`/gear/${containerId}`)
    await authenticatedPage.waitForLoadState('networkidle')

    // Create second item
    await authenticatedPage.click('button:has-text("Add Item"), button:has-text("Dodaj"), a[href*="/items/new"]')
    await authenticatedPage.waitForURL(`**/gear/${containerId}/items/new`, { timeout: 5000 })
    const item2Name = `E2E List Item 2 ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', item2Name)
    await authenticatedPage.click('button[type="submit"]')
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/items\/[^/]+$/, { timeout: 10000 })

    // Go back to container and verify both items are visible
    await authenticatedPage.goto(`/gear/${containerId}`)
    await authenticatedPage.waitForLoadState('networkidle')

    await expect(authenticatedPage.locator(`text=${item1Name}`)).toBeVisible({ timeout: 5000 })
    await expect(authenticatedPage.locator(`text=${item2Name}`)).toBeVisible({ timeout: 5000 })
  })
})
