import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface TokenResponse {
  token: string;
  url: string;
  room_name: string;
  identity: string;
}

export async function fetchLiveKitToken(
  language: string,
  sttProvider: string = "sarvam",
  llmProvider: string = "sarvam"
): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/livekit/token", {
    language,
    stt_provider: sttProvider,
    llm_provider: llmProvider,
  });
  return response.data;
}