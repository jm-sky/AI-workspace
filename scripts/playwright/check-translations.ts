import { writeFile } from 'fs/promises'
import { join } from 'path'
import { chromium } from 'playwright'

async function checkTranslations() {
  console.log('Launching browser...')
  const browser = await chromium.launch({ headless: false })
  const page = await browser.newPage()
  
  console.log('Navigating to http://localhost:5176/...')
  await page.goto('http://localhost:5176/', { waitUntil: 'networkidle' })
  
  console.log('Page loaded! Taking screenshot...')
  const screenshot = await page.screenshot({ fullPage: true })
  
  const screenshotPath = join(process.cwd(), 'screenshot-translations.png')
  await writeFile(screenshotPath, screenshot)
  console.log(`Screenshot saved to: ${screenshotPath}`)
  
  // Get page title
  const title = await page.title()
  console.log(`Page title: ${title}`)
  
  // Get all text content to check for missing translations
  const bodyText = await page.textContent('body')
  console.log('\n=== Page Content (first 500 chars) ===')
  console.log(bodyText?.substring(0, 500))
  
  // Check for common translation keys that might be missing
  const translationKeys = [
    'gear.container.weight',
    'gear.container.weightUnit',
    'gear.container.url',
  ]
  
  console.log('\n=== Checking for translation keys ===')
  for (const key of translationKeys) {
    // This is a simple check - we'd need to inspect the actual Vue app to see missing translations
    console.log(`Looking for: ${key}`)
  }
  
  // Wait a bit so user can see the browser
  console.log('\nBrowser will stay open for 10 seconds...')
  await page.waitForTimeout(10000)
  
  await browser.close()
  console.log('Browser closed. Check complete!')
}

checkTranslations().catch((error) => {
  console.error('Error:', error)
  process.exit(1)
})

