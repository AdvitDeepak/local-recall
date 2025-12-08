"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight, RefreshCw, Play, Pause } from "lucide-react"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"
import type { SystemStatus } from "@/lib/types"

interface SidebarProps {
  collapsed: boolean
  onCollapsedChange: (collapsed: boolean) => void
}

export function Sidebar({ collapsed, onCollapsedChange }: SidebarProps) {
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [toggling, setToggling] = useState(false)

  const fetchStatus = async () => {
    try {
      const data = await api.getStatus()
      setStatus(data)
    } catch (error) {
      console.error("Failed to fetch status:", error)
    }
  }

  useEffect(() => {
    fetchStatus()
    // Refresh status every 5 seconds
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchStatus()
    setTimeout(() => setRefreshing(false), 500)
  }

  const handleToggleCapture = async () => {
    if (!status) return

    setToggling(true)
    try {
      if (status.capturing) {
        await api.stopCapture()
      } else {
        await api.startCapture()
      }
      await fetchStatus()
    } catch (error) {
      console.error("Failed to toggle capture:", error)
    } finally {
      setToggling(false)
    }
  }

  return (
    <div
      className={cn(
        "flex flex-col h-screen border-r bg-card transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex items-center justify-between p-4 border-b">
        {!collapsed && (
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent">
            Local Recall
          </h1>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onCollapsedChange(!collapsed)}
          className={cn(collapsed && "mx-auto")}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      {!collapsed && (
        <div className="flex-1 overflow-y-auto">
          <div className="p-4 space-y-4">
            {/* System Control */}
            <div>
              <h2 className="text-sm font-semibold mb-3">System Control</h2>

              {!status ? (
                <div className="text-sm text-muted-foreground flex items-center gap-2">
                  <RefreshCw className="h-3 w-3 animate-spin" />
                  Loading...
                </div>
              ) : (
                <div className="space-y-2">
                  <Button
                    onClick={handleRefresh}
                    disabled={refreshing}
                    variant="outline"
                    className="w-full"
                    size="sm"
                  >
                    <RefreshCw className={cn("h-3.5 w-3.5 mr-2", refreshing && "animate-spin")} />
                    Refresh
                  </Button>

                  <div className="py-2">
                    {status.capturing ? (
                      <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400 mb-2">
                        ✅ Capture Active
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-sm text-amber-600 dark:text-amber-400 mb-2">
                        ⏸️ Capture Paused
                      </div>
                    )}
                    <Button
                      onClick={handleToggleCapture}
                      disabled={toggling}
                      className={cn(
                        "w-full",
                        status.capturing
                          ? "bg-amber-500 hover:bg-amber-600"
                          : "bg-green-500 hover:bg-green-600"
                      )}
                      size="sm"
                    >
                      {toggling ? (
                        <RefreshCw className="h-3.5 w-3.5 mr-2 animate-spin" />
                      ) : status.capturing ? (
                        <Pause className="h-3.5 w-3.5 mr-2" />
                      ) : (
                        <Play className="h-3.5 w-3.5 mr-2" />
                      )}
                      {status.capturing ? "Stop Capture" : "Start Capture"}
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* Statistics */}
            {status && (
              <>
                <div className="border-t pt-4">
                  <h2 className="text-sm font-semibold mb-3">Statistics</h2>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Total Entries</span>
                      <span className="font-semibold">{status.database.total_entries}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Embedded</span>
                      <span className="font-semibold">{status.database.embedded_entries}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Pending</span>
                      <span className="font-semibold">{status.database.pending_embeddings}</span>
                    </div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h2 className="text-sm font-semibold mb-3">Vector Store</h2>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Total Vectors</span>
                      <span className="font-semibold">{status.vector_store.total_vectors}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Dimension</span>
                      <span className="font-semibold">{status.vector_store.dimension}</span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <div className="p-4 border-t text-xs text-muted-foreground">
        {!collapsed && <p>Privacy-first RAG system</p>}
      </div>
    </div>
  )
}
