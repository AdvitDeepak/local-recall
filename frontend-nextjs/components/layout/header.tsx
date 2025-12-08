"use client"

import { useEffect, useState } from "react"
import { Moon, Sun, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useTheme } from "@/lib/hooks/use-theme"
import { api } from "@/lib/api"
import type { Stats } from "@/lib/types"

export function Header() {
  const { theme, toggleTheme } = useTheme()
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getStats()
        setStats(data)
      } catch (error) {
        console.error("Failed to fetch stats:", error)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b bg-card/50 backdrop-blur-sm">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Activity className={cn(
            "h-4 w-4",
            stats?.is_capturing ? "text-green-500 animate-pulse" : "text-gray-400"
          )} />
          <span className="text-sm font-medium">
            {stats?.is_capturing ? "Capturing" : "Stopped"}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {stats && (
          <div className="flex items-center gap-3 text-sm">
            <div className="flex flex-col items-end">
              <span className="text-muted-foreground">Total Entries</span>
              <span className="font-semibold">{stats.total_entries.toLocaleString()}</span>
            </div>
            <div className="h-8 w-px bg-border" />
            <div className="flex flex-col items-end">
              <span className="text-muted-foreground">Embedded</span>
              <span className="font-semibold">{stats.embedded_entries.toLocaleString()}</span>
            </div>
          </div>
        )}

        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === "dark" ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>
      </div>
    </header>
  )
}

import { cn } from "@/lib/utils"
