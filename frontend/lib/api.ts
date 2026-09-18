const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'https://reachout-smb-backend.onrender.com').replace(/\/$/, '');

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('reachout_token') : null;
  const businessId = typeof window !== 'undefined' ? localStorage.getItem('reachout_business_id') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (businessId) {
    headers['X-Business-Id'] = businessId;
  }

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${API_BASE}${cleanEndpoint}`;
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = `Error: ${response.status} ${response.statusText}`;
    try {
      const errJson = await response.json();
      errorMsg = errJson.detail || errorMsg;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
