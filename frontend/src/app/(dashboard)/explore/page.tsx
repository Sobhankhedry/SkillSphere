"use client";

import { useState, useEffect } from "react";
import { projectsAPI } from "@/lib/api";
import { Project, PaginatedResponse } from "@/types";
import { ProjectCard } from "@/components/projects/ProjectCard";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { Search } from "lucide-react";

export default function ExplorePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    setLoading(true);
    const params: Record<string, string> = { page: String(page) };
    if (search) params.search = search;
    projectsAPI
      .list(params)
      .then(({ data }) => {
        const res = data as PaginatedResponse<Project>;
        setProjects(res.results || data);
        setTotalPages(Math.ceil((res.count || 0) / 20));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, search]);

  return (
    <div className="space-y-6 max-w-5xl">
      <h2 className="text-2xl font-bold">Explore Projects</h2>
      <div className="relative max-w-md">
        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search projects..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-800 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : projects.length === 0 ? (
        <p className="text-center text-gray-500 py-12">No projects found.</p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p) => <ProjectCard key={p.id} project={p} />)}
          </div>
          {totalPages > 1 && (
            <div className="flex justify-center gap-2">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <Button key={p} variant={p === page ? "primary" : "secondary"} size="sm" onClick={() => setPage(p)}>
                  {p}
                </Button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
