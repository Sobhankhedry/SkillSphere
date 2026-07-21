import { ActivityLog } from "@/types";

const activityIcons: Record<string, string> = {
  login: "🔑",
  logout: "👋",
  project_created: "📁",
  project_updated: "✏️",
  project_deleted: "🗑️",
  file_uploaded: "📤",
  file_downloaded: "📥",
  comment_created: "💬",
  api_request: "🌐",
};

export function RecentActivity({ activities }: { activities: ActivityLog[] }) {
  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">Recent Activity</h3>
      {activities.length === 0 && (
        <p className="text-sm text-gray-500">No recent activity.</p>
      )}
      {activities.map((activity) => (
        <div
          key={activity.id}
          className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          <span className="text-xl mt-0.5">{activityIcons[activity.activity_type] || "📌"}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm">{activity.description}</p>
            <p className="text-xs text-gray-500 mt-1">
              {new Date(activity.created_at).toLocaleString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
