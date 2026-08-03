"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, FolderOpen, Users } from "lucide-react";
import { projectsAPI } from "@/lib/api";
import { Project, PaginatedResponse } from "@/types";
import { ProjectCard } from "@/components/projects/ProjectCard";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";

type Tab = "owned" | "collaborating";

export default function MyProjectsPage() {
  const [tab, setTab] = useState<Tab>("owned");
  const [ownedProjects, setOwnedProjects] = useState<Project[]>([]);
  const [collabProjects, setCollabProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");

    Promise.all([
      projectsAPI.myProjects().catch(() => ({ data: { results: [] } })),
      projectsAPI.collaborating().catch(() => ({ data: { results: [] } })),
    ])
      .then(([ownedRes, collabRes]) => {
        const ownedData = ownedRes.data as PaginatedResponse<Project>;
        const collabData = collabRes.data as PaginatedResponse<Project>;
        setOwnedProjects(ownedData.results || ownedData || []);
        setCollabProjects(collabData.results || collabData || []);
      })
      .catch(() => setError("Failed to load projects."))
      .finally(() => setLoading(false));
  }, []);

  const activeProjects = tab === "owned" ? ownedProjects : collabProjects;

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">My Projects</h2>
        <Link href="/projects/new">
          <Button>
            <Plus size={18} className="mr-2" />
            New Project
          </Button>
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b dark:border-gray-700">
        <button
          onClick={() => setTab("owned")}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "owned"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <FolderOpen size={16} />
          Owned ({ownedProjects.length})
        </button>
        <button
          onClick={() => setTab("collaborating")}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "collaborating"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <Users size={16} />
          Collaborating ({collabProjects.length})
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      ) : activeProjects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">
            {tab === "owned"
              ? "You haven&apos;t created any projects yet."
              : "You haven&apos;t been invited to any projects yet."}
          </p>
          {tab === "owned" && (
            <Link href="/projects/new"><Button>Create Your First Project</Button></Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {activeProjects.map((p) => <ProjectCard key={p.id} project={p} />)}
        </div>
      )}
    </div>
  );
}
