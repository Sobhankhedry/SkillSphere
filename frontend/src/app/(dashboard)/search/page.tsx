"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Search as SearchIcon } from "lucide-react";
import { searchAPI } from "@/lib/api";
import { SearchResults } from "@/types";
import { Spinner } from "@/components/ui/Spinner";

export default function SearchPage() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"all" | "projects" | "users">("all");

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      performSearch(initialQuery);
    }
  }, [initialQuery]);

  const performSearch = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const { data } = await searchAPI.global(q);
      setResults(data);
    } catch {
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch(query);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <h2 className="text-2xl font-bold">Search</h2>
      <form onSubmit={handleSubmit} className="relative max-w-xl">
        <SearchIcon size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search projects, users, tags..."
          className="w-full pl-10 pr-4 py-3 bg-white dark:bg-gray-800 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </form>
      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : results ? (
        <div className="space-y-6">
          <div className="flex gap-2 border-b dark:border-gray-700 pb-2">
            {(["all", "projects", "users"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
                  activeTab === tab
                    ? "bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          {(activeTab === "all" || activeTab === "projects") && results.projects.length > 0 && (
            <div>
              <h3 className="font-semibold mb-3">Projects</h3>
              <div className="space-y-2">
                {results.projects.map((p) => (
                  <Link
                    key={p.id}
                    href={`/projects/${p.id}`}
                    className="block p-3 bg-white dark:bg-gray-800 border rounded-lg hover:border-blue-300 transition-colors"
                  >
                    <h4 className="font-medium">{p.title}</h4>
                    <p className="text-sm text-gray-500 line-clamp-1">{p.description}</p>
                    <p className="text-xs text-gray-400 mt-1">by {p.owner__username}</p>
                  </Link>
                ))}
              </div>
            </div>
          )}
          {(activeTab === "all" || activeTab === "users") && results.users.length > 0 && (
            <div>
              <h3 className="font-semibold mb-3">Users</h3>
              <div className="space-y-2">
                {results.users.map((u) => (
                  <div key={u.id} className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 border rounded-lg">
                    <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center font-bold text-blue-600">
                      {u.username[0].toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium">{u.username}</p>
                      <p className="text-sm text-gray-500">
                        {[u.first_name, u.last_name].filter(Boolean).join(" ")}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {results.projects.length === 0 && results.users.length === 0 && (
            <p className="text-center text-gray-500 py-8">No results found.</p>
          )}
        </div>
      ) : (
        <p className="text-center text-gray-500 py-12">Enter a search query to get started.</p>
      )}
    </div>
  );
}
