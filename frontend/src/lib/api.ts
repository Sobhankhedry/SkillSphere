import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("auth-storage");
    if (stored) {
      const { state } = JSON.parse(stored);
      if (state?.accessToken) {
        config.headers.Authorization = `Bearer ${state.accessToken}`;
      }
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    console.error("[API] Response error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers,
      code: error.code,
      message: error.message,
    });
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const stored = localStorage.getItem("auth-storage");
      if (stored) {
        const { state } = JSON.parse(stored);
        if (state?.refreshToken) {
          try {
            const { data } = await axios.post(
              `${process.env.NEXT_PUBLIC_API_URL}/auth/token/refresh/`,
              { refresh: state.refreshToken }
            );
            const newStored = JSON.parse(localStorage.getItem("auth-storage") || "{}");
            newStored.state = { ...newStored.state, accessToken: data.access };
            localStorage.setItem("auth-storage", JSON.stringify(newStored));
            originalRequest.headers.Authorization = `Bearer ${data.access}`;
            return api(originalRequest);
          } catch {
            localStorage.removeItem("auth-storage");
            window.location.href = "/login";
          }
        } else {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export const authAPI = {
  register: (data: {
    email: string;
    username: string;
    password: string;
    password_confirm: string;
    first_name?: string;
    last_name?: string;
  }) => api.post("/auth/register/", data),

  login: (data: { email: string; password: string }) =>
    api.post("/auth/login/", data),

  googleLogin: (accessToken: string) =>
    api.post("/auth/google/", { access_token: accessToken }),

  refreshToken: (refresh: string) =>
    api.post("/auth/token/refresh/", { refresh }),

  logout: (refresh: string) => api.post("/auth/logout/", { refresh }),
};

export const profilesAPI = {
  getMe: () => api.get("/users/profiles/me/"),
  updateMe: (data: FormData) => api.patch("/users/profiles/me/", data),
  getByUsername: (username: string) =>
    api.get(`/users/profiles/by_username/?username=${username}`),
  search: (q: string) =>
    api.get(`/users/profiles/search/`, { params: { q } }),
};

export const projectsAPI = {
  list: (params?: Record<string, string>) =>
    api.get("/projects/", { params }),
  myProjects: () => api.get("/projects/my_projects/"),
  collaborating: () => api.get("/projects/collaborating/"),
  get: (id: string) => api.get(`/projects/${id}/`),
  create: (data: {
    title: string;
    description: string;
    visibility?: string;
    status?: string;
    tag_names?: string[];
    invite_usernames?: string[];
  }) => api.post("/projects/", data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/projects/${id}/`, data),
  delete: (id: string) => api.delete(`/projects/${id}/`),
  getFiles: (id: string) => api.get(`/projects/${id}/files/`),
  uploadFile: (id: string, formData: FormData) =>
    api.post(`/projects/${id}/upload_file/`, formData),
  downloadFile: (projectId: string, fileId: string) =>
    api.get(`/projects/${projectId}/download/${fileId}/`, {
      responseType: "blob",
    }),
};

export const tagsAPI = {
  list: () => api.get("/projects/tags/"),
};

export const commentsAPI = {
  list: (projectId: string) =>
    api.get("/comments/", { params: { project: projectId } }),
  create: (data: { project: string; content: string }) =>
    api.post("/comments/", data),
  update: (id: string, data: { content: string }) =>
    api.patch(`/comments/${id}/`, data),
  delete: (id: string) => api.delete(`/comments/${id}/`),
};

export const notificationsAPI = {
  list: (params?: { unread_only?: boolean }) =>
    api.get("/notifications/", { params }),
  unreadCount: () => api.get("/notifications/unread_count/"),
  markRead: (id: string) => api.patch(`/notifications/${id}/mark_read/`),
  markAllRead: () => api.patch("/notifications/mark_all_read/"),
};

export const dashboardAPI = {
  user: () => api.get("/dashboard/user/"),
  admin: () => api.get("/dashboard/admin/"),
};

export const searchAPI = {
  global: (q: string) => api.get("/search/", { params: { q } }),
  projects: (q: string) => api.get("/search/projects/", { params: { q } }),
  users: (q: string) => api.get("/search/users/", { params: { q } }),
};

export const invitationsAPI = {
  list: () => api.get("/projects/invitations/"),
  pending: () => api.get("/projects/invitations/pending/"),
  sent: () => api.get("/projects/invitations/sent/"),
  accept: (id: string) => api.post(`/projects/invitations/${id}/accept/`),
  decline: (id: string) => api.post(`/projects/invitations/${id}/decline/`),
  send: (projectId: string, data: { invitee_username: string; message?: string }) =>
    api.post(`/projects/${projectId}/invite/`, data),
  collaborators: (projectId: string) =>
    api.get(`/projects/${projectId}/collaborators/`),
};
