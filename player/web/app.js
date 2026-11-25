const itemsEl = document.getElementById('items');
const inputEl = document.getElementById('input');
let shown = 0;
let features = { mongo: false };  // what this machine can run, from /api/features

async function api(path, body) {
  const options = ['/api/run', '/api/providers', '/api/data', '/api/course', '/api/features'].includes(path) ? {} : {
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
  mongo: {
    keywords: new Set('db true false null'.split(' ')),
    functions: new Set(('find findone aggregate countdocuments estimateddocumentcount distinct sort limit skip insertone insertmany '
      + 'updateone updatemany deleteone deletemany isodate').split(' ')),
    token: /("(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)|(\/\/[^\n]*)|(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([$A-Za-z_][$A-Za-z_0-9]*)|(\s+|.)/g,
  },
};

function langKey(lang) {
  return lang === 'python' ? 'python' : (lang === 'mongo' || lang === 'js') ? 'mongo' : 'sql';
}

function highlight(text, lang) {
  const key = langKey(lang);
  const w = WORDS[key];
  const frag = document.createDocumentFragment();
  w.token.lastIndex = 0;
  let m;
  while ((m = w.token.exec(text)) !== null) {
    const [tok, str, com, num, word] = m;
    let cls = null;
    if (str) cls = 'str';
    else if (com) cls = 'com';
    else if (num) cls = 'num';
    else if (word) {
      const x = key === 'sql' ? word.toLowerCase() : word;
      cls = w.keywords.has(x) || (key === 'mongo' && word[0] === '$') ? 'kw' : w.functions.has(key === 'python' ? x.toLowerCase() : x.toLowerCase()) ? 'fn' : null;
    }
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

// a value as the mongo shell prints it: names bare, one line when it fits
function shellValue(v, depth = 0) {
  if (v === null || typeof v !== 'object') return JSON.stringify(v);
  const list = Array.isArray(v);
  const parts = list ? v.map(x => shellValue(x, depth + 1))
    : Object.entries(v).map(([k, x]) => (/^[A-Za-z_$][\w$]*$/.test(k) ? k : JSON.stringify(k)) + ': ' + shellValue(x, depth + 1));
  const [open, close] = list ? ['[', ']'] : ['{', '}'];
  if (!parts.length) return open + close;
  const gap = list ? '' : ' ';
  const flat = open + gap + parts.join(', ') + gap + close;
  if (flat.length + depth * 2 <= 88 && !flat.includes('\n')) return flat;
  const pad = '  '.repeat(depth + 1);
  return open + '\n' + parts.map(p => pad + p).join(',\n') + '\n' + '  '.repeat(depth) + close;
}

function docBlock(d) {
  return codeBlock(shellValue(d), 'doc', 'mongo');
}

function renderResult(item) {
  const box = el('div');
  if (item.label) box.appendChild(el('div', 'label', item.label));
  if (item.lang === 'mongo') {
    if (item.error) { box.appendChild(el('pre', 'output', item.error)); return box; }
    if (!item.docs.length) { box.appendChild(el('div', 'total', 'No documents.')); return box; }
    const plain = item.docs.every(d => d === null || typeof d !== 'object');  // a count, or a list of values
    if (plain) box.appendChild(el('pre', 'printed', item.docs.map(String).join('\n')));
    else item.docs.forEach(d => box.appendChild(docBlock(d)));
    if (!plain || item.total > item.docs.length) {
      const n = item.total.toLocaleString();
      box.appendChild(el('div', 'total', item.total > item.docs.length ? n + ' documents, first ' + item.docs.length + ' shown'
        : n + (item.total === 1 ? ' document' : ' documents')));
    }
    return box;
  }
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

const viewHooks = [];  // things that follow the lesson on screen: the Data tab, the Course panel

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
  viewHooks.forEach(f => f());
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
  const opener = el('div'); opener.id = 'play-open';
  opener.append(button('Data', () => setOpen(true, 'data'), 'tab'),
                button('Try your own code', () => setOpen(true, 'try'), 'tab'));

  const head = el('div', 'play-head');
  const viewTabs = el('div', 'tabs');
  const viewButtons = {};
  [['try', 'Try'], ['data', 'Data']].forEach(([v, label]) => {
    viewButtons[v] = button(label, () => showView(v), 'tab');
    viewTabs.appendChild(viewButtons[v]);
  });
  head.append(viewTabs, button('\u00d7', () => setOpen(false), 'close'));
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
  [['sql', 'SQL'], ['python', 'Python'], ['mongo', 'MongoDB']].forEach(([l, label]) => {
    tabButtons[l] = button(label, () => pick(l), 'tab');
    tabs.appendChild(tabButtons[l]);
  });
  tabButtons.mongo.hidden = true;  // shown once the page knows there is a mongod
  viewHooks.push(() => { tabButtons.mongo.hidden = !features.mongo; });
  const go = async () => {
    if (!ed.box.value.trim()) { hint.textContent = 'Type some code first.'; return; }
    hint.textContent = '';
    try { out.replaceChildren(renderResult(await api('/api/play', { lang, code: ed.box.value }))); }
    catch (e) { hint.textContent = 'That did not go through.'; }
  };
  ed.box.addEventListener('input', () => { hint.textContent = ''; });
  ed.box.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); go(); } });
  const tryView = el('div');
  tryView.append(tabs, ed.wrap, button('Run', go, 'primary small'), hint, out);
  const dataView = el('div', 'data-view');
  panel.append(head, tryView, dataView);
  pick('sql');

  let view = keep.get('play-view') === 'data' ? 'data' : 'try';
  let shownKey = null;  // the dataset now drawn

  const dataTable = t => {
    const box = el('div');
    if (t.docs) {  // a collection: its count and its first documents
      box.appendChild(el('div', 'total', t.total.toLocaleString() + ' documents, first ' + t.docs.length + ' shown'));
      t.docs.forEach(d => box.appendChild(docBlock(d)));
      return box;
    }
    const n = t.total.toLocaleString();
    const note = t.total > t.rows.length ? n + ' rows, first ' + t.rows.length + ' shown' : n + ' rows';
    const table = el('table');
    const hr = el('tr');
    t.columns.forEach(c => hr.appendChild(el('th', null, c)));
    table.appendChild(hr);
    t.rows.forEach(r => {
      const tr = el('tr');
      r.forEach(v => {
        const td = el('td');
        if (v === null) td.appendChild(el('span', 'empty', 'empty')); else td.textContent = v;
        tr.appendChild(td);
      });
      table.appendChild(tr);
    });
    const wrap = el('div', 'tablewrap'); wrap.appendChild(table);
    box.append(el('div', 'total', note), wrap);
    return box;
  };

  const drawData = tables => {
    if (!tables.length) { dataView.replaceChildren(el('p', 'hint', 'There is no data for this step.')); return; }
    const chips = el('div', 'tabs');
    const grid = el('div');
    const buttons = tables.map((t, i) => { const b = button(t.name, () => show(i), 'tab'); chips.appendChild(b); return b; });
    const show = i => {
      buttons.forEach((b, j) => b.classList.toggle('on', i === j));
      grid.replaceChildren(dataTable(tables[i]));
    };
    dataView.replaceChildren(chips, grid);
    show(0);
  };

  const loadData = async () => {
    if (!panel.isConnected || view !== 'data') return;
    try {
      const d = await api('/api/data');
      if (d.data === shownKey) return;  // same dataset: stay as it is
      shownKey = d.data;
      drawData(d.tables);
    } catch (e) {
      shownKey = null;
      dataView.replaceChildren(el('p', 'hint', 'The data did not load.'));
    }
  };

  const showView = v => {
    view = v; keep.set('play-view', v);
    tryView.hidden = v !== 'try'; dataView.hidden = v !== 'data';
    Object.entries(viewButtons).forEach(([n, b]) => b.classList.toggle('on', n === v));
    if (v === 'try') { ed.sync(); ed.box.focus(); } else loadData();
  };
  viewHooks.push(loadData);

  const MIN = 280;
  const setWidth = px => {
    const w = Math.max(MIN, Math.min(px, window.innerWidth - MIN - 9));
    panel.style.setProperty('--play-w', w + 'px');
    keep.set('play-width', String(Math.round(w)));
    return w;
  };
  const setOpen = (on, v) => {
    keep.set('play-open', on ? '1' : '0');
    if (on) {
      split.append(gutter, panel); opener.remove();
      showView(v || view);
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

// ---- the course panel: the whole course as a map. Finished lessons can be sat again, future ones are locked.

function initCourse() {
  const split = document.getElementById('split');
  const panel = el('aside'); panel.id = 'course';
  const opener = button('Course', () => setOpen(true), 'tab'); opener.id = 'course-open';
  const head = el('div', 'play-head');
  head.append(el('span', null, 'The course'), button('\u00d7', () => setOpen(false), 'close'));
  head.lastChild.setAttribute('aria-label', 'Close the course panel');
  const list = el('div', 'course-list');
  const hint = el('p', 'hint');
  panel.append(head, list, hint);
  let confirming = null;  // the lesson whose "from the beginning?" question is showing

  const start = async id => {
    try {
      shown = 0; threads.length = 0;  // a new sitting starts clean
      confirming = null;
      render(await api('/api/lesson/start', { lesson: id }));
    } catch (e) { hint.textContent = 'That did not go through.'; }
  };

  const row = l => {
    const li = el('div', 'course-row ' + l.state + (l.finished ? ' finished' : ''));
    const mark = l.state === 'locked' ? '\ud83d\udd12' : l.state === 'current' ? '\u25b8' : l.finished ? '\u2713' : '';
    li.append(el('span', 'mark', mark), el('span', 'ltitle', l.title));
    if (l.state === 'locked') {
      li.setAttribute('aria-disabled', 'true');
      if (l.waits.length) li.appendChild(el('span', 'act', 'Opens after ' + l.waits.slice(0, 2).join(', ') + (l.waits.length > 2 ? ' and ' + (l.waits.length - 2) + ' more' : '')));
      return li;
    }
    const act = el('span', 'act');
    if (l.state === 'open') act.append(button('Start', () => start(l.lesson), 'link'));
    else if (confirming === l.lesson) {
      act.append(el('span', null, 'From the beginning? '), button('Yes', () => start(l.lesson), 'link'),
                 button('Cancel', () => { confirming = null; draw(); }, 'link'));
    } else act.append(button(l.state === 'current' ? 'Start over' : 'Sit again', () => { confirming = l.lesson; draw(); }, 'link'));
    li.appendChild(act);
    return li;
  };

  let data = null;
  const draw = () => {
    if (!data) return;
    const nodes = [];
    const section = extra => data.strands.forEach(s => {
      const mine = data.lessons.filter(l => l.strand === s.id && l.extra === extra);
      if (!mine.length) return;
      nodes.push(el('h3', null, s.name));
      const layered = new Set(mine.map(l => l.layer)).size > 1;  // only a strand with both layers gets sub-headings
      let layer = null;
      mine.forEach(l => {
        if (layered && l.layer !== layer) nodes.push(el('h4', null, data.layers[l.layer] || l.layer));
        layer = l.layer;
        nodes.push(row(l));
      });
    });
    section(false);
    if (data.lessons.some(l => l.extra)) {  // optional lessons sit apart, with no count of how many are left
      nodes.push(el('h2', null, (data.extras && data.extras.title) || 'Extras'));
      if (data.extras && data.extras.note) nodes.push(el('p', 'hint', data.extras.note));
      section(true);
    }
    list.replaceChildren(...nodes);
  };

  const load = async () => {
    if (!panel.isConnected) return;
    try { data = await api('/api/course'); hint.textContent = ''; draw(); }
    catch (e) { hint.textContent = 'The course did not load.'; }
  };

  const setOpen = on => {
    keep.set('course-open', on ? '1' : '0');
    if (on) { split.prepend(panel); opener.remove(); load(); }
    else { panel.remove(); document.body.appendChild(opener); }
  };
  viewHooks.push(load);
  setOpen(keep.get('course-open') === '1');
}

function initTheme() {
  const root = document.documentElement;
  const toggle = button('', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next; keep.set('theme', next); label();
  }, 'tab');
  toggle.id = 'theme-toggle';
  const label = () => { toggle.textContent = root.dataset.theme === 'dark' ? 'Light mode' : 'Dark mode'; };
  label();
  document.body.appendChild(toggle);
}

initTheme();
initPlay();
initCourse();
Promise.all([api('/api/providers'), api('/api/run'), api('/api/features')]).then(([p, view, f]) => { providers = p.providers; features = f; render(view); });
