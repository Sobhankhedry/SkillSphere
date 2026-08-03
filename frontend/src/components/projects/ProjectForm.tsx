"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { projectsAPI, tagsAPI } from "@/lib/api";
import { Tag, Project } from "@/types";
import { X, UserPlus } from "lucide-react";
import { UserSearchInvite } from "./UserSearchInvite";

interface ProjectFormProps {
  project?: Project;
  mode: "create" | "edit";
}

export function ProjectForm({ project, mode }: ProjectFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState(project?.title || "");
  const [description, setDescription] = useState(project?.description || "");
  const [visibility, setVisibility] = useState<string>(project?.visibility || "public");
  const [status, setStatus] = useState<string>(project?.status || "draft");
  const [tagInput, setTagInput] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>(project?.tags.map((t) => t.name) || []);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [invitedUsernames, setInvitedUsernames] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    tagsAPI.list().then(({ data }) => setAllTags(data));
  }, []);

  const filteredTags = allTags.filter(
    (t) => t.name.toLowerCase().includes(tagInput.toLowerCase()) && !selectedTags.includes(t.name)
  );

  const addTag = (name: string) => {
    if (name && !selectedTags.includes(name)) {
      setSelectedTags([...selectedTags, name]);
      setTagInput("");
    }
  };

  const removeTag = (name: string) => {
    setSelectedTags(selectedTags.filter((t) => t !== name));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        title,
        description,
        visibility,
        status,
        tag_names: selectedTags,
        ...(mode === "create" && invitedUsernames.length > 0
          ? { invite_usernames: invitedUsernames }
          : {}),
      };
      if (mode === "create") {
        const { data } = await projectsAPI.create(payload);
        router.push(`/projects/${data.id}`);
      } else if (project) {
        await projectsAPI.update(project.id, payload);
        router.push(`/projects/${project.id}`);
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, string[]> } };
      const msg = axiosErr.response?.data;
      if (msg) {
        const firstKey = Object.keys(msg)[0];
        setError(Array.isArray(msg[firstKey]) ? msg[firstKey][0] : String(msg[firstKey]));
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
        placeholder="Project title"
      />
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={6}
          required
          className="w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          placeholder="Describe your project..."
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Visibility</label>
          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          >
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          >
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tags</label>
        <div className="flex flex-wrap gap-2 mb-2">
          {selectedTags.map((tag) => (
            <span key={tag} className="flex items-center gap-1 px-2.5 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-sm rounded-full">
              {tag}
              <button type="button" onClick={() => removeTag(tag)} className="hover:text-red-600">
                <X size={14} />
              </button>
            </span>
          ))}
        </div>
        <div className="relative">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            placeholder="Type to search or create tags..."
            className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white text-sm"
          />
          {tagInput && (
            <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border rounded-lg shadow-lg max-h-40 overflow-y-auto">
              {filteredTags.map((tag) => (
                <button
                  key={tag.id}
                  type="button"
                  onClick={() => addTag(tag.name)}
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {tag.name}
                </button>
              ))}
              {!selectedTags.includes(tagInput) && (
                <button
                  type="button"
                  onClick={() => addTag(tagInput)}
                  className="block w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Create &quot;{tagInput}&quot;
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      {mode === "create" && (
        <div>
          <UserSearchInvite
            onInvite={(username) => {
              if (!invitedUsernames.includes(username)) {
                setInvitedUsernames([...invitedUsernames, username]);
              }
            }}
            invitedUsernames={invitedUsernames}
          />
          {invitedUsernames.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {invitedUsernames.map((username) => (
                <span
                  key={username}
                  className="flex items-center gap-1 px-2.5 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-sm rounded-full"
                >
                  <UserPlus size={12} />
                  {username}
                  <button
                    type="button"
                    onClick={() => setInvitedUsernames(invitedUsernames.filter((u) => u !== username))}
                    className="hover:text-red-600"
                  >
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="flex gap-3">
        <Button type="submit" loading={loading}>
          {mode === "create" ? "Create Project" : "Save Changes"}
        </Button>
        <Button type="button" variant="secondary" onClick={() => router.back()}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
