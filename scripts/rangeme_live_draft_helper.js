const fs = require("fs");
const { chromium } = require("playwright");

const creds = JSON.parse(fs.readFileSync(0, "utf8"));
const productUrl = "https://app.rangeme.com/suppliers/koval-distillery-298212/product_form/5920811/basics";

async function login(page) {
  await page.goto("https://app.rangeme.com/login", { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.locator("input[type=email], input[name*=email i], input[id*=email i]").first().fill(creds.email);
  await page.locator("input[type=password], input[name*=password i], input[id*=password i]").first().fill(creds.password);
  await Promise.all([
    page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {}),
    page.locator('button:has-text("Log in"), button:has-text("Login"), input[type=submit]').first().click(),
  ]);
  await page.waitForTimeout(3000);
}

async function main() {
  const mode = process.argv[2] || "inspect";
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
  const page = await context.newPage();
  const out = { ok: false, mode };
  try {
    await login(page);
    await page.goto(productUrl, { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForTimeout(3000);

    if (mode === "cleanup") {
      // Remove the certification chips selected by the first draft pass. They were not source-confirmed
      // to match the exact KOVAL certificates and should remain in the Google Doc as attachment questions.
      const chipTexts = ["Australia Organic Certified - OFC", "Certified Kosher - 1K-Kosher"];
      for (const text of chipTexts) {
        const chip = page.locator(`text=${text}`).first();
        if (await chip.count()) {
          const box = await chip.boundingBox();
          if (box) {
            await page.mouse.click(box.x + box.width + 8, box.y + box.height / 2).catch(() => {});
            await page.waitForTimeout(1000);
          }
        }
      }
      // RangeMe did not find "Bourbon" via category search. Leave it blank rather than forcing a wrong category.
      await page.waitForTimeout(5000);
    }

    const body = await page.locator("body").innerText({ timeout: 10000 });
    out.url = page.url();
    out.saved = /All changes saved/i.test(body);
    out.publishVisible = /Publish Product/i.test(body);
    out.nameVisible = /KOVAL Bourbon/i.test(body);
    out.certificationTextStillVisible = /Australia Organic Certified|Certified Kosher - 1K-Kosher/i.test(body);
    out.categoryBlank = /Select category/i.test(body) || /No categories found/i.test(body);
    out.reviewText = body.slice(0, 5000);
    out.ok = true;
    console.log(JSON.stringify(out, null, 2));
  } catch (error) {
    out.error = String(error).slice(0, 700);
    out.url = page.url();
    console.log(JSON.stringify(out, null, 2));
  } finally {
    await browser.close();
  }
}

main();
