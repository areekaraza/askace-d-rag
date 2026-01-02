import { buildKnowledgeIndexFromTexts, loadDefaultKnowledge } from './rag/knowledge';
import { queryIndex, type SearchHit, type TfidfIndex } from './rag/tfidf';
import { explainHfError, hfGenerateText } from './hf/client';

type Role = 'user' | 'assistant' | 'system';

type ChatMessage = {
  role: Role;
  content: string;
  sources?: SearchHit[];
};

const LS_TOKEN = 'askace:hf_token';
const LS_MODEL = 'askace:hf_model';
const LS_K = 'askace:top_k';

function el<K extends keyof HTMLElementTagNameMap>(tag: K, className?: string): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (className) e.className = className;
  return e;
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string));
}

function formatSources(hits: SearchHit[]): string {
  const lines = hits.map((h, i) => {
    const snippet = h.chunk.text.length > 240 ? `${h.chunk.text.slice(0, 240)}…` : h.chunk.text;
    return `[#${i + 1}] ${h.chunk.source} (score ${h.score.toFixed(3)})\n${snippet}`;
  });
  return lines.join('\n\n');
}

function buildPrompt(args: {
  system: string;
  question: string;
  hits: SearchHit[];
}): string {
  const context = args.hits.length ? formatSources(args.hits) : 'No relevant context found.';

  return [
    `System: ${args.system}`,
    '',
    'You are a helpful RAG assistant. Use the provided context when relevant.',
    'If the answer is not in the context, say you do not know.',
    '',
    'Context:',
    context,
    '',
    `User question: ${args.question}`,
    '',
    'Answer (be concise, cite sources like [#1], [#2] when you use them):',
  ].join('\n');
}

async function readUploadedFiles(files: FileList): Promise<Array<{ source: string; text: string }>> {
  const results: Array<{ source: string; text: string }> = [];
  for (const f of Array.from(files)) {
    const text = await f.text();
    results.push({ source: `upload/${f.name}`, text });
  }
  return results;
}

