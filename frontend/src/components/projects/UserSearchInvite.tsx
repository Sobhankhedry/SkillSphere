"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { X, UserPlus, Search } from "lucide-react";
import { profilesAPI } from "@/lib/api";

interface UserSearchResult {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
}

interface UserSearchInviteProps {
  onInvite: (username: string) => void;
  invitedUsernames: string[];
}

export function UserSearchInvite({ onInvite, invitedUsernames }: UserSearchInviteProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<UserSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const search = useCallback((q: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!q.trim()) {
      setResults([]);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const { data } = await profilesAPI.search(q);
        setResults(data.filter((u: UserSearchResult) => !invitedUsernames.includes(u.username)));
        setOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, [invitedUsernames]);

  const handleSelect = (username: string) => {
    onInvite(username);
    setQuery("");
    setResults([]);
    setOpen(false);
  };

  return (
    <div ref={wrapperRef} className="relative">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Invite Collaborators
      </label>
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            search(e.target.value);
          }}
          onFocus={() => query.trim() && results.length > 0 && setOpen(true)}
          placeholder="Search username to invite..."
          className="w-full pl-9 pr-3 py-2 border rounded-lg bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white text-sm"
        />
        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="animate-spin h-4 w-4 border-2 border-gray-300 border-t-blue-600 rounded-full" />
          </div>
        )}
      </div>
      {open && results.length > 0 && (
        <div className="absolute z-20 w-full mt-1 bg-white dark:bg-gray-800 border dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
          {results.map((user) => (
            <button
              key={user.id}
              type="button"
              onClick={() => handleSelect(user.username)}
              className="flex items-center gap-3 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <UserPlus size={14} className="text-gray-400" />
              <div>
                <span className="font-medium">{user.username}</span>
                {(user.first_name || user.last_name) && (
                  <span className="text-gray-500 dark:text-gray-400 ml-2">
                    {user.first_name} {user.last_name}
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
      {open && query.trim() && results.length === 0 && !loading && (
        <div className="absolute z-20 w-full mt-1 bg-white dark:bg-gray-800 border dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm text-gray-500">
          No users found
        </div>
      )}
    </div>
  );
}
