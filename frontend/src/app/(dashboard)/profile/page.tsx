"use client";

import { useState, useEffect } from "react";
import { profilesAPI } from "@/lib/api";
import { Profile } from "@/types";
import { useAuthStore } from "@/store/useAuthStore";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { Pencil, ExternalLink, Globe } from "lucide-react";

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [bio, setBio] = useState("");
  const [github, setGithub] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    profilesAPI
      .getMe()
      .then(({ data }) => {
        setProfile(data);
        setBio(data.bio || "");
        setGithub(data.github_link || "");
        setLinkedin(data.linkedin_link || "");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append("bio", bio);
      formData.append("github_link", github);
      formData.append("linkedin_link", linkedin);
      if (avatarFile) formData.append("avatar", avatarFile);
      const { data } = await profilesAPI.updateMe(formData);
      setProfile(data);
      setEditing(false);
    } catch {
      alert("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  }

  if (!profile) return null;

  return (
    <div className="max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">My Profile</h2>
        {!editing && (
          <Button variant="secondary" size="sm" onClick={() => setEditing(true)}>
            <Pencil size={16} className="mr-1" /> Edit
          </Button>
        )}
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-4 mb-6">
          {profile.avatar ? (
            <img
              src={profile.avatar}
              alt={user?.username}
              className="w-20 h-20 rounded-full object-cover"
            />
          ) : (
            <div className="w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center text-2xl font-bold text-blue-600">
              {user?.username?.[0]?.toUpperCase()}
            </div>
          )}
          <div>
            <h3 className="text-xl font-semibold">{user?.username}</h3>
            <p className="text-gray-500">{user?.email}</p>
            <p className="text-xs text-gray-400">
              Member since {new Date(profile.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        {editing ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bio</label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={4}
                maxLength={1000}
                className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              />
            </div>
            <Input
              label="GitHub Link"
              value={github}
              onChange={(e) => setGithub(e.target.value)}
              placeholder="https://github.com/username"
            />
            <Input
              label="LinkedIn Link"
              value={linkedin}
              onChange={(e) => setLinkedin(e.target.value)}
              placeholder="https://linkedin.com/in/username"
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Avatar</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setAvatarFile(e.target.files?.[0] || null)}
                className="text-sm"
              />
            </div>
            <div className="flex gap-3">
              <Button onClick={handleSave} loading={saving}>Save</Button>
              <Button variant="secondary" onClick={() => setEditing(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-1">Bio</h4>
              <p className="text-gray-700 dark:text-gray-300">{profile.bio || "No bio yet."}</p>
            </div>
            <div className="flex gap-4">
              {profile.github_link && (
                <a href={profile.github_link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600">
                  <ExternalLink size={16} /> GitHub
                </a>
              )}
              {profile.linkedin_link && (
                <a href={profile.linkedin_link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600">
                  <Globe size={16} /> LinkedIn
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
