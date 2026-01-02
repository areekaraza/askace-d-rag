export type HfTextGenerationParams = {
  max_new_tokens?: number;
  temperature?: number;
  top_p?: number;
  repetition_penalty?: number;
  return_full_text?: boolean;
};

export type HfGenerateRequest = {
  model: string;
  token: string;
  prompt: string;
  parameters?: HfTextGenerationParams;
  signal?: AbortSignal;
};

export type HfGenerateResult = {
  text: string;
  raw: unknown;
};

const HF_ENDPOINT = 'https://api-inference.huggingface.co/models';

function toErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

export async function hfGenerateText(req: HfGenerateRequest): Promise<HfGenerateResult> {
  const url = `${HF_ENDPOINT}/${encodeURIComponent(req.model)}`;

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${req.token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      inputs: req.prompt,
      parameters: {
        return_full_text: false,
        max_new_tokens: 256,
        temperature: 0.2,
        top_p: 0.95,
        repetition_penalty: 1.05,
        ...(req.parameters ?? {}),
      },
      options: {
        wait_for_model: true,
      },
    }),
    signal: req.signal,
  });

  const contentType = res.headers.get('content-type') ?? '';
  const isJson = contentType.includes('application/json');
  const payload = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    // HF returns useful error payloads; surface them.
    const details = typeof payload === 'string' ? payload : JSON.stringify(payload);
    throw new Error(`Hugging Face request failed (${res.status}): ${details}`);
  }

  // Typical text-generation output: [{ generated_text: "..." }]
  if (Array.isArray(payload) && payload.length > 0 && typeof payload[0]?.generated_text === 'string') {
    return { text: payload[0].generated_text, raw: payload };
  }

  // Some models return { generated_text: "..." }
  if (payload && typeof (payload as any).generated_text === 'string') {
    return { text: (payload as any).generated_text, raw: payload };
  }

  // Fallback to stringifying unknown payload.
  return { text: typeof payload === 'string' ? payload : JSON.stringify(payload), raw: payload };
}

export function explainHfError(err: unknown): string {
  const msg = toErrorMessage(err);
  // Common case: model is loading
  if (msg.includes('is currently loading')) {
    return `${msg}\n\nTip: keep \"wait_for_model\" on (this app does). Try again in ~20-60s.`;
  }
  if (msg.includes('Authorization header is missing') || msg.includes('Invalid credentials')) {
    return `${msg}\n\nTip: paste a valid Hugging Face token (starts with hf_).`;
  }
  return msg;
}
