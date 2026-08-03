"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search, Bell, Menu, X, Sun, Moon } from "lucide-react";
import { useAuthStore } from "@/store/useAuthStore";
import { useTheme } from "@/store/useThemeStore";
import { notificationsAPI } from "@/lib/api";

interface TopbarProps {
  onMenuToggle: () => void;
  menuOpen: boolean;
}

export function Topbar({ onMenuToggle, menuOpen }: TopbarProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [unreadCount, setUnreadCount] = useState(0);
  const { dark, toggle, mounted } = useTheme();

  useEffect(() => {
    const fetchCount = async () => {
      try {
        const { data } = await notificationsAPI.unreadCount();
        setUnreadCount(data.count);
      } catch {
        // ignore
      }
    };
    fetchCount();
    const interval = setInterval(fetchCount, 30000);

    // Listen for when notifications page marks all as read
    const handleNotificationsRead = () => fetchCount();
    window.addEventListener("notifications-read", handleNotificationsRead);

    return () => {
      clearInterval(interval);
      window.removeEventListener("notifications-read", handleNotificationsRead);
    };
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
      <div className="flex items-center justify-between h-16 px-4 lg:px-6">
        <button onClick={onMenuToggle} className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <form onSubmit={handleSearch} className="hidden sm:flex flex-1 max-w-md mx-4">
          <div className="relative w-full">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search projects, users..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </form>
        <div className="flex items-center gap-1">
          {mounted && (
            <button
              onClick={toggle}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              title={dark ? "Switch to light mode" : "Switch to dark mode"}
            >
              {dark ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          )}
          <Link
            href="/notifications"
            className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Bell size={22} />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                {unreadCount > 99 ? "99+" : unreadCount}
              </span>
            )}
          </Link>
        </div>
      </div>
    </header>
  );
}
