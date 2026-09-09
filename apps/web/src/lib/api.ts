const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: (batchId?: string) =>
    request(`/dashboard${batchId ? `?batch_id=${encodeURIComponent(batchId)}` : ""}`),
  meta: () => request("/meta"),
  exceptions: (params: Record<string, string | undefined>) => {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value) search.set(key, value);
    });
    const suffix = search.toString();
    return request(`/exceptions${suffix ? `?${suffix}` : ""}`);
  },
  exception: (id: string) => request(`/exceptions/${id}`),
  resolve: (id: string, body: Record<string, string | null>) =>
    request(`/exceptions/${id}/resolve`, { method: "POST", body: JSON.stringify(body) }),
  investigate: (id: string) => request(`/exceptions/${id}/investigate`, { method: "POST" }),
  insights: (batchId?: string) =>
    request(`/insights${batchId ? `?batch_id=${encodeURIComponent(batchId)}` : ""}`),
  improvements: () => request("/improvements"),
  improvement: (id: string) => request(`/improvements/${id}`),
  updateImprovement: (id: string, status: string) =>
    request(`/improvements/${id}/status`, { method: "POST", body: JSON.stringify({ status }) }),
  importBatch: async (file: File) => {
    const data = new FormData();
    data.append("file", file);
    const response = await fetch(`${API_BASE}/batches/import`, { method: "POST", body: data });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  },
};