export function createApp(mount: HTMLElement | null): void {
  if (!mount) throw new Error('Missing mount element');

  const state: {
    index: TfidfIndex | null;
    messages: ChatMessage[];
    busy: boolean;
    abort?: AbortController;
  } = {
    index: null,
    messages: [
      {
        role: 'assistant',
        content:
          'Hi! Add knowledge files (left panel), paste your Hugging Face token, then ask a question.\n\nRAG retrieval runs locally in your browser; only the final prompt is sent to Hugging Face.',
      },
    ],
    busy: false,
  };

  // Layout
  const container = el('div', 'container');
  const header = el('div', 'header');
  const title = el('div', 'title');
  title.innerHTML = `<h1>AskAce RAG (GitHub Pages)</h1><p>Simple, free static RAG: TF-IDF retrieval in-browser + Hugging Face generation.</p>`;

  const badge = el('div', 'badge');
  const dot = el('div', 'dot');
  const badgeText = el('div');
  badgeText.textContent = 'Not ready: build index first';
  badge.append(dot, badgeText);

  header.append(title, badge);

  const grid = el('div', 'grid');

  // Left: settings
  const settings = el('section', 'card');
  settings.innerHTML = `
    <header>
      <h2>Settings</h2>
      <p>Token is stored locally in your browser (localStorage). Don’t commit it to GitHub.</p>
    </header>
    <div class="body"></div>
  `;
  const settingsBody = settings.querySelector('.body') as HTMLDivElement;

  const tokenField = el('div', 'field');
  const tokenLabel = el('label');
  tokenLabel.textContent = 'Hugging Face token (hf_…)';
  const tokenInput = el('input') as HTMLInputElement;
  tokenInput.type = 'password';
  tokenInput.placeholder = 'hf_********************************';
  tokenInput.value = localStorage.getItem(LS_TOKEN) ?? '';
  tokenField.append(tokenLabel, tokenInput);

  const modelField = el('div', 'field');
  const modelLabel = el('label');
  modelLabel.textContent = 'Model';
  const modelInput = el('input') as HTMLInputElement;
  modelInput.type = 'text';
  modelInput.placeholder = 'mistralai/Mistral-7B-Instruct-v0.2';
  modelInput.value = localStorage.getItem(LS_MODEL) ?? 'mistralai/Mistral-7B-Instruct-v0.2';
  modelField.append(modelLabel, modelInput);

  const kField = el('div', 'field');
  const kLabel = el('label');
  kLabel.textContent = 'Top K chunks';
  const kSelect = el('select') as HTMLSelectElement;
  for (const k of [2, 3, 4, 6, 8]) {
    const opt = document.createElement('option');
    opt.value = String(k);
    opt.textContent = String(k);
    kSelect.append(opt);
  }
  kSelect.value = localStorage.getItem(LS_K) ?? '4';
  kField.append(kLabel, kSelect);

  const kbField = el('div', 'field');
  const kbLabel = el('label');
  kbLabel.textContent = 'Knowledge files (.txt/.md)';
  const kbInput = el('input') as HTMLInputElement;
  kbInput.type = 'file';
  kbInput.multiple = true;
  kbInput.accept = '.txt,.md,text/plain,text/markdown';
  const kbHelp = el('div', 'small');
  kbHelp.textContent = 'Optional: upload your own files. If empty, the app uses web/public/knowledge/*.txt shipped with the site.';
  kbField.append(kbLabel, kbInput, kbHelp);

  const btnRow = el('div', 'row');
  const buildBtn = el('button', 'btn') as HTMLButtonElement;
  buildBtn.textContent = 'Build / Rebuild Index';
  const clearBtn = el('button', 'btn danger') as HTMLButtonElement;
  clearBtn.textContent = 'Clear Chat';
  btnRow.append(buildBtn, clearBtn);

  const status = el('div', 'small');
  status.textContent = 'Index: not built.';

  settingsBody.append(tokenField, modelField, kField, kbField, btnRow, status);

  // Right: chat
  const chat = el('section', 'card chat');
  chat.innerHTML = `
    <header>
      <h2>Chat</h2>
      <p>Ask a question. The answer will cite retrieved chunks as [#1], [#2], …</p>
    </header>
  `;

  const messages = el('div', 'messages');
  const composer = el('div', 'composer');

  const question = el('textarea') as HTMLTextAreaElement;
  question.placeholder = 'Ask a question about your knowledge base…';

  const actionRow = el('div', 'row');
  const askBtn = el('button', 'btn') as HTMLButtonElement;
  askBtn.textContent = 'Ask';
  const stopBtn = el('button', 'btn secondary') as HTMLButtonElement;
  stopBtn.textContent = 'Stop';
  stopBtn.disabled = true;

  actionRow.append(askBtn, stopBtn);

  const footer = el('div', 'footer');
  footer.innerHTML = `Built for free hosting on GitHub Pages. Uses Hugging Face Inference API from the browser.`;

  composer.append(question, actionRow, footer);
  chat.append(messages, composer);

  grid.append(settings, chat);
  container.append(header, grid);
  mount.replaceChildren(container);

  function setReady(ready: boolean, text: string) {
    dot.className = ready ? 'dot ok' : 'dot';
    badgeText.textContent = text;
  }

  function setBusy(busy: boolean) {
    state.busy = busy;
    askBtn.disabled = busy;
    buildBtn.disabled = busy;
    stopBtn.disabled = !busy;
  }

  function persistSettings() {
    localStorage.setItem(LS_TOKEN, tokenInput.value);
    localStorage.setItem(LS_MODEL, modelInput.value);
    localStorage.setItem(LS_K, kSelect.value);
  }

  function render() {
    messages.replaceChildren();

    for (const m of state.messages) {
      const wrap = el('div', 'msg');
      const meta = el('div', 'meta');
      meta.textContent = m.role === 'user' ? 'You' : m.role === 'assistant' ? 'Assistant' : 'System';

      const bubble = el('div', `bubble ${m.role === 'user' ? 'user' : 'assistant'}`);
      bubble.textContent = m.content;

      wrap.append(meta, bubble);

      if (m.role === 'assistant' && m.sources && m.sources.length) {
        const src = el('div', 'sources');
        src.innerHTML = `<div style="margin-bottom:6px; color: rgba(255,255,255,0.78)">Sources</div><pre style="margin:0; white-space: pre-wrap;">${escapeHtml(formatSources(m.sources))}</pre>`;
        wrap.append(src);
      }

      messages.append(wrap);
    }

    // scroll to bottom
    messages.scrollTop = messages.scrollHeight;
  }

  async function buildIndex() {
    setBusy(true);
    setReady(false, 'Building index…');
    status.textContent = 'Index: building…';

    try {
      const inputs: Array<{ source: string; text: string }> = [];

      if (kbInput.files && kbInput.files.length > 0) {
        inputs.push(...(await readUploadedFiles(kbInput.files)));
      } else {
        const def = await loadDefaultKnowledge();
        for (const f of def.files) inputs.push({ source: f.name, text: f.text });
      }

      const result = await buildKnowledgeIndexFromTexts(inputs);
      state.index = result.index;

      setReady(true, `Ready: ${result.chunksCount} chunks from ${result.sources.length} source(s)`);
      status.textContent = `Index: built (${result.chunksCount} chunks).`;
    } catch (e) {
      state.index = null;
      setReady(false, 'Index build failed');
      status.textContent = `Index: failed (${String(e)}).`;
    } finally {
      setBusy(false);
      render();
    }
  }

  async function ask() {
    persistSettings();

    if (!state.index) {
      state.messages.push({ role: 'assistant', content: 'Please build the index first (left panel).' });
      render();
      return;
    }

    const token = tokenInput.value.trim();
    if (!token) {
      state.messages.push({ role: 'assistant', content: 'Please paste your Hugging Face token (hf_...) in Settings.' });
      render();
      return;
    }

    const q = question.value.trim();
    if (!q) return;

    const topK = Number(kSelect.value || '4');
    const hits = queryIndex(state.index, q, topK);

    state.messages.push({ role: 'user', content: q });
    render();
    question.value = '';

    const system = 'Answer using the provided context. Be accurate and concise.';
    const prompt = buildPrompt({ system, question: q, hits });

    setBusy(true);
    setReady(true, 'Generating answer…');

    const abort = new AbortController();
    state.abort = abort;

    try {
      const result = await hfGenerateText({
        model: modelInput.value.trim() || 'mistralai/Mistral-7B-Instruct-v0.2',
        token,
        prompt,
        parameters: {
          max_new_tokens: 260,
          temperature: 0.2,
          top_p: 0.95,
          return_full_text: false,
        },
        signal: abort.signal,
      });

      state.messages.push({ role: 'assistant', content: result.text.trim(), sources: hits });
    } catch (e) {
      state.messages.push({ role: 'assistant', content: `Error:\n${explainHfError(e)}` });
    } finally {
      state.abort = undefined;
      setBusy(false);
      setReady(!!state.index, state.index ? 'Ready' : 'Not ready');
      render();
    }
  }

  buildBtn.addEventListener('click', () => buildIndex());
  askBtn.addEventListener('click', () => ask());
  stopBtn.addEventListener('click', () => {
    state.abort?.abort();
  });
  clearBtn.addEventListener('click', () => {
    state.messages = [state.messages[0]];
    render();
  });

  tokenInput.addEventListener('change', persistSettings);
  modelInput.addEventListener('change', persistSettings);
  kSelect.addEventListener('change', persistSettings);

  question.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      void ask();
    }
  });

  // Initial render
  render();
}
