# Supplemental element captures for the deck: the guardian's phone alone, the
# agent decision-log panel, and a readable top-crop of the tall compliance shot.
import re
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

APP = "http://localhost:5173"
OUT = Path(__file__).parent / "captures"

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
    page = ctx.new_page()
    page.set_default_timeout(15000)
    page.goto(APP)
    page.locator("button", has_text="Missold Policyholder").first.wait_for(state="visible")

    # Flow M up to the guardian gate
    page.locator("button", has_text="Missold Policyholder").first.click()
    page.wait_for_timeout(900)
    allow = page.locator("button", has_text=re.compile("Yes, analyse|विश्लेषण करें")).first
    allow.wait_for(state="visible")
    allow.click()
    page.get_by_text("Why am I seeing this?").first.wait_for(state="visible")
    page.locator('button[class*="mt-3 w-full rounded-xl py-2.5"]').first.click()
    approve = page.locator("button", has_text=re.compile("^(Approve|मंज़ूर करें)$")).first
    approve.wait_for(state="visible")

    # Guardian phone = the ancestor block around the Approve button's card
    guardian = approve.locator(
        'xpath=ancestor::div[contains(@class, "rounded")][last()-1]'
    )
    try:
        guardian.screenshot(path=str(OUT / "e06b_guardian_phone.png"))
        print("saved e06b_guardian_phone.png")
    except Exception as e:  # noqa: BLE001
        print(f"guardian ancestor failed ({e}); trying second phone frame")
        frames = page.locator('div[class*="rounded-[2.5rem]"]')
        if frames.count() > 1:
            frames.nth(1).screenshot(path=str(OUT / "e06b_guardian_phone.png"))
            print("saved e06b_guardian_phone.png (frame fallback)")

    # Decision log panel (right column) — ancestor of the AGENT DECISION LOOP label
    label = page.get_by_text("Agent decision loop", exact=False).first
    panel = label.locator("xpath=ancestor::div[2]")
    panel.screenshot(path=str(OUT / "e10_decision_log.png"))
    print("saved e10_decision_log.png")

    browser.close()

# Readable crop of the tall compliance capture: header + verify badge + first records
src = Image.open(OUT / "e08_compliance.png")
w, h = src.size
crop = src.crop((0, 0, w, min(h, int(w * 1.05))))  # roughly square-ish top slice
crop.save(OUT / "e08b_compliance_top.png")
print(f"saved e08b_compliance_top.png ({crop.size[0]}x{crop.size[1]})")
