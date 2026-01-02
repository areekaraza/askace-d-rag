export type Chunk = {
  id: string;
  source: string;
  text: string;
};

export type SearchHit = {
  chunk: Chunk;
  score: number;
};

export type TfidfIndex = {
  chunks: Chunk[];
  // Per doc vector: Map(term -> weight)
  vectors: Array<Map<string, number>>;
  idf: Map<string, number>;
};

const WORD_RE = /[\p{L}\p{N}]+/gu;

function tokenize(text: string): string[] {
  const lower = text.toLowerCase();
  const words = lower.match(WORD_RE) ?? [];
  // Very small stopword list (keeps it simple & language-agnostic-ish).
  const stop = new Set([
    'the', 'a', 'an', 'and', 'or', 'to', 'of', 'in', 'is', 'it', 'for', 'on', 'with', 'as', 'at', 'by',
    'be', 'are', 'was', 'were', 'this', 'that', 'these', 'those', 'you', 'your', 'we', 'our', 'i',
  ]);
  return words
    .map((w) => w.trim())
    .filter((w) => w.length >= 2 && w.length <= 40)
    .filter((w) => !stop.has(w));
}

function termFrequencies(tokens: string[]): Map<string, number> {
  const tf = new Map<string, number>();
  for (const t of tokens) tf.set(t, (tf.get(t) ?? 0) + 1);
  return tf;
}

function l2Norm(vec: Map<string, number>): number {
  let sum = 0;
  for (const v of vec.values()) sum += v * v;
  return Math.sqrt(sum);
}

function cosineSim(a: Map<string, number>, b: Map<string, number>): number {
  // iterate smaller map
  const [small, big] = a.size <= b.size ? [a, b] : [b, a];
  let dot = 0;
  for (const [k, av] of small.entries()) {
    const bv = big.get(k);
    if (bv !== undefined) dot += av * bv;
  }
  const denom = l2Norm(a) * l2Norm(b);
  return denom === 0 ? 0 : dot / denom;
}

export function chunkText(source: string, text: string, chunkSize = 900, overlap = 120): Chunk[] {
  const clean = text.replace(/\r\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
  if (!clean) return [];

  const chunks: Chunk[] = [];
  let start = 0;
  let chunkIndex = 0;

  while (start < clean.length) {
    const end = Math.min(clean.length, start + chunkSize);
    let slice = clean.slice(start, end);

    // try to cut on paragraph boundary near the end
    if (end < clean.length) {
      const lastBreak = slice.lastIndexOf('\n\n');
      if (lastBreak > Math.max(120, slice.length * 0.6)) {
        slice = slice.slice(0, lastBreak).trim();
      }
    }

    const id = `${source}::${chunkIndex}`;
    chunks.push({ id, source, text: slice.trim() });

    chunkIndex += 1;
    if (end >= clean.length) break;
    start = Math.max(0, start + chunkSize - overlap);
  }

  return chunks;
}

export function buildTfidfIndex(chunks: Chunk[]): TfidfIndex {
  const docFreq = new Map<string, number>();
  const docTfs: Array<Map<string, number>> = [];

  for (const c of chunks) {
    const tokens = tokenize(c.text);
    const tf = termFrequencies(tokens);
    docTfs.push(tf);

    const seen = new Set<string>();
    for (const term of tf.keys()) {
      if (seen.has(term)) continue;
      seen.add(term);
      docFreq.set(term, (docFreq.get(term) ?? 0) + 1);
    }
  }

  const nDocs = Math.max(1, chunks.length);
  const idf = new Map<string, number>();
  for (const [term, df] of docFreq.entries()) {
    // Smooth IDF
    const value = Math.log((nDocs + 1) / (df + 1)) + 1;
    idf.set(term, value);
  }

  const vectors = docTfs.map((tf) => {
    const vec = new Map<string, number>();
    for (const [term, freq] of tf.entries()) {
      const w = (1 + Math.log(freq)) * (idf.get(term) ?? 0);
      if (w > 0) vec.set(term, w);
    }
    return vec;
  });

  return { chunks, vectors, idf };
}

export function queryIndex(index: TfidfIndex, query: string, topK = 4): SearchHit[] {
  const qTokens = tokenize(query);
  const qTf = termFrequencies(qTokens);
  const qVec = new Map<string, number>();

  for (const [term, freq] of qTf.entries()) {
    const w = (1 + Math.log(freq)) * (index.idf.get(term) ?? 0);
    if (w > 0) qVec.set(term, w);
  }

  const hits: SearchHit[] = [];
  for (let i = 0; i < index.chunks.length; i++) {
    const score = cosineSim(qVec, index.vectors[i]);
    if (score > 0) hits.push({ chunk: index.chunks[i], score });
  }

  hits.sort((a, b) => b.score - a.score);
  return hits.slice(0, Math.max(1, topK));
}
