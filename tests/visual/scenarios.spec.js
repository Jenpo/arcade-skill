const { test, expect } = require("@playwright/test");

const viewports = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
];

for (const viewport of viewports) {
  test(`scenarios ${viewport.name} visual contract`, async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    await page.goto("/scenarios/", { waitUntil: "networkidle" });

    await expect(page.locator("main")).toBeVisible();
    await expect(page.locator(".cabinet")).toBeVisible();
    await expect(page.locator(".avatar")).toBeVisible();

    const overflow = await page.evaluate(() => ({
      viewport: window.innerWidth,
      document: document.documentElement.scrollWidth,
    }));
    expect(overflow.document).toBeLessThanOrEqual(overflow.viewport);

    if (viewport.name === "mobile") {
      const cabinetTop = await page.locator(".cabinet").evaluate((node) => node.getBoundingClientRect().top);
      const titleTop = await page.locator("h1").evaluate((node) => node.getBoundingClientRect().top);
      expect(cabinetTop).toBeLessThan(titleTop);
    }

    await page.keyboard.press("Tab");
    const focusStyle = await page.evaluate(() => {
      const node = document.activeElement;
      const style = window.getComputedStyle(node);
      return { tag: node.tagName, width: parseFloat(style.outlineWidth) || 0 };
    });
    expect(focusStyle.tag).toBe("A");
    expect(focusStyle.width).toBeGreaterThan(0);

    await expect(page).toHaveScreenshot(`scenarios-${viewport.name}.png`, {
      animations: "disabled",
      fullPage: true,
      maxDiffPixelRatio: 0.03,
      threshold: 0.25,
    });
    await context.close();
  });
}
