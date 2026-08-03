"use client";

import { ProjectForm } from "@/components/projects/ProjectForm";

export default function NewProjectPage() {
  return (
    <div className="max-w-5xl">
      <h2 className="text-2xl font-bold mb-6">Create New Project</h2>
      <ProjectForm mode="create" />
    </div>
  );
}
