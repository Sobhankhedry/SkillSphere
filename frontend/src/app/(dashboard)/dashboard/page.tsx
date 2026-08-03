"use client";

import { useState, useEffect } from "react";
import { dashboardAPI } from "@/lib/api";
import { UserDashboard } from "@/types";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { Spinner } from "@/components/ui/Spinner";

export default function DashboardPage() {
  const [data, setData] = useState<UserDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI
      .user()
      .then(({ data }) => setData(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      {data && (
        <>
          <StatsCards
            totalProjects={data.total_projects}
            totalDownloads={data.total_downloads}
            totalComments={data.total_comments}
          />
          <RecentActivity activities={data.recent_activities} />
        </>
      )}
    </div>
  );
}
