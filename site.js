// A Pack to Recovery — site behavior (works without JS; this only enhances)
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} }
};

// Keep sticky directory tools just under the header
const head = document.querySelector('.site-head');
const setHead = () => head && document.documentElement.style.setProperty('--headh', head.offsetHeight + 'px');
setHead(); addEventListener('resize', setHead);

// Mobile menu
const menuBtn = document.querySelector('.menu-btn');
const nav = document.querySelector('#nav');
if (menuBtn && nav) {
  menuBtn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open);
  });
}

// Larger text toggle (remembered per visitor)
const sizeBtn = document.querySelector('#textsize');
const applySize = on => {
  document.documentElement.classList.toggle('big', on);
  if (sizeBtn) { sizeBtn.setAttribute('aria-pressed', on); sizeBtn.textContent = on ? 'A− Normal text' : 'A+ Larger text'; }
};
applySize(store.get('apr-big', false));
sizeBtn?.addEventListener('click', () => { const on = !document.documentElement.classList.contains('big'); store.set('apr-big', on); applySize(on); });

// Progress bars
document.querySelectorAll('.progress').forEach(p => {
  const goal = +p.dataset.goal || 1, packed = +p.dataset.packed || 0;
  const fill = p.querySelector('.fill');
  requestAnimationFrame(() => setTimeout(() => { fill.style.width = Math.max(2, Math.min(100, packed / goal * 100)) + '%'; }, 150));
});

// Directory
const q = document.querySelector('#q');
if (q) {
  const cards = [...document.querySelectorAll('.res')];
  const groups = [...document.querySelectorAll('.group')];
  const townSel = document.querySelector('#town');
  const chips = [...document.querySelectorAll('.chip[data-cat]')];
  const flags = [...document.querySelectorAll('.chip[data-flag]')];
  const count = document.querySelector('#count');
  const empty = document.querySelector('#empty');
  const savedCount = document.querySelector('#savedcount');
  let saved = new Set(store.get('apr-saved', []));
  let cat = 'all';

  // Index text once
  cards.forEach(c => { c._text = (c.closest('.group').querySelector('h2').textContent + ' ' + c.textContent).toLowerCase(); });

  const syncSaved = () => {
    cards.forEach(c => c.querySelector('.save').setAttribute('aria-pressed', saved.has(c.dataset.id)));
    savedCount.textContent = saved.size;
    store.set('apr-saved', [...saved]);
  };

  const update = () => {
    const terms = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    const town = townSel.value;
    const on = flags.filter(f => f.getAttribute('aria-pressed') === 'true').map(f => f.dataset.flag);
    let total = 0;
    for (const g of groups) {
      let vis = 0;
      const catOk = cat === 'all' || g.dataset.cat === cat;
      for (const c of g.querySelectorAll('.res')) {
        const tags = c.dataset.tags.split(',');
        const ok = catOk
          && terms.every(t => c._text.includes(t))
          && (!town || c.dataset.town === town)
          && on.every(f => f === 'saved' ? saved.has(c.dataset.id) : tags.includes(f));
        c.hidden = !ok;
        if (ok) vis++;
      }
      g.hidden = vis === 0;
      g.querySelector('.gcount').textContent = vis;
      total += vis;
    }
    count.textContent = `${total} resource${total === 1 ? '' : 's'} shown`;
    empty.hidden = total > 0;
    const params = new URLSearchParams();
    if (q.value) params.set('q', q.value);
    if (town) params.set('town', town);
    if (cat !== 'all') params.set('cat', cat);
    history.replaceState(null, '', params.toString() ? '?' + params : location.pathname + location.hash);
  };

  // Restore from URL (so volunteers can share a filtered link)
  const p = new URLSearchParams(location.search);
  if (p.get('q')) q.value = p.get('q');
  if (p.get('town')) townSel.value = p.get('town');
  if (p.get('cat')) cat = p.get('cat');
  chips.forEach(c => c.setAttribute('aria-pressed', c.dataset.cat === cat));
  if (location.hash === '#saved') document.querySelector('#savedchip').setAttribute('aria-pressed', 'true');

  let t;
  q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(update, 120); });
  townSel.addEventListener('change', update);
  chips.forEach(c => c.addEventListener('click', () => {
    cat = c.dataset.cat;
    chips.forEach(x => x.setAttribute('aria-pressed', x === c));
    update();
  }));
  flags.forEach(f => f.addEventListener('click', () => {
    f.setAttribute('aria-pressed', f.getAttribute('aria-pressed') !== 'true');
    update();
  }));
  document.querySelector('#reset').addEventListener('click', () => {
    q.value = ''; townSel.value = ''; cat = 'all';
    chips.forEach(x => x.setAttribute('aria-pressed', x.dataset.cat === 'all'));
    flags.forEach(f => f.setAttribute('aria-pressed', 'false'));
    update();
  });
  document.querySelector('#print').addEventListener('click', () => window.print());
  document.addEventListener('click', e => {
    const b = e.target.closest('.save');
    if (!b) return;
    const id = b.closest('.res').dataset.id;
    saved.has(id) ? saved.delete(id) : saved.add(id);
    syncSaved();
    if (document.querySelector('#savedchip').getAttribute('aria-pressed') === 'true') update();
  });

  syncSaved();
  update();
}
