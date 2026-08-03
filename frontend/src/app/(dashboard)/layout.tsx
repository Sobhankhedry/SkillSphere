"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { useAuthStore } from "@/store/useAuthStore";
import { profilesAPI } from "@/lib/api";
import Link from "next/link";
import { X } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, setUser, isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!user && isAuthenticated()) {
      profilesAPI.getMe().then(({ data }) => {
        setUser(data.user || data);
      }).catch(() => {
        router.replace("/login");
      });
    }
  }, [user, setUser, isAuthenticated, router]);

  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-950">
        <Sidebar />
        {menuOpen && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <div className="absolute inset-0 bg-black/50" onClick={() => setMenuOpen(false)} />
            <div className="absolute left-0 top-0 h-full w-64 bg-white dark:bg-gray-900 shadow-xl z-50">
              <div className="flex items-center justify-between p-4">
                <h1 className="text-xl font-bold text-blue-600">SkillSphere</h1>
                <button onClick={() => setMenuOpen(false)} className="p-1">
                  <X size={20} />
                </button>
              </div>
              <nav className="px-3 space-y-1">
                {[
                  { href: "/dashboard", label: "Dashboard" },
                  { href: "/projects", label: "My Projects" },
                  { href: "/explore", label: "Explore" },
                  { href: "/notifications", label: "Notifications" },
                  { href: "/search", label: "Search" },
                  ...(user?.role === "admin" ? [{ href: "/admin", label: "Admin" }] : []),
                ].map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMenuOpen(false)}
                    className="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        )}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Topbar onMenuToggle={() => setMenuOpen(!menuOpen)} menuOpen={menuOpen} />
          <main className="flex-1 overflow-y-auto p-4 lg:p-6">
            {children}
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
