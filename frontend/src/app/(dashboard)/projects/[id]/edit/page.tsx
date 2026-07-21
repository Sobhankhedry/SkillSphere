"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { projectsAPI } from "@/lib/api";
import { Project } from "@/types";
import { ProjectForm } from "@/components/projects/ProjectForm";
import { Spinner } from "@/components/ui/Spinner";

export default function EditProjectPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsAPI
      .get(id)
      .then(({ data }) => setProject(data))
      .catch(() => router.push("/projects"))
      .finally(() => setLoading(false));
  }, [id, router]);

  if (loading) {
    return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  }

  if (!project) return null;

  return (
    <div className="max-w-5xl">
      <h2 className="text-2xl font-bold mb-6">Edit Project</h2>
      <ProjectForm project={project} mode="edit" />
    </div>
  );
}
