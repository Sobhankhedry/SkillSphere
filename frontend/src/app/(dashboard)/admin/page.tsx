"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { dashboardAPI } from "@/lib/api";
import { AdminDashboard } from "@/types";
import { useAuthStore } from "@/store/useAuthStore";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { Users, FolderKanban, MessageSquare, Download } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function AdminPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== "admin") {
      router.replace("/dashboard");
      return;
    }
    dashboardAPI
      .admin()
      .then(({ data }) => setData(data))
      .catch(() => router.replace("/dashboard"))
      .finally(() => setLoading(false));
  }, [user, router]);

  if (loading) {
    return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  }

  if (!data) return null;

  const stats = [
    { label: "Total Users", value: data.total_users, icon: Users, color: "text-blue-600 bg-blue-100" },
    { label: "Total Projects", value: data.total_projects, icon: FolderKanban, color: "text-green-600 bg-green-100" },
    { label: "Total Comments", value: data.total_comments, icon: MessageSquare, color: "text-purple-600 bg-purple-100" },
    { label: "Total Downloads", value: data.total_downloads, icon: Download, color: "text-orange-600 bg-orange-100" },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <h2 className="text-2xl font-bold">Admin Dashboard</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon size={22} />
              </div>
              <div>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-xs text-gray-500">{stat.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="font-semibold mb-4">Daily Registrations (Last 30 days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.daily_registrations}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <h3 className="font-semibold mb-4">Daily Uploads (Last 30 days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.daily_uploads}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}
