const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    // FastAPI errors are JSON: { "detail": "..." }
    try {
      const json = JSON.parse(text);
      throw new Error(json.detail || text || `HTTP ${response.status}`);
    } catch (e) {
      if (e instanceof SyntaxError) throw new Error(text || `HTTP ${response.status}`);
      throw e;
    }
  }
  return response.json() as Promise<T>;
}

export async function createApplication(payload: Record<string, any>, resumeFile?: File) {
  const formData = new FormData();
  formData.append("full_name", payload.full_name);
  formData.append("email", payload.email);
  formData.append("github_url", payload.github_url);
  formData.append("role_applied", payload.role_applied);
  if (payload.personal_json) formData.append("personal_json", payload.personal_json);
  if (payload.education_json) formData.append("education_json", payload.education_json);
  if (payload.experience_json) formData.append("experience_json", payload.experience_json);
  if (payload.professional_json) formData.append("professional_json", payload.professional_json);
  if (payload.motivation_json) formData.append("motivation_json", payload.motivation_json);
  if (resumeFile) formData.append("resume_file", resumeFile);

  const response = await fetch(`${BASE_URL}/applications`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(response);
}

export async function getApplications() {
  const response = await fetch(`${BASE_URL}/applications`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  return handleResponse<any[]>(response);
}

export async function getApplicationById(id: string | number) {
  const response = await fetch(`${BASE_URL}/applications/${id}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  return handleResponse<any>(response);
}

export async function getApplicationStats() {
  const response = await fetch(`${BASE_URL}/applications/stats`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  return handleResponse<{
    total_applications: number;
    pending_review: number;
    accepted: number;
    rejected: number;
    new_this_week: number;
  }>(response);
}

export async function generatePlan(
  id: string | number,
  options?: { weeks?: number; daily_hours?: number; target_role?: string }
) {
  const response = await fetch(
    `${BASE_URL}/applications/${id}/generate-plan`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(options ?? {}),
    }
  );
  return handleResponse<any>(response);
}

export async function modifyPlan(id: string | number, message: string) {
  const response = await fetch(
    `${BASE_URL}/applications/${id}/modify-plan`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    }
  );
  return handleResponse<any>(response);
}

export async function updateStatus(
  id: string | number,
  status: "in_review" | "accepted" | "rejected" | "intern"
) {
  const response = await fetch(`${BASE_URL}/applications/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  return handleResponse<any>(response);
}

export async function verifyApplication(id: string | number) {
  const response = await fetch(`${BASE_URL}/applications/${id}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  return handleResponse<any>(response);
}
