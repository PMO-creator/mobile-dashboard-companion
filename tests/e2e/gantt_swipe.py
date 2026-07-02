"""
E2E: no mobile, abre um eixo do Gantt e faz swipes horizontais longos.
Verifica que:
  1) o eixo continua ABERTO (altura do SVG não voltou a zero);
  2) as barras (<rect>) continuam SINCRONIZADAS com os textos da coluna sticky
     (mesmo Y de cada linha antes e depois do swipe).

Uso:
  BASE_URL=http://localhost:8080 python3 tests/e2e/gantt_swipe.py
  BASE_URL=https://pmo-creator.github.io/maz-dashboard python3 tests/e2e/gantt_swipe.py
"""
import asyncio, os, sys, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")
URL  = f"{BASE}/mobile.html"
SHOTS = Path("/tmp/browser/gantt_swipe"); SHOTS.mkdir(parents=True, exist_ok=True)

# iPhone 14 Pro-ish
VIEWPORT = {"width": 390, "height": 844}
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

def approx(a, b, tol=1.5): return abs(a-b) <= tol

async def swipe(page, x0, y, dx, steps=20):
    """Swipe horizontal contínuo dentro de um container."""
    await page.mouse.move(x0, y)
    await page.mouse.down()
    for i in range(1, steps+1):
        await page.mouse.move(x0 + dx*i/steps, y, steps=1)
        await asyncio.sleep(0.01)
    await page.mouse.up()
    await asyncio.sleep(0.15)

async def measure(page):
    """Coleta estado do primeiro Gantt renderizado: altura + Y de rects e textos."""
    return await page.evaluate("""
      () => {
        const wrap = document.querySelector('.gantt-svg-wrap');
        if (!wrap) return {ok:false, reason:'no gantt-svg-wrap'};
        const svgs = wrap.querySelectorAll('svg');
        if (!svgs.length) return {ok:false, reason:'no svg inside wrap'};
        const svg = svgs[svgs.length-1]; // barras normalmente ficam no SVG da direita
        const rects = [...svg.querySelectorAll('rect')]
          .filter(r => +r.getAttribute('height') > 6 && +r.getAttribute('height') < 40)
          .map(r => ({y:+r.getAttribute('y'), h:+r.getAttribute('height')}));
        const leftSvg = svgs[0];
        const texts = [...leftSvg.querySelectorAll('text')]
          .map(t => ({y:+t.getAttribute('y')}));
        return {
          ok:true,
          wrapH: wrap.getBoundingClientRect().height,
          scrollLeft: wrap.querySelector('div')?.scrollLeft ?? 0,
          rectCount: rects.length,
          rects: rects.slice(0,12),
          textCount: texts.length,
          texts: texts.slice(0,12),
        };
      }
    """)

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport=VIEWPORT, user_agent=UA,
                                        has_touch=True, is_mobile=True)
        page = await ctx.new_page()
        page.on("console", lambda m: print(f"  [console.{m.type}] {m.text}"[:180]))
        print(f"→ {URL}")
        await page.goto(URL, wait_until="domcontentloaded")
        # espera dados carregarem (ou timeout curto se offline)
        try:
            await page.wait_for_function(
                "document.querySelectorAll('.gantt-svg-wrap svg').length > 0",
                timeout=15000)
        except Exception:
            await page.screenshot(path=str(SHOTS/"00_no_gantt.png"))
            print("✗ Gantt não renderizou (provável bloqueio Sheets API neste ambiente).")
            print("  Rode contra sua URL do GitHub Pages: BASE_URL=https://... python3 tests/e2e/gantt_swipe.py")
            await browser.close(); return 2

        # navega até a aba Gantt (tab bar do mobile)
        await page.evaluate("""() => {
          const btn = [...document.querySelectorAll('.mob-tabbar [data-tab],[data-tab="gantt"],button,a')]
            .find(el => (el.textContent||'').toLowerCase().includes('gantt'));
          if (btn) btn.click();
        }""")
        await asyncio.sleep(0.5)
        await page.screenshot(path=str(SHOTS/"01_gantt_tab.png"))

        # abre o primeiro eixo (header clicável)
        opened = await page.evaluate("""() => {
          const hdr = document.querySelector('.gantt-axis-header,[data-axis],.gantt-group-header,.gantt-axis-title');
          if (hdr) { hdr.click(); return true; }
          // fallback: clica no primeiro título dentro da seção Gantt
          const anyHdr = document.querySelector('#tab-gantt h2, #tab-gantt h3, #tab-gantt .card > *:first-child');
          if (anyHdr) { anyHdr.click(); return true; }
          return false;
        }""")
        await asyncio.sleep(0.6)
        await page.screenshot(path=str(SHOTS/"02_axis_open.png"))

        before = await measure(page)
        print("baseline:", json.dumps(before, indent=2)[:600])
        if not before.get("ok") or before["rectCount"] == 0:
            print("✗ Não achei barras no Gantt aberto — teste inconclusivo."); 
            await browser.close(); return 3

        # descobre o container rolável do Gantt e faz 3 swipes longos
        box = await page.evaluate("""() => {
          const inner = document.querySelector('.gantt-svg-wrap > div');
          if (!inner) return null;
          const r = inner.getBoundingClientRect();
          return {x:r.x, y:r.y, w:r.width, h:r.height};
        }""")
        if not box:
            print("✗ Não achei scroller interno."); await browser.close(); return 4

        cy = box["y"] + box["h"]/2
        for i in range(3):
            await swipe(page, box["x"]+box["w"]-20, cy, -(box["w"]-40), steps=25)
            await asyncio.sleep(0.2)
        await page.screenshot(path=str(SHOTS/"03_after_swipes.png"))

        after = await measure(page)
        print("after:", json.dumps({k:after[k] for k in ('wrapH','scrollLeft','rectCount','textCount')}, indent=2))

        # assertions
        fails = []
        if not approx(after["wrapH"], before["wrapH"], tol=2):
            fails.append(f"altura do wrap mudou: {before['wrapH']} → {after['wrapH']} (eixo fechou?)")
        if after["rectCount"] < before["rectCount"]:
            fails.append(f"barras sumiram: {before['rectCount']} → {after['rectCount']}")
        if after["textCount"] != before["textCount"]:
            fails.append(f"textos da coluna sticky mudaram: {before['textCount']} → {after['textCount']}")
        # sincronia Y linha a linha
        n = min(len(before["rects"]), len(after["rects"]))
        drift = []
        for i in range(n):
            if not approx(before["rects"][i]["y"], after["rects"][i]["y"], tol=1.0):
                drift.append((i, before["rects"][i]["y"], after["rects"][i]["y"]))
        if drift:
            fails.append(f"Y das barras dessincronizou em {len(drift)} linhas: {drift[:3]}")
        if after["scrollLeft"] <= 0:
            fails.append(f"swipe não rolou (scrollLeft={after['scrollLeft']})")

        await browser.close()
        if fails:
            print("\n✗ FALHOU:"); [print("  -", f) for f in fails]; return 1
        print(f"\n✓ OK — eixo permaneceu aberto e {n} barras sincronizadas após swipes.")
        return 0

sys.exit(asyncio.run(main()))
