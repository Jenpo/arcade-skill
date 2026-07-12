const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/visual",
  outputDir: "./growth/reports/visual",
  snapshotPathTemplate: "{testDir}/../visual-snapshots/{arg}{ext}",
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["line"], ["html", { outputFolder: "growth/reports/visual-html", open: "never" }]] : "line",
  use: {
    baseURL: "http://127.0.0.1:4173",
    browserName: "chromium",
    colorScheme: "light",
    locale: "en-US",
    timezoneId: "UTC",
  },
  webServer: {
    command: "python3 -m http.server 4173 --directory dist",
    url: "http://127.0.0.1:4173/scenarios/",
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
});
