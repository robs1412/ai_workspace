const puppeteer = require('puppeteer-core');
const path = require('path');

async function main() {
  const [, , inputPath, outputPath, orientation] = process.argv;
  if (!inputPath || !outputPath) {
    throw new Error('Usage: node html_to_pdf.js <input.html> <output.pdf> [portrait|landscape]');
  }

  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--allow-file-access-from-files'],
  });

  try {
    const page = await browser.newPage();
    const url = 'file://' + path.resolve(inputPath);
    await page.goto(url, { waitUntil: 'networkidle0' });
    await page.pdf({
      path: outputPath,
      format: 'Letter',
      printBackground: true,
      displayHeaderFooter: false,
      landscape: orientation === 'landscape',
      margin: {
        top: '0.35in',
        right: '0.35in',
        bottom: '0.35in',
        left: '0.35in',
      },
    });
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
