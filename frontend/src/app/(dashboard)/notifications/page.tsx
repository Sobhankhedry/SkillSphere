"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { CheckCheck, Bell, Check, X } from "lucide-react";
import { notificationsAPI, invitationsAPI } from "@/lib/api";
import { Notification, PaginatedResponse } from "@/types";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { Badge } from "@/components/ui/Badge";

const typeLabels: Record<string, string> = {
  new_comment: "New Comment",
  invitation: "Invitation",
  system_message: "System",
};

function extractProjectId(link: string): string | null {
  const match = link.match(/\/projects\/([a-f0-9-]+)/i);
  return match ? match[1] : null;
}

interface InvitationStatus {
  id: string;
  project: string;
  status: "pending" | "accepted" | "declined";
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  // Map of projectId -> invitation status, fetched from API so it survives navigation
  const [invitationStatuses, setInvitationStatuses] = useState<Map<string, string>>(new Map());

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const params = unreadOnly ? { unread_only: true } : undefined;
      const { data } = await notificationsAPI.list(params);
      const res = data as PaginatedResponse<Notification>;
      setNotifications(res.results || data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchInvitationStatuses = async () => {
    try {
      const { data: invitations } = await invitationsAPI.list();
      const results = (invitations.results || invitations) as InvitationStatus[];
      const map = new Map<string, string>();
      for (const inv of results) {
        map.set(inv.project, inv.status);
      }
      setInvitationStatuses(map);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchNotifications();
    fetchInvitationStatuses();
  }, [unreadOnly]);

  // When entering the page, immediately mark all as read on server and update bell
  useEffect(() => {
    notificationsAPI.markAllRead().catch(() => {});
    window.dispatchEvent(new Event("notifications-read"));
  }, []);

  const handleMarkRead = async (id: string) => {
    await notificationsAPI.markRead(id);
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
    window.dispatchEvent(new Event("notifications-read"));
  };

  const handleMarkAllRead = async () => {
    await notificationsAPI.markAllRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    window.dispatchEvent(new Event("notifications-read"));
  };

  const getInvitationStatus = (notification: Notification): "pending" | "accepted" | "declined" | null => {
    if (notification.notification_type !== "invitation") return null;
    const projectId = extractProjectId(notification.link);
    if (!projectId) return null;
    return (invitationStatuses.get(projectId) as "pending" | "accepted" | "declined") || null;
  };

  const handleAcceptInvitation = async (notification: Notification) => {
    const projectId = extractProjectId(notification.link);
    if (!projectId) return;

    setActionLoading(notification.id);
    try {
      const { data: invitations } = await invitationsAPI.list();
      const results = (invitations.results || invitations) as InvitationStatus[];
      const invitation = results.find(
        (inv) => inv.project === projectId && inv.status === "pending"
      );
      if (invitation) {
        await invitationsAPI.accept(invitation.id);
        await notificationsAPI.markRead(notification.id);
        setNotifications((prev) =>
          prev.map((n) =>
            n.id === notification.id ? { ...n, is_read: true } : n
          )
        );
        setInvitationStatuses((prev) => new Map(prev).set(projectId, "accepted"));
        window.dispatchEvent(new Event("notifications-read"));
      }
    } catch {
      alert("Failed to accept invitation");
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeclineInvitation = async (notification: Notification) => {
    const projectId = extractProjectId(notification.link);
    if (!projectId) return;

    setActionLoading(notification.id);
    try {
      const { data: invitations } = await invitationsAPI.list();
      const results = (invitations.results || invitations) as InvitationStatus[];
      const invitation = results.find(
        (inv) => inv.project === projectId && inv.status === "pending"
      );
      if (invitation) {
        await invitationsAPI.decline(invitation.id);
        await notificationsAPI.markRead(notification.id);
        setNotifications((prev) =>
          prev.map((n) =>
            n.id === notification.id ? { ...n, is_read: true } : n
          )
        );
        setInvitationStatuses((prev) => new Map(prev).set(projectId, "declined"));
        window.dispatchEvent(new Event("notifications-read"));
      }
    } catch {
      alert("Failed to decline invitation");
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Notifications</h2>
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => setUnreadOnly(!unreadOnly)}>
            {unreadOnly ? "Show All" : "Unread Only"}
          </Button>
          <Button variant="secondary" size="sm" onClick={handleMarkAllRead}>
            <CheckCheck size={16} className="mr-1" /> Mark All Read
          </Button>
        </div>
      </div>
      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-12">
          <Bell size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No notifications.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => {
            const isInvitation = n.notification_type === "invitation";
            const invStatus = getInvitationStatus(n);
            const isPending = invStatus === "pending";
            const hasActed = isInvitation && invStatus !== null && invStatus !== "pending";
            const showInviteButtons = isInvitation && isPending;

            return (
              <div
                key={n.id}
                onClick={() => !n.is_read && !showInviteButtons && handleMarkRead(n.id)}
                className={`p-4 rounded-lg border transition-colors ${
                  showInviteButtons
                    ? "bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700"
                    : n.is_read
                    ? "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700"
                    : "bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800"
                } ${showInviteButtons ? "" : "cursor-pointer"}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-sm">{n.title}</h4>
                      <Badge variant={isInvitation ? "info" : n.is_read ? "default" : "info"}>
                        {typeLabels[n.notification_type] || n.notification_type}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{n.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(n.created_at).toLocaleString()}
                    </p>
                  </div>
                  {!n.is_read && !showInviteButtons && (
                    <div className="w-2.5 h-2.5 bg-blue-500 rounded-full mt-1.5 ml-2 shrink-0" />
                  )}
                </div>

                {showInviteButtons && (
                  <div className="flex gap-2 mt-3">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAcceptInvitation(n);
                      }}
                      loading={actionLoading === n.id}
                    >
                      <Check size={14} className="mr-1" /> Accept
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeclineInvitation(n);
                      }}
                      loading={actionLoading === n.id}
                    >
                      <X size={14} className="mr-1" /> Decline
                    </Button>
                  </div>
                )}

                {hasActed && (
                  <p className="text-xs mt-2 italic flex items-center gap-1">
                    {invStatus === "accepted" ? (
                      <span className="text-green-600 dark:text-green-400">You accepted this project ✓</span>
                    ) : (
                      <span className="text-red-500 dark:text-red-400">You declined this project ✓</span>
                    )}
                  </p>
                )}

                {n.link && !isInvitation && (
                  <Link
                    href={n.link}
                    className="text-xs text-blue-600 hover:underline mt-2 inline-block"
                    onClick={(e) => e.stopPropagation()}
                  >
                    View details
                  </Link>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
