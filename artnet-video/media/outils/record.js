const { chromium } = require('playwright');
const path = require('path');
const W = 1280, H = 800;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const OVERLAY = () => {
  const css = document.createElement('style');
  css.textContent = `
    #demoCursor { position: fixed; left: 0; top: 0; z-index: 99999; pointer-events: none;
      width: 26px; height: 26px; transform: translate(-3px,-2px); transition: none; }
    #demoClick { position: fixed; z-index: 99998; pointer-events: none; width: 44px; height: 44px;
      margin: -22px 0 0 -22px; border-radius: 50%; border: 3px solid #4f9dff; opacity: 0; }
    #demoClick.go { animation: ck .5s ease-out; }
    @keyframes ck { from { opacity: 1; transform: scale(.3) } to { opacity: 0; transform: scale(1.4) } }
    #demoCap { position: fixed; left: 50%; bottom: 28px; transform: translateX(-50%); z-index: 99990;
      max-width: 1000px; padding: 14px 26px; border-radius: 14px; background: rgba(10,12,16,.88);
      color: #fff; font: 600 23px/1.35 "Segoe UI", system-ui, sans-serif; text-align: center;
      border: 1px solid rgba(79,157,255,.5); box-shadow: 0 10px 40px rgba(0,0,0,.6);
      opacity: 0; transition: opacity .35s; pointer-events: none; }
    #demoCap.on { opacity: 1; }
    #demoCard { position: fixed; inset: 0; z-index: 99995; display: flex; flex-direction: column;
      align-items: center; justify-content: center; background: radial-gradient(circle at 50% 40%, #1c2b45, #07090c 70%);
      color: #fff; font-family: "Segoe UI", system-ui, sans-serif; text-align: center;
      opacity: 0; transition: opacity .6s; pointer-events: none; }
    #demoCard.on { opacity: 1; }
    #demoCard h1 { font-size: 58px; margin: 0 0 14px; letter-spacing: -.01em; }
    #demoCard p { font-size: 25px; color: #b8c4d6; margin: 6px 0; }
    #demoCard .chip { display: inline-block; margin: 26px 8px 0; padding: 8px 16px; border-radius: 999px;
      background: rgba(79,157,255,.15); border: 1px solid rgba(79,157,255,.5); font-size: 18px; color: #cfe2ff; }
    #demoSim { position: fixed; inset: 0; z-index: 99980; background: #050608; opacity: 0;
      transition: opacity .6s; pointer-events: none; }
    #demoSim.on { opacity: 1; }
    #demoSimTitle { position: fixed; top: 26px; left: 0; right: 0; text-align: center; z-index: 99981;
      color: #9aa0a6; font: 600 16px "Segoe UI", system-ui; letter-spacing: .12em; text-transform: uppercase;
      opacity: 0; transition: opacity .6s; pointer-events: none; }
    #demoSimTitle.on { opacity: 1; }`;
  document.head.appendChild(css);
  const cur = document.createElement('div'); cur.id = 'demoCursor';
  cur.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M3 2l7 19 2.5-7.5L20 11z" fill="#fff" stroke="#000" stroke-width="1.5" stroke-linejoin="round"/></svg>';
  const ck = document.createElement('div'); ck.id = 'demoClick';
  const cap = document.createElement('div'); cap.id = 'demoCap';
  const card = document.createElement('div'); card.id = 'demoCard';
  const sim = document.createElement('canvas'); sim.id = 'demoSim';
  const simT = document.createElement('div'); simT.id = 'demoSimTitle';
  simT.textContent = 'Simulation de l\'installation : 5 barres × 120 LEDs';
  document.body.append(sim, simT, card, cap, ck, cur);
  document.addEventListener('mousemove', e => { cur.style.left = e.clientX + 'px'; cur.style.top = e.clientY + 'px'; }, true);
  document.addEventListener('mousedown', e => {
    ck.style.left = e.clientX + 'px'; ck.style.top = e.clientY + 'px';
    ck.classList.remove('go'); void ck.offsetWidth; ck.classList.add('go');
  }, true);
  window.demo = {
    cap(t) { if (!t) { cap.classList.remove('on'); return; } cap.innerHTML = t; cap.classList.add('on'); },
    card(html) { if (!html) { card.classList.remove('on'); return; } card.innerHTML = html; card.classList.add('on'); },
    sim(on) { sim.classList.toggle('on', on); simT.classList.toggle('on', on); },
  };
  // rendu simulé du mur de LEDs, à partir des vraies données calculées par l'application
  function drawSim() {
    requestAnimationFrame(drawSim);
    if (!sim.classList.contains('on') && getComputedStyle(sim).opacity === '0') return;
    const w = sim.width = innerWidth, h = sim.height = innerHeight, x = sim.getContext('2d');
    x.fillStyle = '#050608'; x.fillRect(0, 0, w, h);
    const st = layout.stage, k = Math.min(w * 0.8 / st.w, h * 0.72 / st.h);
    const ox = w / 2 - (st.x0 + st.w / 2) * k, oy = h * 0.47 + (st.y0 + st.h / 2) * k;
    x.globalCompositeOperation = 'lighter';
    let li = 0;
    for (const b of layout.bars) {
      for (let i = 0; i < b.n; i++, li++) {
        const t = (i + .5) / b.n, px = ox + (b.x1 + (b.x2 - b.x1) * t) * k, py = oy - (b.y1 + (b.y2 - b.y1) * t) * k;
        const r = ledColors[li * 3] | 0, g = ledColors[li * 3 + 1] | 0, bl = ledColors[li * 3 + 2] | 0;
        const gr = x.createRadialGradient(px, py, 0, px, py, 16);
        gr.addColorStop(0, `rgba(${r},${g},${bl},.55)`); gr.addColorStop(1, `rgba(${r},${g},${bl},0)`);
        x.fillStyle = gr; x.fillRect(px - 16, py - 16, 32, 32);
        x.fillStyle = `rgb(${Math.min(255, r + 40)},${Math.min(255, g + 40)},${Math.min(255, bl + 40)})`;
        x.beginPath(); x.arc(px, py, 2.6, 0, 7); x.fill();
      }
    }
    x.globalCompositeOperation = 'source-over';
  }
  drawSim();
};

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: W, height: H },
    recordVideo: { dir: path.join(__dirname, 'rec'), size: { width: W, height: H } } });
  const p = await ctx.newPage();
  p.on('dialog', d => d.accept());
  p.on('pageerror', e => console.log('ERR', e));
  let mx = W / 2, my = H / 2;

  async function moveTo(x, y, ms = 700) {
    const steps = Math.max(8, Math.round(ms / 16));
    await p.mouse.move(x, y, { steps }); mx = x; my = y;
  }
  async function center(sel) {
    await p.evaluate(s => document.querySelector(s).scrollIntoView({ block: 'center', behavior: 'smooth' }), sel);
    await sleep(700);
  }
  async function pos(sel) {
    const b = await p.locator(sel).first().boundingBox();
    return [b.x + b.width / 2, b.y + b.height / 2, b];
  }
  async function click(sel, ms = 700) {
    const [x, y] = await pos(sel); await moveTo(x, y, ms); await sleep(150);
    await p.mouse.down(); await p.mouse.up();
    await p.locator(sel).first().click({ force: true, position: undefined, trial: true }).catch(() => {});
  }
  async function realClick(sel, ms = 700) {
    const [x, y] = await pos(sel); await moveTo(x, y, ms); await sleep(150);
    await p.mouse.click(x, y);
  }
  async function typeInto(sel, val) {
    await realClick(sel, 500);
    await p.keyboard.press('Control+A'); await p.keyboard.type(String(val), { delay: 90 });
    await p.dispatchEvent(sel, 'input'); await p.dispatchEvent(sel, 'change');
  }
  async function slide(sel, to, ms = 1400) {
    const [, , b] = await pos(sel);
    const info = await p.evaluate(s => { const e = document.querySelector(s); return [+e.min, +e.max, +e.value]; }, sel);
    const [mn, mxv, from] = info, xAt = v => b.x + 8 + (b.width - 16) * (v - mn) / (mxv - mn);
    await moveTo(xAt(from), b.y + b.height / 2, 500);
    await p.mouse.down();
    await moveTo(xAt(to), b.y + b.height / 2, ms);
    await p.mouse.up();
  }
  const cap = t => p.evaluate(t => demo.cap(t), t);
  const card = h => p.evaluate(h => demo.card(h), h);
  const editorPt = (bar, end) => p.evaluate(([bar, end]) => {
    const b = layout.bars[bar]; const [x, y] = view.toC(end === 0 ? (b.x1 + b.x2) / 2 : b['x' + end], end === 0 ? (b.y1 + b.y2) / 2 : b['y' + end]);
    const r = editor.getBoundingClientRect(); return [r.left + x * r.width / editor.width, r.top + y * r.height / editor.height];
  }, [bar, end]);
  async function dragEditor(bar, end, dxCm, dyCm, ms = 1300) {
    const [x, y] = await editorPt(bar, end);
    const kpx = await p.evaluate(() => view.k * editor.getBoundingClientRect().width / editor.width);
    await moveTo(x, y, 700); await sleep(200); await p.mouse.down();
    await moveTo(x + dxCm * kpx, y - dyCm * kpx, ms); await sleep(150); await p.mouse.up();
  }

  await p.goto('http://localhost:8090/');
  await p.evaluate(() => localStorage.clear());
  await p.reload();
  await p.evaluate(OVERLAY);
  await p.mouse.move(mx, my);

  // 1. Titre
  await card(`<h1>🎬 Vidéo → Art-Net → WLED</h1>
    <p>Affichez n'importe quelle vidéo sur vos barres de LEDs</p>
    <p style="font-size:20px">Fichier vidéo ou YouTube · câble Ethernet · contrôleur WLED</p>`);
  await sleep(3800);
  await card(null); await sleep(700);

  // 2. Vue d'ensemble
  await cap('Une page web calcule la couleur de chaque LED…');
  await sleep(1500);
  await realClick('#status', 1000);
  await cap('…et un petit relais l\'envoie en <b>Art-Net</b> au boîtier WLED, par le câble RJ45.');
  await sleep(2600);

  // 3. Générateur
  await center('#btnGen');
  await cap('1. Décrivez votre installation : nombre de barres, longueur, LEDs, espacement…');
  await typeInto('#gN', 4); await sleep(300);
  await typeInto('#gSp', 60); await sleep(300);
  await realClick('#btnGen'); await sleep(900);
  await cap('…sans oublier par où arrive le fil de données et le câblage en serpentin.');
  await typeInto('#gN', 5); await sleep(200);
  await typeInto('#gSp', 50); await sleep(200);
  await realClick('#gSerp', 500); await sleep(300); await realClick('#gSerp', 300);
  await realClick('#btnGen'); await sleep(1200);

  // 4. Mire
  await center('[data-test=mire]');
  await cap('2. La <b>mire</b> vérifie l\'ordre et le sens de chaque barre : une couleur par barre, du sombre au clair.');
  await realClick('[data-test=mire]');
  await sleep(600);
  await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })); await sleep(900);
  await moveTo(900, 450, 900);
  await sleep(2600);

  // 5. Éditeur
  await cap('3. Barres espacées, verticales ou en biais : glissez les poignées, par paliers de 50 cm.');
  await dragEditor(4, 2, 0, 50);
  await sleep(500);
  await dragEditor(2, 0, 0, 25, 1100);
  await sleep(500);
  await dragEditor(2, 0, 0, -25, 900);
  await sleep(1300);

  // 6. Tableau
  await center('#bars');
  await cap('Ou saisissez les positions exactes en centimètres. ▲▼ changent l\'ordre, ⇄ inverse le sens.');
  await typeInto('#bars tr:nth-child(5) input[data-k=y2]', 200);
  await p.keyboard.press('Enter'); await sleep(400);
  await moveTo((await pos('#bars tr:nth-child(5) [data-a=rev]'))[0], (await pos('#bars tr:nth-child(5) [data-a=rev]'))[1], 800);
  await sleep(1800);

  // 7. Source vidéo
  await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })); await sleep(800);
  await cap('4. Ouvrez un fichier vidéo, ou capturez un onglet YouTube.');
  const [fx, fy] = await pos('#btnFile'); await moveTo(fx, fy, 900); await sleep(200);
  await p.mouse.down(); await p.mouse.up();
  await p.setInputFiles('#file', path.join(__dirname, 'plasma.webm'));
  await sleep(1200);
  await moveTo(880, 420, 900);
  await cap('Chaque LED prend la couleur de la vidéo <b>à sa position réelle</b> sur l\'installation.');
  await sleep(3200);

  // 8. Cadrage
  await center('#zoom');
  await cap('5. Cadrez : zoom, décalage, et épaisseur de vidéo captée autour de chaque barre.');
  await slide('#zoom', 170); await sleep(300);
  await slide('#panX', -20, 1000); await sleep(300);
  await slide('#thick', 50, 1000); await sleep(800);
  await realClick('#btnRecenter'); await sleep(1200);

  // 9. Simulation
  await cap('Résultat sur l\'installation : ~30 images par seconde, en Art-Net.');
  await p.evaluate(() => demo.sim(true));
  await sleep(6500);
  await p.evaluate(() => demo.sim(false)); await sleep(700);

  // 10. Manuel
  await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })); await sleep(600);
  await cap('Tout est expliqué dans le <b>Manuel utilisateur</b> : réseau, WLED, mire, dépannage…');
  await realClick('[data-tab=tabManual]', 900); await sleep(1200);
  await realClick('#toc a[href="#m-wled"]', 900); await sleep(2000);
  await realClick('#toc a[href="#m-depannage"]', 900); await sleep(2200);
  await cap(null);

  // 11. Fin
  await card(`<h1>Prêt à l'emploi</h1>
    <p>Double-cliquez sur <b>lancer.bat</b>, branchez le câble, lancez la vidéo.</p>
    <div><span class="chip">Windows · Python</span><span class="chip">Chrome / Edge</span>
    <span class="chip">WLED en Art-Net</span></div>`);
  await sleep(4200);

  await ctx.close(); await browser.close();
  console.log('ok');
})();
