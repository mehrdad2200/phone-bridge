const {JSDOM, VirtualConsole} = require('jsdom');
const fs = require('fs');
const path = require('path');
const DIR = process.argv[2] || __dirname;   // folder holding page_fa.html / page_en.html (see dump_page.py)
let pass = 0, fail = 0;
const ok = (n, c, info) => { if (c) pass++; else { fail++; console.log('FAIL', n, info || ''); } };
function boot(lang) {
  const posts = [], gets = [], errors = [];
  const vc = new VirtualConsole(); vc.on('jsdomError', e => errors.push(String(e.message || e)));
  const dom = new JSDOM(fs.readFileSync(path.join(DIR, 'page_' + lang + '.html'), 'utf8'), {runScripts: 'dangerously', url: 'http://192.168.1.9:8765/?t=TOKEN123', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => { if (o && o.body) posts.push(JSON.parse(o.body)); else gets.push(u);
        const body = u.includes('/state') ? {screen: true, system: false} : u.includes('/inbox') ? {id: 1, text: 'https://example.com'} : {text: 'pc clip'};
        return Promise.resolve({ok: true, json: () => Promise.resolve(body)}); };
      w.navigator.vibrate = () => true;
    }});
  return {dom, w: dom.window, d: dom.window.document, posts, gets, errors};
}
const touch = (w, el, type, pts) => { const e = new w.Event(type, {bubbles: true, cancelable: true}); e.touches = pts.map(([x, y]) => ({clientX: x, clientY: y})); el.dispatchEvent(e); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fl = () => sleep(25);

(async () => {
  for (const lang of ['fa', 'en']) {
    const {w, d, posts, errors} = boot(lang);
    await sleep(300);
    ok(lang + ': no JS errors on load', errors.length === 0, errors.join(' | '));
    ok(lang + ': html lang/dir', d.documentElement.lang === lang && d.documentElement.dir === (lang === 'fa' ? 'rtl' : 'ltr'), d.documentElement.dir);
    ok(lang + ': 5 bottom-nav items', d.querySelectorAll('#nav button').length === 5);
    ok(lang + ': first view = type', d.getElementById('v-type').classList.contains('on'));
    ok(lang + ': title translated', d.querySelector('.brand span:last-child').textContent === (lang === 'fa' ? 'ریموت کامپیوتر' : 'PC Remote'), d.querySelector('.brand span:last-child').textContent);
    ok(lang + ': 20 shortcut buttons with labels', d.querySelectorAll('#keygrid .btn').length === 20 && d.querySelector('#keygrid .btn').textContent === (lang === 'fa' ? 'کپی' : 'Copy'));
    ok(lang + ': svg icons injected', d.querySelectorAll('i[data-i] svg').length >= 10 && d.querySelectorAll('#nav svg').length === 5);
    // navigation
    for (const [id, nb] of [['pad', 'pad'], ['pres', 'pres'], ['media', 'media'], ['more', 'more'], ['keys', 'more'], ['screen', 'more'], ['clip', 'more'], ['sys', 'more'], ['type', 'type']]) {
      w.go(id); ok(lang + ': go(' + id + ')', d.getElementById('v-' + id).classList.contains('on') && d.getElementById('nb-' + nb).classList.contains('on'));
    }
    // language toggle flips everything
    const before = d.getElementById('lang').textContent; d.getElementById('lang').click();
    const other = lang === 'fa' ? 'en' : 'fa';
    ok(lang + ': toggle -> ' + other, d.documentElement.lang === other && d.getElementById('lang').textContent !== before && d.documentElement.dir === (other === 'fa' ? 'rtl' : 'ltr'));
    d.getElementById('lang').click();
    // typing diff + combo mods
    posts.length = 0; const t = d.getElementById('t');
    t.value = 'سلام'; t.dispatchEvent(new w.Event('input')); await fl();
    ok(lang + ': type -> text event', posts.length === 1 && posts[0].type === 'text' && posts[0].add === 'سلام' && posts[0].back === 0, JSON.stringify(posts));
    posts.length = 0; t.value = 'سلم'; t.dispatchEvent(new w.Event('input')); await fl();
    ok(lang + ': autocorrect/backspace diff', posts.length === 1 && posts[0].back === 2 && posts[0].add === 'م', JSON.stringify(posts));
    posts.length = 0; d.querySelectorAll('#mods .chip')[0].click(); t.value = 'سلمc'; t.dispatchEvent(new w.Event('input')); await fl();
    ok(lang + ': Ctrl + letter -> combo', posts.length === 1 && posts[0].type === 'combo' && posts[0].keys.join('+') === 'ctrl+c' && t.value === 'سلم', JSON.stringify(posts));
    posts.length = 0; d.querySelectorAll('#keyrow .btn')[3].click(); await fl();
    ok(lang + ': backspace key button', posts[0] && posts[0].key === 'backspace', JSON.stringify(posts));
    // trackpad gestures
    w.go('pad'); const pad = d.getElementById('pad'); posts.length = 0;
    touch(w, pad, 'touchstart', [[100, 100]]); touch(w, pad, 'touchmove', [[130, 110]]); touch(w, pad, 'touchend', []);
    await sleep(120);
    const mv = posts.find(p => p.type === 'move');
    ok(lang + ': 1-finger move -> relative move (accelerated)', mv && mv.dx > 30 && mv.dy > 10, JSON.stringify(posts));
    posts.length = 0; await sleep(320);
    touch(w, pad, 'touchstart', [[50, 50]]); touch(w, pad, 'touchend', []); await fl();
    ok(lang + ': tap -> left click', posts.length === 1 && posts[0].type === 'click' && posts[0].b === 'left', JSON.stringify(posts));
    posts.length = 0; await sleep(320);
    touch(w, pad, 'touchstart', [[50, 50], [90, 50]]); touch(w, pad, 'touchend', []); await fl();
    ok(lang + ': 2-finger tap -> right click', posts.length === 1 && posts[0].b === 'right', JSON.stringify(posts));
    posts.length = 0; await sleep(320);
    touch(w, pad, 'touchstart', [[50, 50], [90, 50]]); touch(w, pad, 'touchmove', [[50, 120], [90, 120]]); touch(w, pad, 'touchend', []); await fl();
    const sc = posts.filter(p => p.type === 'scroll');
    ok(lang + ': 2-finger drag -> scroll (natural, 4 notches)', sc.length === 4 && sc.every(p => p.d === -1), JSON.stringify(posts));
    posts.length = 0; await sleep(320);
    touch(w, pad, 'touchstart', [[50, 50]]); touch(w, pad, 'touchend', []);     // first tap
    touch(w, pad, 'touchstart', [[50, 50]]); touch(w, pad, 'touchmove', [[80, 80]]); await fl();
    ok(lang + ': tap-then-touch -> mouse down (drag)', posts.some(p => p.type === 'mouse' && p.act === 'down'), JSON.stringify(posts));
    touch(w, pad, 'touchend', []); await fl(); ok(lang + ': release -> mouse up', posts.some(p => p.type === 'mouse' && p.act === 'up'));
    // media / slides / keys
    posts.length = 0; w.go('media'); d.querySelector('#v-media .play').click(); d.querySelectorAll('#v-media .row .btn')[4].click(); await fl();
    ok(lang + ': media play + vol up', posts[0].k === 'play' && posts[1].k === 'vol_up', JSON.stringify(posts));
    posts.length = 0; d.querySelector('#keygrid .btn').click(); await fl(); ok(lang + ': shortcut Ctrl+C', posts[0].keys.join('+') === 'ctrl+c');
    // presentation timer
    w.tmToggle(); await sleep(2100); w.tmToggle(); ok(lang + ': slide timer counts', d.getElementById('tm').textContent === '00:02' || d.getElementById('tm').textContent === '00:01', d.getElementById('tm').textContent);
    // system confirm sheet (no accidental shutdown)
    posts.length = 0; w.pw('shutdown'); ok(lang + ': shutdown needs confirmation', posts.length === 0 && d.getElementById('sheet').classList.contains('on'));
    d.getElementById('sheetok').click(); await fl(); ok(lang + ': confirm -> power event', posts.length === 1 && posts[0].cmd === 'shutdown');
    posts.length = 0; w.pw('cancel'); await fl(); ok(lang + ': cancel shutdown is immediate', posts[0].cmd === 'cancel');
    // inbox from PC
    await sleep(100); ok(lang + ': PC->phone text shown + link button', d.getElementById('inbox').textContent === 'https://example.com' && d.getElementById('openbtn').style.display === 'flex', d.getElementById('openbtn').style.display);
    ok(lang + ': system disabled message from /state', d.getElementById('sysmsg').textContent.length > 5);
    ok(lang + ': still no JS errors after all actions', errors.length === 0, errors.join(' | '));
    w.close();
  }
  console.log('JS page tests: ' + pass + ' passed, ' + fail + ' failed');
  process.exit(fail ? 1 : 0);
})();
