"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Bell } from "lucide-react";
import { notificationsAPI } from "@/lib/api";
import { connectWebSocket, disconnectWebSocket } from "@/lib/websocket";
import { useAuthStore } from "@/store/useAuthStore";

export function NotificationBell() {
  const { accessToken } = useAuthStore();
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchCount = async () => {
    try {
      const { data } = await notificationsAPI.unreadCount();
      setUnreadCount(data.count);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchCount();

    if (accessToken) {
      connectWebSocket(accessToken, () => {
        setUnreadCount((prev) => prev + 1);
      });
    }

    const interval = setInterval(fetchCount, 30000);

    // Listen for when notifications page marks all as read
    const handleNotificationsRead = () => fetchCount();
    window.addEventListener("notifications-read", handleNotificationsRead);

    return () => {
      clearInterval(interval);
      disconnectWebSocket();
      window.removeEventListener("notifications-read", handleNotificationsRead);
    };
  }, [accessToken]);

  return (
    <Link href="/notifications" className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
      <Bell size={22} />
      {unreadCount > 0 && (
        <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </Link>
  );
}
