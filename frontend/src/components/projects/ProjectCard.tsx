import Link from "next/link";
import { Calendar, Download, MessageSquare } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Project } from "@/types";

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Link href={`/projects/${project.id}`} className="block group">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold group-hover:text-blue-600 transition-colors line-clamp-1">
            {project.title}
          </h3>
          <Badge variant={project.status === "published" ? "success" : "warning"}>
            {project.status}
          </Badge>
        </div>
        <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2 mb-4">
          {project.description}
        </p>
        <div className="flex flex-wrap gap-1.5 mb-4">
          {project.tags.map((tag) => (
            <span
              key={tag.id}
              className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded-full"
            >
              {tag.name}
            </span>
          ))}
        </div>
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Download size={14} />
              {project.download_count}
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare size={14} />
              {project.comments_count}
            </span>
          </div>
          <span className="flex items-center gap-1">
            <Calendar size={14} />
            {new Date(project.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </Link>
  );
}
