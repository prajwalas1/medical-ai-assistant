import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

export interface TokenResponse {
  token: string;
  url: string;
  room_name: string;
  identity: string;
}

export async function fetchLiveKitToken(
  language: string
): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/livekit/token", {
    language,
  });
  return response.data;
}