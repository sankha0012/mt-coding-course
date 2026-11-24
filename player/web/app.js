const itemsEl = document.getElementById('items');
const inputEl = document.getElementById('input');
let shown = 0;

async function api(path, body) {
  const options = (path === '/api/run' || path === '/api/providers') ? {} : {
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
  const parts = text.split(/```(\w*)\n([\s\S]*?)\n?```/);
  for (let i = 0; i < parts.length; i += 3) {
    parts[i].split(/\n\s*\n/).filter(p => p.trim()).forEach(p => {
      const para = el('p'); para.appendChild(lineNodes(p.trim(), lang)); box.appendChild(para);
    });
    if (i + 2 < parts.length) box.appendChild(codeBlock(parts[i + 2], null, parts[i + 1] || lang));
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

// ---- side questions: a thread opens in the transcript, the lesson waits, the learner says when to go back

const threads = [];       // each: { at: item count when it began, lang, messages, thinking, back, node }
let lastTeacher = null;   // the prompt now waiting, for "Where we were"
let providers = [];       // the question services that have a key, from the server
const PROVIDER_NAMES = { gemini: 'Gemini', groq: 'Groq' };

function threadNode(t) {
  const box = el('div', 'side');
  box.appendChild(el('div', 'label', 'Side question'));
  t.messages.forEach(m => box.appendChild(m.role === 'user' ? el('p', 'you', m.text) : renderText(m.text, 'reply', t.lang)));
  if (t.thinking) box.appendChild(el('p', 'hint', 'Thinking it over.'));
  if (t.back && t.back.text) {
    box.appendChild(el('div', 'label', 'Back to the lesson'));
    box.appendChild(renderText('Where we were:\n\n' + t.back.text, 'reply', t.back.lang));
  }
  return box;
}

function makeAsk(lang) {
  const pane = el('div', 'ask');
  const self = { pane, box: el('textarea'), onBack: () => {} };
  if (!providers.length) {
    pane.appendChild(el('p', 'hint', 'No question service is set up. Put a key in the .env file and restart the player.'));
    return self;
  }
  const box = self.box;
  box.rows = 3;
  box.placeholder = 'Ask the teacher about this step, or about SQL, Python, pandas or machine learning.';
  ['autocomplete', 'autocapitalize', 'autocorrect'].forEach(a => box.setAttribute(a, 'off'));
  box.setAttribute('spellcheck', 'false');
  const menu = el('select', 'provider');
  menu.setAttribute('aria-label', 'Which service answers');
  providers.forEach(p => menu.appendChild(new Option(PROVIDER_NAMES[p] || p, p)));
  const saved = keep.get('ask-provider');
  if (providers.includes(saved)) menu.value = saved;
  menu.addEventListener('change', () => keep.set('ask-provider', menu.value));
  const hint = el('p', 'hint');
  let thread = null;
  const paint = () => {
    const node = threadNode(thread);
    if (thread.node) thread.node.replaceWith(node); else itemsEl.appendChild(node);
    thread.node = node;
    node.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  };
  const ask = async () => {
    const question = box.value.trim();
    if (!question) { hint.textContent = 'Type a question first.'; return; }
    if (!thread) { thread = { at: shown, lang, messages: [], thinking: false, back: null, node: null }; threads.push(thread); }
    const earlier = thread.messages.map(m => ({ role: m.role, text: m.text }));
    thread.messages.push({ role: 'user', text: question });
    thread.thinking = true; box.value = ''; hint.textContent = ''; back.hidden = true;
    paint();
    try {
      const r = await api('/api/ask', { question, thread: earlier, provider: menu.value });
      thread.messages.push({ role: 'teacher', text: r.reply });
    } catch (e) { hint.textContent = 'That did not go through.'; }
    thread.thinking = false;
    paint();
    back.hidden = false;
  };
  const back = button('Got it, back to the lesson', () => {
    thread.back = lastTeacher || { text: '' };
    paint();
    thread = null; back.hidden = true;
    self.onBack();
    inputEl.scrollIntoView({ block: 'end', behavior: 'smooth' });
  }, 'primary small');
  back.hidden = true;
  box.addEventListener('input', () => { hint.textContent = ''; });
  box.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); ask(); } });
  const row = el('div', 'ask-row');
  row.append(button('Ask', ask, 'primary small'), menu, back);
  pane.append(box, row, hint);
  return self;
}

