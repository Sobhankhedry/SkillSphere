"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Edit2, Trash2, ArrowLeft, User, Users, Check, X } from "lucide-react";
import { projectsAPI, invitationsAPI } from "@/lib/api";
import { Project } from "@/types";
import { useAuthStore } from "@/store/useAuthStore";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { FileUpload } from "@/components/projects/FileUpload";
import { CommentSection } from "@/components/projects/CommentSection";
import { UserSearchInvite } from "@/components/projects/UserSearchInvite";

interface Collaborator {
  id: string;
  username: string;
  status: "pending" | "accepted" | "declined";
  created_at: string;
}

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const { user } = useAuthStore();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);

  useEffect(() => {
    projectsAPI
      .get(id)
      .then(({ data }) => setProject(data))
      .catch(() => router.push("/projects"))
      .finally(() => setLoading(false));
  }, [id, router]);

  useEffect(() => {
    if (project) {
      invitationsAPI.collaborators(id).then(({ data }) => setCollaborators(data));
    }
  }, [id, project]);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this project?")) return;
    try {
      await projectsAPI.delete(id);
      router.push("/projects");
    } catch {
      alert("Failed to delete project");
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  }

  if (!project) return null;

  const isOwner = user?.id === project.owner;
  const isAcceptedCollaborator = collaborators.some(
    (c) => c.username === user?.username && c.status === "accepted"
  );
  const canEdit = isOwner || isAcceptedCollaborator;

  return (
    <div className="max-w-4xl space-y-6">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
        <ArrowLeft size={18} /> Back
      </button>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold">{project.title}</h2>
            <div className="flex items-center gap-2 mt-2 text-sm text-gray-500">
              <User size={14} />
              <span>{project.owner_username}</span>
              <span>&middot;</span>
              <span>{new Date(project.created_at).toLocaleDateString()}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={project.status === "published" ? "success" : "warning"}>
              {project.status}
            </Badge>
            <Badge variant="info">{project.visibility}</Badge>
          </div>
        </div>
        <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap mb-4">
          {project.description}
        </p>
        <div className="flex flex-wrap gap-1.5 mb-4">
          {project.tags.map((tag) => (
            <span key={tag.id} className="px-2.5 py-0.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded-full">
              {tag.name}
            </span>
          ))}
        </div>
        {canEdit && (
          <div className="flex gap-2 pt-4 border-t dark:border-gray-700">
            <Link href={`/projects/${project.id}/edit`}>
              <Button variant="secondary" size="sm">
                <Edit2 size={16} className="mr-1" /> Edit
              </Button>
            </Link>
            {isOwner && (
              <Button variant="danger" size="sm" onClick={handleDelete}>
                <Trash2 size={16} className="mr-1" /> Delete
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Collaborators Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Users size={18} />
          <h3 className="text-lg font-semibold">Collaborators</h3>
        </div>

        {collaborators.length === 0 && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            No collaborators yet. Invite people to work on this project.
          </p>
        )}

        {collaborators.length > 0 && (
          <div className="space-y-2 mb-4">
            {collaborators.map((collab) => (
              <div key={collab.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span className="text-sm font-medium">{collab.username}</span>
                <Badge
                  variant={
                    collab.status === "accepted"
                      ? "success"
                      : collab.status === "pending"
                      ? "warning"
                      : "danger"
                  }
                >
                  {collab.status}
                </Badge>
              </div>
            ))}
          </div>
        )}

        {isOwner && (
          <div className="pt-4 border-t dark:border-gray-700">
            <UserSearchInvite
              onInvite={async (username) => {
                try {
                  await invitationsAPI.send(id, { invitee_username: username });
                  const { data } = await invitationsAPI.collaborators(id);
                  setCollaborators(data);
                } catch {
                  alert("Failed to send invitation");
                }
              }}
              invitedUsernames={collaborators.map((c) => c.username)}
            />
          </div>
        )}
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold mb-4">Files</h3>
        <FileUpload
          projectId={project.id}
          files={project.files}
          onFilesUpdate={(files) => setProject({ ...project, files })}
          canUpload={canEdit}
        />
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <CommentSection projectId={project.id} />
      </div>
    </div>
  );
}
