"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/useAuthStore";
import { Button } from "@/components/ui/Button";
import { Compass, FolderKanban, Users, Zap } from "lucide-react";

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-blue-600">SkillSphere</h1>
        <div className="flex items-center gap-3">
          {mounted && isAuthenticated() ? (
            <Link href="/dashboard">
              <Button>Dashboard</Button>
            </Link>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost">Login</Button>
              </Link>
              <Link href="/register">
                <Button>Get Started</Button>
              </Link>
            </>
          )}
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-20">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Learn, Build, Collaborate
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8">
            SkillSphere is a platform where learners and creators come together to share projects,
            give feedback, and grow their skills.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href={mounted && isAuthenticated() ? "/explore" : "/register"}>
              <Button size="lg">
                <Compass size={20} className="mr-2" />
                {mounted && isAuthenticated() ? "Explore Projects" : "Join Now"}
              </Button>
            </Link>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: FolderKanban,
              title: "Showcase Projects",
              desc: "Create project portfolios, share files, and get feedback from the community.",
            },
            {
              icon: Users,
              title: "Collaborate",
              desc: "Comment on projects, discuss ideas, and connect with like-minded learners.",
            },
            {
              icon: Zap,
              title: "Real-time Updates",
              desc: "Get instant notifications and stay updated on project activity.",
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700"
            >
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-4">
                <feature.icon size={24} className="text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600 dark:text-gray-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
