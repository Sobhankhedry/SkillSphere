"use client";

import { useState, useEffect } from "react";
import { Send, Trash2, Edit2 } from "lucide-react";
import { commentsAPI } from "@/lib/api";
import { Comment } from "@/types";
import { useAuthStore } from "@/store/useAuthStore";

interface CommentSectionProps {
  projectId: string;
}

export function CommentSection({ projectId }: CommentSectionProps) {
  const { user } = useAuthStore();
  const [comments, setComments] = useState<Comment[]>([]);
  const [content, setContent] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchComments = async () => {
    try {
      const { data } = await commentsAPI.list(projectId);
      setComments(data.results || data);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchComments();
  }, [projectId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    setLoading(true);
    try {
      await commentsAPI.create({ project: projectId, content });
      setContent("");
      fetchComments();
    } catch {
      alert("Failed to post comment");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (id: string) => {
    try {
      await commentsAPI.update(id, { content: editContent });
      setEditingId(null);
      fetchComments();
    } catch {
      alert("Failed to update comment");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this comment?")) return;
    try {
      await commentsAPI.delete(id);
      fetchComments();
    } catch {
      alert("Failed to delete comment");
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Comments ({comments.length})</h3>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write a comment..."
          className="flex-1 px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white text-sm"
        />
        <button
          type="submit"
          disabled={loading || !content.trim()}
          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Send size={18} />
        </button>
      </form>
      <div className="space-y-3">
        {comments.map((comment) => (
          <div key={comment.id} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-blue-600">{comment.author_username}</span>
              <span className="text-xs text-gray-500">
                {new Date(comment.created_at).toLocaleDateString()}
              </span>
            </div>
            {editingId === comment.id ? (
              <div className="flex gap-2">
                <input
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="flex-1 px-2 py-1 border rounded text-sm bg-white dark:bg-gray-700 dark:text-white"
                />
                <button onClick={() => handleUpdate(comment.id)} className="text-green-600 text-sm">Save</button>
                <button onClick={() => setEditingId(null)} className="text-gray-500 text-sm">Cancel</button>
              </div>
            ) : (
              <p className="text-sm text-gray-700 dark:text-gray-300">{comment.content}</p>
            )}
            {user?.id === comment.author && editingId !== comment.id && (
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => { setEditingId(comment.id); setEditContent(comment.content); }}
                  className="text-xs text-gray-500 hover:text-blue-600"
                >
                  <Edit2 size={14} />
                </button>
                <button
                  onClick={() => handleDelete(comment.id)}
                  className="text-xs text-gray-500 hover:text-red-600"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
