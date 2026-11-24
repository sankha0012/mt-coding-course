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

// ---- colours for code, in the page and in the editor

const WORDS = {
  sql: {
    keywords: new Set(('select from where group by order limit offset having join left right inner outer full cross on as and or '
      + 'not in is null like between distinct union all with case when then else end asc desc over partition using exists').split(' ')),
    functions: new Set('count avg sum min max round coalesce length lower upper abs lag lead row_number rank strftime'.split(' ')),
    token: /('(?:[^']|'')*'?|"[^"]*"?)|(--[^\n]*)|(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z_0-9]*)|(\s+|.)/g,
  },
  python: {
    keywords: new Set(('def return if elif else for while in not and or is None True False import from as pass break continue lambda '
      + 'try except with class assert yield del global raise').split(' ')),
    functions: new Set(('print len sum min max sorted reversed range list dict set tuple str int float bool open enumerate zip round abs '
      + 'map filter any all isinstance split join append get items keys values lower upper strip').split(' ')),
    token: /("""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|'(?:\\.|[^'\\\n])*'?|"(?:\\.|[^"\\\n])*"?)|(#[^\n]*)|(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z_0-9]*)|(\s+|.)/g,
  },
};

function highlight(text, lang) {
  const w = WORDS[lang === 'python' ? 'python' : 'sql'];
  const frag = document.createDocumentFragment();
  w.token.lastIndex = 0;
  let m;
  while ((m = w.token.exec(text)) !== null) {
    const [tok, str, com, num, word] = m;
    let cls = null;
    if (str) cls = 'str';
    else if (com) cls = 'com';
    else if (num) cls = 'num';
    else if (word) { const x = lang === 'python' ? word : word.toLowerCase(); cls = w.keywords.has(x) ? 'kw' : w.functions.has(x.toLowerCase()) ? 'fn' : null; }
    frag.appendChild(cls ? el('span', cls, tok) : document.createTextNode(tok));
  }
  return frag;
}

function codeBlock(code, cls, lang) {
  const pre = el('pre', cls);
  pre.appendChild(highlight(code, lang));
  return pre;
}

// ---- the teacher's text and the results

function lineNodes(text, lang) {
  const out = document.createDocumentFragment();
  text.split('\n').forEach((line, i) => {
    if (i) out.appendChild(document.createElement('br'));
    line.split('`').forEach((part, j) => {
      if (j % 2) { const c = el('code'); c.appendChild(highlight(part, lang)); out.appendChild(c); }
      else out.appendChild(document.createTextNode(part));
    });
  });
  return out;
}

function renderText(text, cls, lang) {
  const box = el('div', 'teacher' + (cls ? ' ' + cls : ''));
  const parts = text.split(/```(\w+)\n([\s\S]*?)\n```/);
  for (let i = 0; i < parts.length; i += 3) {
    parts[i].split(/\n\s*\n/).filter(p => p.trim()).forEach(p => {
      const para = el('p'); para.appendChild(lineNodes(p.trim(), lang)); box.appendChild(para);
    });
    if (parts[i + 1]) box.appendChild(codeBlock(parts[i + 2], null, parts[i + 1]));
  }
  return box;
}

function renderResult(item) {
  const box = el('div');
  if (item.label) box.appendChild(el('div', 'label', item.label));
  if (item.lang === 'python') {
    if (item.text) box.appendChild(el('pre', 'printed', item.text.replace(/\n$/, '')));
    else if (!item.error) box.appendChild(el('div', 'total', 'Nothing was printed.'));
    if (item.error) box.appendChild(el('pre', 'output', item.error));
    return box;
  }
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
  if (item.type === 'teacher') return renderText(item.text, item.style, item.lang);
  if (item.type === 'learner') return codeBlock(item.sql, 'learner', item.lang);
  if (item.type === 'result') return renderResult(item);
  const box = el('div', 'compare');
  [['Yours', item.yours, ''], ['Usual', item.usual, ' usual']].forEach(([name, sql, extra]) => {
    const col = el('div');
    col.appendChild(el('div', 'label' + extra, name));
    col.appendChild(codeBlock(sql, null, 'sql'));
    box.appendChild(col);
  });
  return box;
}

// ---- the editor

function button(label, onClick, cls) {
  const b = el('button', cls || 'primary', label); b.type = 'button'; b.onclick = onClick; return b;
}

function makeEditor(initialLang) {
  let lang = initialLang || 'sql';
  const wrap = el('div', 'editor');
  const layer = el('pre', 'hl'); layer.setAttribute('aria-hidden', 'true');
  const box = el('textarea');
  box.rows = 3;
  box.setAttribute('autocomplete', 'off'); box.setAttribute('autocapitalize', 'off');
  box.setAttribute('autocorrect', 'off'); box.setAttribute('spellcheck', 'false');
  const sync = () => {
    layer.replaceChildren(highlight(box.value + (box.value.endsWith('\n') ? ' ' : ''), lang));
    box.style.height = 'auto';
    box.style.height = Math.max(box.scrollHeight, 96) + 'px';
  };
  const insert = text => { box.setRangeText(text, box.selectionStart, box.selectionEnd, 'end'); sync(); };
  box.addEventListener('input', sync);
  box.addEventListener('keydown', e => {
    if (lang !== 'python') return;
    if (e.key === 'Tab' && !e.shiftKey) { e.preventDefault(); insert('    '); }
    if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey && !e.shiftKey) {
      e.preventDefault();
      const before = box.value.slice(0, box.selectionStart);
      const line = before.slice(before.lastIndexOf('\n') + 1);
      insert('\n' + line.match(/^ */)[0] + (/:\s*$/.test(line) ? '    ' : ''));
    }
  });
  wrap.append(layer, box);
  return { wrap, box, sync, setLang: l => { lang = l; sync(); } };
}

function renderInput(pending) {
  inputEl.replaceChildren();
  const lang = pending.lang || 'sql';
  if (pending.mode === 'continue') {
    inputEl.appendChild(button('Continue', () => send('/api/next')));
  } else if (pending.mode === 'run') {
    inputEl.appendChild(codeBlock(pending.sql, null, lang));
    inputEl.appendChild(button('Run', () => send('/api/next')));
  } else if (pending.mode === 'answer') {
    const { wrap, box, sync } = makeEditor(lang);
    const hint = el('p', 'hint');
    const run = () => {
      if (!box.value.trim()) { hint.textContent = 'Type an answer first.'; return; }
      send('/api/answer', { sql: box.value });
    };
    box.addEventListener('input', () => { hint.textContent = ''; });
    box.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); } });
    inputEl.append(wrap, button('Run', run), hint);
    sync();
    box.focus();
  } else if (pending.mode === 'done') {
    if (pending.next) inputEl.appendChild(button('Next lesson', () => send('/api/run/new', { next: true })));
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

// ---- the try-it panel: the learner's own code on the same data. Nothing is saved or logged.

function initPlay() {
  const panel = el('details'); panel.id = 'play';
  panel.appendChild(el('summary', null, 'Try your own code'));
  const body = el('div', 'play-body');
  const ed = makeEditor('sql');
  const out = el('div', 'play-out');
  const hint = el('p', 'hint');
  let lang = 'sql';
  const tabs = el('div', 'tabs');
  const tabButtons = {};
  const pick = l => {
    lang = l; ed.setLang(l);
    Object.entries(tabButtons).forEach(([name, b]) => b.classList.toggle('on', name === l));
  };
  [['sql', 'SQL'], ['python', 'Python']].forEach(([l, label]) => {
    tabButtons[l] = button(label, () => pick(l), 'tab');
    tabs.appendChild(tabButtons[l]);
  });
  const go = async () => {
    if (!ed.box.value.trim()) { hint.textContent = 'Type some code first.'; return; }
    hint.textContent = '';
    try { out.replaceChildren(renderResult(await api('/api/play', { lang, code: ed.box.value }))); }
    catch (e) { hint.textContent = 'That did not go through.'; }
  };
  ed.box.addEventListener('input', () => { hint.textContent = ''; });
  ed.box.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); go(); } });
  body.append(tabs, ed.wrap, button('Run', go, 'primary small'), hint, out);
  panel.appendChild(body);
  pick('sql');
  document.querySelector('main').appendChild(panel);
}

initPlay();
api('/api/run').then(render);
