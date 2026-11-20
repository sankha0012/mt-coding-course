const itemsEl = document.getElementById('items');
const inputEl = document.getElementById('input');

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

function lineNodes(text) {
  const out = document.createDocumentFragment();
  text.split('\n').forEach((line, i) => {
    if (i) out.appendChild(document.createElement('br'));
    line.split('`').forEach((part, j) => out.appendChild(j % 2 ? el('code', null, part) : document.createTextNode(part)));
  });
  return out;
}

function renderText(text, cls) {
  const box = el('div', 'teacher' + (cls ? ' ' + cls : ''));
  text.split(/```sql\n([\s\S]*?)\n```/).forEach((part, i) => {
    if (i % 2) { box.appendChild(el('pre', null, part)); return; }
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
  box.appendChild(table);
  if (item.total > item.rows.length) box.appendChild(el('div', 'total', item.total.toLocaleString() + ' rows in all'));
  return box;
}

function renderItem(item) {
  if (item.type === 'teacher') return renderText(item.text, item.style);
  if (item.type === 'learner') return el('pre', 'learner', item.sql);
  if (item.type === 'result') return renderResult(item);
  const box = el('div', 'compare');
  [['Yours', item.yours], ['Usual', item.usual]].forEach(([name, sql]) => {
    const col = el('div'); col.appendChild(el('div', 'caption', name)); col.appendChild(el('pre', null, sql)); box.appendChild(col);
  });
  return box;
}

function button(label, onClick) {
  const b = el('button', null, label); b.type = 'button'; b.onclick = onClick; return b;
}

function renderInput(pending) {
  inputEl.replaceChildren();
  if (pending.mode === 'continue') {
    inputEl.appendChild(button('Continue', () => send('/api/next')));
  } else if (pending.mode === 'run') {
    inputEl.appendChild(el('pre', null, pending.sql));
    inputEl.appendChild(button('Run', () => send('/api/next')));
  } else if (pending.mode === 'answer') {
    const box = el('textarea');
    box.setAttribute('autocomplete', 'off'); box.setAttribute('autocapitalize', 'off');
    box.setAttribute('autocorrect', 'off'); box.setAttribute('spellcheck', 'false');
    const hint = el('p', 'hint');
    const run = () => {
      if (!box.value.trim()) { hint.textContent = 'Type an answer first.'; return; }
      send('/api/answer', { sql: box.value });
    };
    box.oninput = () => { hint.textContent = ''; };
    box.onkeydown = e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); } };
    inputEl.append(box, button('Run', run), hint);
    box.focus();
  } else if (pending.mode === 'done') {
    inputEl.appendChild(button('Sit this lesson again', () => send('/api/run/new')));
  }
}

function render(view) {
  itemsEl.replaceChildren();
  const lastTeacher = view.items.map(i => i.type).lastIndexOf('teacher');
  view.items.forEach((item, i) => {
    const node = renderItem(item);
    if (i < lastTeacher) node.classList.add('old');
    itemsEl.appendChild(node);
  });
  renderInput(view.pending);
  inputEl.scrollIntoView({ block: 'end', behavior: 'smooth' });
}

async function send(path, body) {
  try { render(await api(path, body)); }
  catch (e) { inputEl.appendChild(el('p', 'hint', 'That did not go through. Reload the page.')); }
}

api('/api/run').then(render);
