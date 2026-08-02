import axios from "axios";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120_000, // SLM üretimi birkaç saniye sürebilir
});

export interface RiskMatch {
  belgedeki_madde: string;
  madde_turu: string;
  eslesen_riskli_madde: string;
  validity: string;
  aciklama: string;
  benzerlik_skoru: number;
}

export interface UploadResponse {
  message: string;
  filename: string;
  ocr_text: string;
  chunk_count: number;
  risk_match_count: number;
  risk_matches: RiskMatch[];
  ai_summary: string | null;
  ai_summary_error: string | null;
}

export interface ChatContextMatch {
  eslesen_madde: string;
  validity: string;
  benzerlik_skoru: number;
}

export interface ChatResponse {
  reply: string;
  context_matches: ChatContextMatch[];
}

export interface HealthResponse {
  api: string;
  slm: {
    ollama_reachable: boolean;
    model_loaded: boolean;
    expected_model?: string;
    available_models?: string[];
    error?: string;
  };
}

/** Belge/görsel yükleyip OCR + RAG risk analizi ve SLM özetini alır. */
export async function analyzeDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await api.post<UploadResponse>("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return data;
}

/** Serbest metin sohbeti; backend RAG ile ilgili bağlamı bulup SLM'e sorar. */
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/chat", { message });
  return data;
}

/** Backend + SLM (Ollama) durumunu kontrol eder. */
export async function checkHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>("/health");
  return data;
}

/** axios/network hatalarını kullanıcıya gösterilebilir bir mesaja çevirir. */
export function toErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) {
      return String(error.response.data.detail);
    }
    if (error.code === "ECONNABORTED") {
      return "İstek zaman aşımına uğradı. SLM sunucusu meşgul olabilir.";
    }
    if (!error.response) {
      return "Backend sunucusuna ulaşılamadı. API'nin çalıştığından emin olun.";
    }
  }
  return "Beklenmeyen bir hata oluştu.";
}
