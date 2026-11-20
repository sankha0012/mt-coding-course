const itemsEl = document.getElementById('items');
const inputEl = document.getElementById('input');
let shown = 0;

async function api(path, body) {
  const options = path === '/api/run' ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) };
  const r = await fetch(path, options);
  if (!r.ok) throw new Error(path + ' ' + r.status);
  return r.json();
}

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

const KEYWORDS = new Set(('select from where group by order limit offset having join left right inner outer full cross on as and or '
  + 'not in is null like between distinct union all with case when then else end asc desc over partition using exists').split(' '));
const FUNCTIONS = new Set('count avg sum min max round coalesce length lower upper abs'.split(' '));
const TOKEN = /('(?:[^']|'')*'?|"[^"]*"?)|(--[^\n]*)|(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z_0-9]*)|(\s+|.)/g;

function highlight(text) {
  const frag = document.createDocumentFragment();
  TOKEN.lastIndex = 0;
  let m;
  while ((m = TOKEN.exec(text)) !== null) {
    const [tok, str, com, num, word] = m;
    let cls = null;
    if (str) cls = 'str';
    else if (com) cls = 'com';
    else if (num) cls = 'num';
    else if (word) { const w = word.toLowerCase(); cls = KEYWORDS.has(w) ? 'kw' : FUNCTIONS.has(w) ? 'fn' : null; }
    frag.appendChild(cls ? el('span', cls, tok) : document.createTextNode(tok));
  }
  return frag;
}

function codeBlock(sql, cls) {
  const pre = el('pre', cls);
  pre.appendChild(highlight(sql));
  return pre;
}

function lineNodes(text) {
  const out = document.createDocumentFragment();
  text.split('\n').forEach((line, i) => {
    if (i) out.appendChild(document.createElement('br'));
    line.split('`').forEach((part, j) => {
      if (j % 2) { const c = el('code'); c.appendChild(highlight(part)); out.appendChild(c); }
      else out.appendChild(document.createTextNode(part));
    });
  });
  return out;
}

function renderText(text, cls) {
  const box = el('div', 'teacher' + (cls ? ' ' + cls : ''));
  text.split(/```sql\n([\s\S]*?)\n```/).forEach((part, i) => {
    if (i % 2) { box.appendChild(codeBlock(part)); return; }
    part.split(/\n\s*\n/).filter(p => p.trim()).forEach(p => {
      const para = el('p'); para.appendChild(lineNodes(p.trim())); box.appendChild(para);
    });
  });
  return box;
}

function renderResult(item) {
  const box = el('div');
  if (item.label) box.appendChild(el('div', 'label', item.label));
  if (item.error) { box.appendChild(el('pre', 'output', item.error)); return box; }
  const table = el('table');
  const head = el('tr');
  item.columns.forEach(c => head.appendChild(el('th', null, c)));
  table.appendChild(head);
  item.rows.forEach(r => {
    const tr = el('tr');
    r.forEach(v => tr.appendChild(el('td', null, v === null ? '' : String(v))));
    table.appendChild(tr);
  });
  const wrap = el('div', 'tablewrap');
  wrap.appendChild(table);
  box.appendChild(wrap);
  if (item.total > item.rows.length) box.appendChild(el('div', 'total', item.total.toLocaleString() + ' rows in all'));
  return box;
}

function renderItem(item) {
  if (item.type === 'teacher') return renderText(item.text, item.style);
  if (item.type === 'learner') return codeBlock(item.sql, 'learner');
  if (item.type === 'result') return renderResult(item);
  const box = el('div', 'compare');
  [['Yours', item.yours, ''], ['Usual', item.usual, ' usual']].forEach(([name, sql, extra]) => {
    const col = el('div');
    col.appendChild(el('div', 'label' + extra, name));
    col.appendChild(codeBlock(sql));
    box.appendChild(col);
  });
  return box;
}

function button(label, onClick) {
  const b = el('button', 'primary', label); b.type = 'button'; b.onclick = onClick; return b;
}

function makeEditor() {
  const wrap = el('div', 'editor');
  const layer = el('pre', 'hl'); layer.setAttribute('aria-hidden', 'true');
  const box = el('textarea');
  box.rows = 3;
  box.setAttribute('autocomplete', 'off'); box.setAttribute('autocapitalize', 'off');
  box.setAttribute('autocorrect', 'off'); box.setAttribute('spellcheck', 'false');
  const sync = () => {
    layer.replaceChildren(highlight(box.value + (box.value.endsWith('\n') ? ' ' : '')));
    box.style.height = 'auto';
    box.style.height = Math.max(box.scrollHeight, 96) + 'px';
  };
  box.addEventListener('input', sync);
  wrap.append(layer, box);
  return { wrap, box, sync };
}

function renderInput(pending) {
  inputEl.replaceChildren();
  if (pending.mode === 'continue') {
    inputEl.appendChild(button('Continue', () => send('/api/next')));
  } else if (pending.mode === 'run') {
    inputEl.appendChild(codeBlock(pending.sql));
    inputEl.appendChild(button('Run', () => send('/api/next')));
  } else if (pending.mode === 'answer') {
    const { wrap, box, sync } = makeEditor();
    const hint = el('p', 'hint');
    const run = () => {
      if (!box.value.trim()) { hint.textContent = 'Type an answer first.'; return; }
      send('/api/answer', { sql: box.value });
    };
    box.addEventListener('input', () => { hint.textContent = ''; });
    box.onkeydown = e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); } };
    inputEl.append(wrap, button('Run', run), hint);
    sync();
    box.focus();
  } else if (pending.mode === 'done') {
    inputEl.appendChild(button('Sit this lesson again', () => send('/api/run/new')));
  }
}

function render(view) {
  if (view.items.length < shown) shown = 0;
  itemsEl.replaceChildren();
  const lastTeacher = view.items.map(i => i.type).lastIndexOf('teacher');
  view.items.forEach((item, i) => {
    const node = renderItem(item);
    if (i < lastTeacher) node.classList.add('old');
    if (shown && i >= shown) node.classList.add('rise');
    itemsEl.appendChild(node);
  });
  shown = view.items.length;
  renderInput(view.pending);
  inputEl.scrollIntoView({ block: 'end', behavior: 'smooth' });
}

async function send(path, body) {
  try { render(await api(path, body)); }
  catch (e) { inputEl.appendChild(el('p', 'hint', 'That did not go through. Reload the page.')); }
}

api('/api/run').then(render);
