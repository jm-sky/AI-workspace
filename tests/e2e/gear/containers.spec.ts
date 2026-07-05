import { expect, test } from '../fixtures/auth'

test.describe('E2E - Containers', () => {
  test('should display containers list page', async ({ authenticatedPage }) => {
    // Navigate to containers list
    await authenticatedPage.goto('/gear')

    // Wait for page to load
    await authenticatedPage.waitForLoadState('networkidle')

    // Verify page header is visible
    await expect(authenticatedPage.locator('h1, [data-testid="page-title"]').first()).toBeVisible()
  })

  test('should create new container via form', async ({ authenticatedPage }) => {
    // Navigate to containers list
    await authenticatedPage.goto('/gear')

    // Click create button
    await authenticatedPage.click('button:has-text("Create"), button:has-text("Dodaj"), a[href*="/new"]')

    // Wait for form page
    await authenticatedPage.waitForURL('**/gear/new', { timeout: 5000 })

    // Fill container form
    const containerName = `E2E Test Container ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', containerName)

    // Submit form
    await authenticatedPage.click('button[type="submit"]')

    // Wait for redirect to container detail
    await authenticatedPage.waitForURL(/\/gear\/[^/]+$/, { timeout: 10000 })

    // Verify container name is displayed
    await expect(authenticatedPage.locator(`text=${containerName}`)).toBeVisible({ timeout: 5000 })
  })

  test('should edit container via form', async ({ authenticatedPage }) => {
    // First create a container
    await authenticatedPage.goto('/gear/new')

    const originalName = `E2E Edit Test ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', originalName)
    await authenticatedPage.click('button[type="submit"]')

    // Wait for detail page
    await authenticatedPage.waitForURL(/\/gear\/[^/]+$/, { timeout: 10000 })

    // Click edit button
    await authenticatedPage.click('button:has-text("Edit"), button:has-text("Edytuj"), a[href*="/edit"]')

    // Wait for edit form
    await authenticatedPage.waitForURL(/\/gear\/[^/]+\/edit/, { timeout: 5000 })

    // Update name
    const updatedName = `${originalName} - Updated`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', updatedName)

    // Submit form
    await authenticatedPage.click('button[type="submit"]')

    // Wait for redirect back to detail page
    await authenticatedPage.waitForURL(/\/gear\/[^/]+$/, { timeout: 10000 })

    // Verify updated name is displayed
    await expect(authenticatedPage.locator(`text=${updatedName}`)).toBeVisible({ timeout: 5000 })
  })

  test('should delete container with confirmation', async ({ authenticatedPage }) => {
    // First create a container
    await authenticatedPage.goto('/gear/new')

    const containerName = `E2E Delete Test ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', containerName)
    await authenticatedPage.click('button[type="submit"]')

    // Wait for detail page
    await authenticatedPage.waitForURL(/\/gear\/[^/]+$/, { timeout: 10000 })

    // Click delete button
    await authenticatedPage.click('button:has-text("Delete"), button:has-text("Usuń")')

    // Wait for and confirm deletion dialog
    await authenticatedPage.waitForSelector('[role="alertdialog"], [role="dialog"]', { timeout: 5000 })
    await authenticatedPage.click(
      'button:has-text("Delete"), button:has-text("Confirm"), button:has-text("Usuń"), button:has-text("Potwierdź")',
    )

    // Wait for redirect to containers list
    await authenticatedPage.waitForURL('**/gear', { timeout: 10000 })

    // Verify container is no longer in the list
    await expect(authenticatedPage.locator(`text=${containerName}`)).not.toBeVisible({ timeout: 5000 })
  })

  test('should navigate from containers list to container detail', async ({ authenticatedPage }) => {
    // First create a container
    await authenticatedPage.goto('/gear/new')

    const containerName = `E2E Navigation Test ${Date.now()}`
    await authenticatedPage.fill('input[placeholder*="name"], input[name="name"], input:first-of-type', containerName)
    await authenticatedPage.click('button[type="submit"]')

    // Wait for detail page and get container ID from URL
    await authenticatedPage.waitForURL(/\/gear\/[^/]+$/, { timeout: 10000 })
    const detailUrl = authenticatedPage.url()

    // Go back to containers list
    await authenticatedPage.goto('/gear')
    await authenticatedPage.waitForLoadState('networkidle')

    // Click on the container card/link
    await authenticatedPage.click(`text=${containerName}`)

    // Verify we're back on detail page
    await authenticatedPage.waitForURL(detailUrl, { timeout: 10000 })
    await expect(authenticatedPage.locator(`text=${containerName}`)).toBeVisible()
  })
})
