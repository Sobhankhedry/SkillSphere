export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: "user" | "admin";
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
}

export interface Profile {
  id: string;
  user: User;
  bio: string;
  avatar: string | null;
  github_link: string;
  linkedin_link: string;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface ProjectFile {
  id: string;
  file: string;
  original_filename: string;
  file_type: "pdf" | "zip" | "image";
  file_size: number;
  uploaded_by: string;
  created_at: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  owner: string;
  owner_username: string;
  tags: Tag[];
  files: ProjectFile[];
  visibility: "public" | "private";
  status: "draft" | "published";
  download_count: number;
  comments_count: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  project: string;
  project_title: string;
  author: string;
  author_username: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  sender: string | null;
  sender_username: string | null;
  notification_type: "project_approved" | "new_comment" | "invitation" | "system_message";
  title: string;
  message: string;
  link: string;
  is_read: boolean;
  created_at: string;
}

export interface ActivityLog {
  id: string;
  username: string | null;
  activity_type: string;
  description: string;
  ip_address: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface UserDashboard {
  total_projects: number;
  total_downloads: number;
  total_comments: number;
  recent_activities: ActivityLog[];
}

export interface AdminDashboard {
  total_users: number;
  total_projects: number;
  total_comments: number;
  total_downloads: number;
  daily_registrations: { date: string; count: number }[];
  daily_uploads: { date: string; count: number }[];
}

export interface SearchResults {
  projects: { id: string; title: string; description: string; owner__username: string }[];
  users: { id: string; username: string; first_name: string; last_name: string }[];
  tags: Tag[];
}
