# Captures the demo screenshots used by the deck (phone closeups, e_*.png) and the
# submission video (full-page frames, f_*.png). Re-runnable: resets learning/attention
# state first, then walks the flows in an order that leaves honest on-screen state
# (meter at 2/4 for Flow A, audit chain populated before the Compliance shot).
#
# Run:  backend\.venv\Scripts\python video\capture_screens.py
# Needs: backend on :8000, frontend dev server on :5173, playwright chromium installed.

import json
import re
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

APP = "http://localhost:5173"
API = "http://localhost:8000"
OUT = Path(__file__).parent / "captures"
OUT.mkdir(parents=True, exist_ok=True)

PHONE = 'div[class*="rounded-[2.5rem]"]'  # the mocked phone frame
CONSOLE = 'div[class*="bg-yono-ink"][class*="rounded-3xl"]'  # Mission Control box

errors: list[str] = []


def reset_all_personas() -> list[dict]:
    personas = json.load(urllib.request.urlopen(f"{API}/personas"))
    for p in personas:
        req = urllib.request.Request(f"{API}/feedback/{p['persona_id']}", method="DELETE")
        urllib.request.urlopen(req)
    return personas


def shot(page, name: str, element=None):
    path = OUT / f"{name}.png"
    (element or page).screenshot(path=str(path))
    print(f"  saved {path.name}")


def phone(page):
    return page.locator(PHONE).first


def click_persona(page, headline: str):
    page.locator("button", has_text=headline).first.click()
    page.wait_for_timeout(900)  # nudge + txn fetch


def allow_consent(page):
    btn = page.locator("button", has_text=re.compile("Yes, analyse|विश्लेषण करें")).first
    btn.wait_for(state="visible", timeout=15000)
    btn.click()
    page.wait_for_timeout(600)


def open_why(page):
    page.get_by_text("Why am I seeing this?").first.click()
    page.wait_for_timeout(400)


def close_why(page):
    page.get_by_text("Hide", exact=True).first.click()
    page.wait_for_timeout(200)


def click_primary(page):
    page.locator('button[class*="mt-3 w-full rounded-xl py-2.5"]').first.click()
    page.wait_for_timeout(900)


def set_lang(page, lang: str):
    label = "EN" if lang == "en" else "हिं"
    page.locator("button", has_text=re.compile(f"^{label}$")).first.click()
    page.wait_for_timeout(300)


