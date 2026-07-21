import { FolderKanban, Download, MessageSquare } from "lucide-react";
import { Card } from "@/components/ui/Card";

interface StatsCardsProps {
  totalProjects: number;
  totalDownloads: number;
  totalComments: number;
}

export function StatsCards({ totalProjects, totalDownloads, totalComments }: StatsCardsProps) {
  const stats = [
    { label: "Projects", value: totalProjects, icon: FolderKanban, color: "text-blue-600 bg-blue-100 dark:bg-blue-900/30" },
    { label: "Downloads", value: totalDownloads, icon: Download, color: "text-green-600 bg-green-100 dark:bg-green-900/30" },
    { label: "Comments", value: totalComments, icon: MessageSquare, color: "text-purple-600 bg-purple-100 dark:bg-purple-900/30" },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <div className="flex items-center gap-4">
            <div className={`p-3 rounded-lg ${stat.color}`}>
              <stat.icon size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-sm text-gray-500">{stat.label}</p>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
