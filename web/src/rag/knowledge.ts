import { buildTfidfIndex, chunkText, type Chunk, type TfidfIndex } from './tfidf';

export type KnowledgeBuildResult = {
  index: TfidfIndex;
  sources: string[];
  chunksCount: number;
};

async function safeFetchText(url: string): Promise<string | null> {
  const res = await fetch(url, { cache: 'no-cache' });
  if (!res.ok) return null;
  return await res.text();
}

export async function loadDefaultKnowledge(): Promise<{ files: Array<{ name: string; text: string }> }> {
  // GitHub Pages static hosting does not allow directory listing,
  // so we keep a tiny explicit manifest.
  const manifestUrl = `${import.meta.env.BASE_URL}knowledge/manifest.json`;
  const manifestText = await safeFetchText(manifestUrl);

  if (!manifestText) {
    // Fallback: try a single sample
    const sampleUrl = `${import.meta.env.BASE_URL}knowledge/sample.txt`;
    const sample = await safeFetchText(sampleUrl);
    return { files: sample ? [{ name: 'knowledge/sample.txt', text: sample }] : [] };
  }

  const manifest = JSON.parse(manifestText) as { files: string[] };
  const files: Array<{ name: string; text: string }> = [];

  for (const path of manifest.files) {
    const url = `${import.meta.env.BASE_URL}${path}`;
    const txt = await safeFetchText(url);
    if (txt) files.push({ name: path, text: txt });
  }

  return { files };
}

export async function buildKnowledgeIndexFromTexts(
  inputs: Array<{ source: string; text: string }>,
  opts?: { chunkSize?: number; overlap?: number }
): Promise<KnowledgeBuildResult> {
  const chunkSize = opts?.chunkSize ?? 900;
  const overlap = opts?.overlap ?? 120;

  const allChunks: Chunk[] = [];
  for (const f of inputs) {
    const chunks = chunkText(f.source, f.text, chunkSize, overlap);
    allChunks.push(...chunks);
  }

  const index = buildTfidfIndex(allChunks);
  const sources = Array.from(new Set(allChunks.map((c) => c.source)));
  return { index, sources, chunksCount: allChunks.length };
}