def scene(fn):
    """Run a capture scene; a failure logs but never kills the whole run."""
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        errors.append(f"{fn.__name__}: {e}")
        print(f"  !! {fn.__name__} failed: {e}", file=sys.stderr)


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
    page = ctx.new_page()
    page.set_default_timeout(15000)

    reset_all_personas()
    page.goto(APP)
    page.locator("button", has_text="Idle Saver").first.wait_for(state="visible")
    page.wait_for_timeout(1500)  # auto-selected Idle Saver: nudge fetch + consent gate

    def s01_hero():
        shot(page, "f01_hero")

    def s02_flow_b():
        click_persona(page, "Premium Leaker")
        page.locator("button", has_text=re.compile("Yes, analyse|विश्लेषण करें")).first.wait_for(
            state="visible"
        )
        shot(page, "f02a_consent_hi")
        shot(page, "e02a_consent_hi", phone(page))
        allow_consent(page)
        page.get_by_text("Why am I seeing this?").first.wait_for(state="visible")
        shot(page, "f02b_nudge_hi")
        shot(page, "e02b_nudge_hi", phone(page))
        # XAI card reads better in English for judges
        set_lang(page, "en")
        open_why(page)
        da = page.get_by_text(re.compile("devil's advocate", re.I)).first
        da.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        shot(page, "f02c_why_da")
        shot(page, "e02c_why_da", phone(page))
        close_why(page)
        click_primary(page)
        page.get_by_text("Talk to a human advisor first").first.wait_for(state="visible")
        shot(page, "f02d_comparison")
        shot(page, "e02d_comparison", phone(page))
        # scroll the "where doing nothing wins" box into view
        dn = page.get_by_text(re.compile("doing nothing", re.I)).first
        dn.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        shot(page, "f02e_donothing")
        shot(page, "e02e_donothing", phone(page))

    def s03_flow_m():
        click_persona(page, "Missold Policyholder")
        allow_consent(page)
        page.get_by_text("Why am I seeing this?").first.wait_for(state="visible")
        shot(page, "f03a_missold_flag")
        shot(page, "e03a_missold_flag", phone(page))
        set_lang(page, "en")
        open_why(page)
        shot(page, "e03b_missold_why", phone(page))
        close_why(page)
        click_primary(page)  # blocked by Sahayak co-consent
        page.locator("button", has_text=re.compile("^(Approve|मंज़ूर करें)$")).first.wait_for(
            state="visible"
        )
        shot(page, "f06_guardian")  # both phones side by side
        shot(page, "e06_guardian_wait", phone(page))
        page.locator("button", has_text=re.compile("^(Approve|मंज़ूर करें)$")).first.click()
        page.wait_for_timeout(800)
        page.get_by_text(re.compile("Keep policy|पॉलिसी रखें")).first.wait_for(state="visible")
        shot(page, "f03c_exit_vs_stay")
        shot(page, "e03c_exit_vs_stay", phone(page))

    def s09a_shelf():
        click_persona(page, "New Earner")
        allow_consent(page)
        page.get_by_text("Why am I seeing this?").first.wait_for(state="visible")
        click_primary(page)
        page.get_by_text(re.compile("non-SBI option wins|कोई और बेहतर है")).first.wait_for(
            state="visible"
        )
        shot(page, "f09a_open_shelf")
        shot(page, "e09a_open_shelf", phone(page))

    def s09b_flow_d():
        click_persona(page, "Explorer")
        try:
            allow_consent(page)
        except Exception:  # noqa: BLE001
            pass  # feature discovery may not gate on consent
        page.get_by_text("Why am I seeing this?").first.wait_for(state="visible")
        click_primary(page)
        page.wait_for_timeout(800)
        shot(page, "f09b_flowd_walkthrough")
        shot(page, "e09b_flowd_walkthrough", phone(page))

    def s05_flow_a():
        # Second visit this session -> attention meter honestly reads 2 of 4
        click_persona(page, "Idle Saver")
        allow_consent(page)
        page.get_by_text("Why am I seeing this?").first.wait_for(state="visible")
        shot(page, "f05a_flowa_nudge_en")
        shot(page, "e05a_flowa_nudge_en", phone(page))
        set_lang(page, "hi")
        shot(page, "f05b_flowa_nudge_hi")
        shot(page, "e05b_flowa_nudge_hi", phone(page))
        set_lang(page, "en")
        open_why(page)
        dn = page.get_by_text(re.compile("do nothing|inflation", re.I)).first
        dn.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        shot(page, "e05c_flowa_why_donothing", phone(page))
        close_why(page)
        # attention meter closeup
        meter = page.get_by_text(re.compile("attention budget|ध्यान बजट", re.I)).first
        box = meter.locator("xpath=ancestor::div[2]")
        shot(page, "e05d_attention_meter", box)

    def s07_mission():
        page.get_by_role("button", name="Mission Control", exact=True).click()
        page.get_by_text("autonomously").first.wait_for(state="visible", timeout=20000)
        page.wait_for_timeout(500)
        shot(page, "f07_mission_control")
        shot(page, "e07_mission_control", page.locator(CONSOLE).first)

    def s08_compliance():
        page.locator("button", has_text=re.compile("^Compliance$", re.I)).first.click()
        page.get_by_text("chain verified").first.wait_for(state="visible")
        # expand the newest record to show the hash link
        page.locator('button[class*="px-3 py-2.5 text-left"]').first.click()
        page.wait_for_timeout(400)
        shot(page, "f08_compliance")
        shot(page, "e08_compliance", page.locator(CONSOLE).first)

    for s in (s01_hero, s02_flow_b, s03_flow_m, s09a_shelf, s09b_flow_d, s05_flow_a, s07_mission, s08_compliance):
        print(f"scene: {s.__name__}")
        scene(s)

    browser.close()

print("\n--- capture summary ---")
for f in sorted(OUT.glob("*.png")):
    print(f"{f.name}  {f.stat().st_size // 1024} KB")
if errors:
    print("\nFAILED SCENES:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
print("all scenes captured")
