const fs = require("fs");
const { chromium } = require("playwright");

const creds = JSON.parse(fs.readFileSync(0, "utf8"));
const startUrl = process.argv[3] || "https://app.rangeme.com/suppliers/koval-distillery-298212/brands/341187";

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

async function summarizePage(page) {
  const body = await page.locator("body").innerText({ timeout: 10000 });
  const links = await page.locator("a").evaluateAll((nodes) =>
    nodes
      .map((a) => ({
        text: (a.innerText || a.textContent || "").trim().replace(/\s+/g, " ").slice(0, 120),
        href: a.href,
      }))
      .filter((x) => x.text || x.href)
      .slice(0, 120)
  );
  const buttons = await page.locator("button, input[type=button], input[type=submit]").evaluateAll((nodes) =>
    nodes
      .map((b) => ({
        text: (b.innerText || b.value || b.getAttribute("aria-label") || "").trim().replace(/\s+/g, " ").slice(0, 120),
        disabled: b.disabled || b.getAttribute("aria-disabled") === "true",
      }))
      .filter((x) => x.text)
      .slice(0, 120)
  );
  return {
    url: page.url(),
    title: await page.title().catch(() => ""),
    body: body.slice(0, 8000),
    links,
    buttons,
  };
}

async function main() {
  const mode = process.argv[2] || "inspect";
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
  const page = await context.newPage();
  const out = { ok: false, mode };
  try {
    await login(page);
    const waitUntil = mode === "extract-detail" ? "domcontentloaded" : "networkidle";
    await page.goto(startUrl, { waitUntil, timeout: 45000 });
    if (mode === "extract-detail") {
      await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
    }
    await page.waitForTimeout(3000);

    if (mode === "inspect") {
      Object.assign(out, await summarizePage(page));
    } else if (mode === "click-opportunities") {
      const target = page.locator('a:has-text("Retailer Opportunities"), button:has-text("Retailer Opportunities"), text=Retailer Opportunities').first();
      if (await target.count()) {
        await Promise.all([
          page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {}),
          target.click(),
        ]);
        await page.waitForTimeout(3000);
      }
      Object.assign(out, await summarizePage(page));
    } else if (mode === "search-account") {
      const term = process.argv[4] || "Sam";
      const fields = page.locator('input[type=search], input[placeholder*=Search i], input[name*=search i], input[id*=search i]');
      if (await fields.count()) {
        await fields.first().fill(term);
        await page.waitForTimeout(3000);
      }
      Object.assign(out, await summarizePage(page));
    } else if (mode === "share-modal") {
      const share = page.locator('button:has-text("Share profile"), a:has-text("Share profile")').first();
      if (await share.count()) {
        await share.click();
        await page.waitForTimeout(3000);
      }
      Object.assign(out, await summarizePage(page));
    } else if (mode === "start-target") {
      const target = process.argv[4] || "7-Eleven";
      const targetBox = await page.locator(`text=${target}`).first().boundingBox();
      let clicked = false;
      if (targetBox) {
        const buttons = await page.locator('button:has-text("Start submission")').elementHandles();
        const candidates = [];
        for (const button of buttons) {
          const box = await button.boundingBox();
          if (!box) continue;
          const dy = box.y - targetBox.y;
          const dx = Math.abs((box.x + box.width / 2) - (targetBox.x + targetBox.width / 2));
          if (dy > -20 && dy < 260) candidates.push({ button, dy, dx });
        }
        candidates.sort((a, b) => a.dy - b.dy || a.dx - b.dx);
        if (candidates[0]) {
          await candidates[0].button.click();
          clicked = true;
        }
      }
      out.target = target;
      out.clickedStartSubmission = clicked;
      if (clicked) {
        await page.waitForLoadState("networkidle", { timeout: 25000 }).catch(() => {});
        await page.waitForTimeout(5000);
      }
      Object.assign(out, await summarizePage(page));
    } else if (mode === "start-target-with-pitch") {
      const target = process.argv[4] || "7-Eleven";
      const pitch = process.argv.slice(5).join(" ").trim();
      const targetBox = await page.locator(`text=${target}`).first().boundingBox();
      let clicked = false;
      let filledPitch = false;
      if (targetBox) {
        const fields = await page.locator("textarea, [contenteditable=true], input[type=text]").elementHandles();
        const fieldCandidates = [];
        for (const field of fields) {
          const box = await field.boundingBox();
          if (!box) continue;
          const dy = box.y - targetBox.y;
          if (dy > -20 && dy < 420) fieldCandidates.push({ field, dy });
        }
        fieldCandidates.sort((a, b) => a.dy - b.dy);
        if (pitch && fieldCandidates[0]) {
          await fieldCandidates[0].field.fill(pitch.slice(0, 500)).catch(async () => {
            await fieldCandidates[0].field.click();
            await page.keyboard.insertText(pitch.slice(0, 500));
          });
          filledPitch = true;
          await page.waitForTimeout(1000);
        }

        const buttons = await page.locator('button:has-text("Start submission")').elementHandles();
        const buttonCandidates = [];
        for (const button of buttons) {
          const box = await button.boundingBox();
          if (!box) continue;
          const dy = box.y - targetBox.y;
          const dx = Math.abs((box.x + box.width / 2) - (targetBox.x + targetBox.width / 2));
          if (dy > -20 && dy < 520) buttonCandidates.push({ button, dy, dx });
        }
        buttonCandidates.sort((a, b) => a.dy - b.dy || a.dx - b.dx);
        if (buttonCandidates[0]) {
          await buttonCandidates[0].button.click();
          clicked = true;
        }
      }
      out.target = target;
      out.filledPitch = filledPitch;
      out.clickedStartSubmission = clicked;
      if (clicked) {
        await page.waitForLoadState("networkidle", { timeout: 25000 }).catch(() => {});
        await page.waitForTimeout(5000);
      }
      Object.assign(out, await summarizePage(page));
    } else if (mode === "inspect-form") {
      out.fields = await page.locator("input, textarea, [contenteditable=true], select").evaluateAll((nodes) =>
        nodes.map((n, i) => {
          const r = n.getBoundingClientRect();
          return {
            i,
            tag: n.tagName,
            type: n.getAttribute("type"),
            name: n.getAttribute("name"),
            id: n.id,
            placeholder: n.getAttribute("placeholder"),
            aria: n.getAttribute("aria-label"),
            role: n.getAttribute("role"),
            valueLen: (n.value || n.textContent || "").length,
            x: Math.round(r.x),
            y: Math.round(r.y),
            w: Math.round(r.width),
            h: Math.round(r.height),
            html: n.outerHTML.slice(0, 500),
          };
        })
      );
      out.buttons = await page.locator("button").evaluateAll((nodes) =>
        nodes
          .map((n, i) => {
            const r = n.getBoundingClientRect();
            return {
              i,
              text: (n.innerText || n.textContent || "").trim().replace(/\s+/g, " ").slice(0, 120),
              x: Math.round(r.x),
              y: Math.round(r.y),
              w: Math.round(r.width),
              h: Math.round(r.height),
              disabled: n.disabled,
              html: n.outerHTML.slice(0, 300),
            };
          })
          .filter((b) => b.text.includes("Start") || b.text.includes("Submit") || b.y > 500)
      );
      Object.assign(out, await summarizePage(page));
    } else if (mode === "direct-start-with-pitch") {
      const pitch = process.argv.slice(4).join(" ").trim();
      const message = page.locator("#message").first();
      if (await message.count()) {
        await message.fill(pitch.slice(0, 500));
        await page.waitForTimeout(1000);
        out.filledValueLen = await message.inputValue().then((v) => v.length).catch(() => -1);
      } else {
        out.filledValueLen = -1;
      }
      const beforeBody = await page.locator("body").innerText({ timeout: 10000 });
      out.remainingTextBeforeClick = beforeBody.match(/\d+\s*\/\s*500/g)?.slice(-3) || [];
      const buttons = page.locator('button:has-text("Start submission")');
      out.startButtonCount = await buttons.count();
      if (out.startButtonCount > 0) {
        await buttons.last().click();
        out.clickedStartSubmission = true;
        await page.waitForLoadState("networkidle", { timeout: 25000 }).catch(() => {});
        await page.waitForTimeout(5000);
      } else {
        out.clickedStartSubmission = false;
      }
      Object.assign(out, await summarizePage(page));
    } else if (mode === "manage-summary") {
      const body = await page.locator("body").innerText({ timeout: 10000 });
      out.matches = body
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => /7-Eleven|Application|Submission|Submitted|In Review|Not Submitted/i.test(line))
        .slice(0, 120);
      Object.assign(out, await summarizePage(page));
    } else if (mode === "manage-ongoing-summary") {
      const tab = page.locator('button:has-text("Ongoing Submissions")').first();
      if (await tab.count()) {
        await tab.click();
        await page.waitForTimeout(3000);
      }
      const body = await page.locator("body").innerText({ timeout: 10000 });
      out.matches = body
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => /7-Eleven|Application|Submission|Submitted|In Review|Not Submitted|KOVAL/i.test(line))
        .slice(0, 160);
      Object.assign(out, await summarizePage(page));
    } else if (mode === "extract-detail") {
      const body = await page.locator("body").innerText({ timeout: 10000 });
      out.url = page.url();
      out.detailLines = body
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .slice(0, 260);
      out.fields = await page.locator("input, textarea, [contenteditable=true], select").evaluateAll((nodes) =>
        nodes
          .map((n, i) => {
            const r = n.getBoundingClientRect();
            return {
              i,
              tag: n.tagName,
              type: n.getAttribute("type"),
              name: n.getAttribute("name"),
              id: n.id,
              placeholder: n.getAttribute("placeholder"),
              dataTname: n.getAttribute("data-tname"),
              value: (n.value || n.textContent || "").trim().slice(0, 500),
              x: Math.round(r.x),
              y: Math.round(r.y),
              w: Math.round(r.width),
              h: Math.round(r.height),
            };
          })
          .filter((field) => field.w > 0 || field.h > 0 || field.value)
      );
      out.buttons = await page.locator("button, input[type=submit]").evaluateAll((nodes) =>
        nodes.map((n) => ({
          text: (n.innerText || n.value || n.getAttribute("aria-label") || "").trim().replace(/\s+/g, " ").slice(0, 120),
          disabled: n.disabled || n.getAttribute("aria-disabled") === "true",
        })).filter((x) => x.text)
      );
      out.ok = true;
      console.log(JSON.stringify(out, null, 2));
      await browser.close();
      return;
    } else if (mode === "diversity-options") {
      const ids = ["react-select-2-input", "react-select-3-input", "react-select-4-input", "react-select-5-input"];
      out.options = {};
      for (const id of ids) {
        const field = page.locator(`#${id}`).first();
        if (await field.count()) {
          await field.click({ force: true }).catch(() => {});
          await page.waitForTimeout(800);
          const body = await page.locator("body").innerText({ timeout: 10000 });
          const lines = body.split("\n").map((line) => line.trim()).filter(Boolean);
          out.options[id] = lines.slice(-80);
          await page.keyboard.press("Escape").catch(() => {});
          await page.waitForTimeout(300);
        }
      }
      Object.assign(out, await summarizePage(page));
    } else if (mode === "set-diversity-source-backed") {
      const gender = page.locator("#react-select-2-input").first();
      if (await gender.count()) {
        await gender.click({ force: true });
        await page.waitForTimeout(500);
        await page.keyboard.type("Female");
        await page.waitForTimeout(500);
        await page.keyboard.press("Enter");
        await page.waitForTimeout(1500);
      }
      const body = await page.locator("body").innerText({ timeout: 10000 });
      out.saved = /All changes saved/i.test(body);
      out.hasFemale = /Female/i.test(body);
      out.hasWomenOwned = /Women-Owned/i.test(body);
      out.hasWosb = /Women Owned Small Business \\(WOSB\\)/i.test(body);
      out.continueDisabled = await page.locator('button:has-text("Continue")').first().evaluate((b) => b.disabled || b.getAttribute("aria-disabled") === "true").catch(() => null);
      out.submitDisabled = await page.locator('button:has-text("Submit my brand")').first().evaluate((b) => b.disabled || b.getAttribute("aria-disabled") === "true").catch(() => null);
      Object.assign(out, await summarizePage(page));
    }

    out.ok = true;
    console.log(JSON.stringify(out, null, 2));
  } catch (error) {
    out.error = String(error).slice(0, 900);
    out.url = page.url();
    console.log(JSON.stringify(out, null, 2));
  } finally {
    await browser.close();
  }
}

main();