function renderInput(pending) {
  inputEl.replaceChildren();
  const lang = pending.lang || 'sql';
  const codePane = el('div'), tabs = el('div', 'tabs'), ask = makeAsk(lang);
  let focusCode = () => {};
  const tab = {};
  const show = which => {
    codePane.hidden = which !== 'code'; ask.pane.hidden = which !== 'ask';
    tab.code.classList.toggle('on', which === 'code'); tab.ask.classList.toggle('on', which === 'ask');
    if (which === 'ask') ask.box.focus(); else focusCode();
  };
  tab.code = button('Code', () => show('code'), 'tab');
  tab.ask = button('Ask', () => show('ask'), 'tab');
  tabs.append(tab.code, tab.ask);
  ask.onBack = () => show('code');

  if (pending.mode === 'continue') {
    codePane.appendChild(button('Continue', () => send('/api/next')));
  } else if (pending.mode === 'run') {
    codePane.appendChild(codeBlock(pending.sql, null, lang));
    codePane.appendChild(button('Run', () => send('/api/next')));
  } else if (pending.mode === 'answer') {
    const { wrap, box, sync } = makeEditor(lang);
    const hint = el('p', 'hint');
    const run = () => {
      if (!box.value.trim()) { hint.textContent = 'Type an answer first.'; return; }
      send('/api/answer', { sql: box.value });
    };
    box.addEventListener('input', () => { hint.textContent = ''; });
    box.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); } });
    codePane.append(wrap, button('Run', run), hint);
    focusCode = () => { sync(); box.focus(); };
  } else if (pending.mode === 'done') {
    if (pending.next) codePane.appendChild(button('Next lesson', () => send('/api/run/new', { next: true })));
    codePane.appendChild(button('Sit this lesson again', () => send('/api/run/new')));
  }
  inputEl.append(tabs, codePane, ask.pane);
  show('code');
}

function render(view) {
  if (view.items.length < shown) { shown = 0; threads.length = 0; }  // a new sitting starts clean
  itemsEl.replaceChildren();
  const lastTeacherAt = view.items.map(i => i.type).lastIndexOf('teacher');
  view.items.forEach((item, i) => {
    const node = renderItem(item);
    if (i < lastTeacherAt) node.classList.add('old');
    if (shown && i >= shown) node.classList.add('rise');
    itemsEl.appendChild(node);
    threads.filter(t => t.at === i + 1).forEach(t => { t.thinking = false; t.node = threadNode(t); itemsEl.appendChild(t.node); });
  });
  shown = view.items.length;
  const t = lastTeacherAt >= 0 ? view.items[lastTeacherAt] : null;
  lastTeacher = t ? { text: t.text, lang: t.lang || 'sql' } : null;
  renderInput(view.pending);
  inputEl.scrollIntoView({ block: 'end', behavior: 'smooth' });
}

async function send(path, body) {
  try { render(await api(path, body)); }
  catch (e) { inputEl.appendChild(el('p', 'hint', 'That did not go through. Reload the page.')); }
}

// ---- the try-it panel: the learner's own code on the same data. Nothing is saved or logged.
// It opens to the right of the lesson, and the bar between them drags to resize.

const keep = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* not kept; fine */ } },
};

function initPlay() {
  const split = document.getElementById('split');
  const gutter = el('div'); gutter.id = 'gutter'; gutter.tabIndex = 0;
  gutter.setAttribute('role', 'separator'); gutter.setAttribute('aria-orientation', 'vertical');
  gutter.setAttribute('aria-label', 'Resize the panes');
  const panel = el('aside'); panel.id = 'play';
  const opener = button('Try your own code', () => setOpen(true), 'tab'); opener.id = 'play-open';

  const head = el('div', 'play-head');
  head.append(el('span', null, 'Try your own code'), button('\u00d7', () => setOpen(false), 'close'));
  head.lastChild.setAttribute('aria-label', 'Close this pane');
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
  panel.append(head, tabs, ed.wrap, button('Run', go, 'primary small'), hint, out);
  pick('sql');

  const MIN = 280;
  const setWidth = px => {
    const w = Math.max(MIN, Math.min(px, window.innerWidth - MIN - 9));
    panel.style.setProperty('--play-w', w + 'px');
    keep.set('play-width', String(Math.round(w)));
    return w;
  };
  const setOpen = on => {
    keep.set('play-open', on ? '1' : '0');
    if (on) {
      split.append(gutter, panel); opener.remove(); ed.sync(); ed.box.focus();
      // in a narrow window the pane stacks under the lesson, so bring it into view
      if (getComputedStyle(gutter).display === 'none') panel.scrollIntoView({ block: 'start' });
    }
    else { gutter.remove(); panel.remove(); document.body.appendChild(opener); }
  };
  gutter.addEventListener('pointerdown', e => {
    gutter.setPointerCapture(e.pointerId);
    gutter.classList.add('drag'); document.body.classList.add('dragging');
  });
  gutter.addEventListener('pointermove', e => {
    if (gutter.hasPointerCapture(e.pointerId)) setWidth(window.innerWidth - e.clientX - 4);
  });
  const stop = e => { gutter.classList.remove('drag'); document.body.classList.remove('dragging'); };
  gutter.addEventListener('pointerup', stop);
  gutter.addEventListener('pointercancel', stop);
  gutter.addEventListener('keydown', e => {
    const step = e.key === 'ArrowLeft' ? 24 : e.key === 'ArrowRight' ? -24 : 0;
    if (step) { e.preventDefault(); setWidth(panel.getBoundingClientRect().width + step); }
  });
  window.addEventListener('resize', () => { if (panel.isConnected) setWidth(panel.getBoundingClientRect().width); });

  const saved = parseInt(keep.get('play-width'), 10);
  if (saved) panel.style.setProperty('--play-w', saved + 'px');
  setOpen(keep.get('play-open') === '1');
}

initPlay();
Promise.all([api('/api/providers'), api('/api/run')]).then(([p, view]) => { providers = p.providers; render(view); });
