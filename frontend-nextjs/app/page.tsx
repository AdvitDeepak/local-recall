"use client"

import { useState, useEffect, useRef } from "react"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { NavigationTabs } from "@/components/layout/navigation-tabs"
import { SearchTab } from "@/components/tabs/search-tab"
import { DataTab } from "@/components/tabs/data-tab"
import { UploadTab } from "@/components/tabs/upload-tab"
import { SettingsTab } from "@/components/tabs/settings-tab"
import { Toaster } from "@/components/ui/toaster"
import { useToast } from "@/lib/hooks/use-toast"
import { api } from "@/lib/api"

export default function Home() {
  const [currentTab, setCurrentTab] = useState("search")
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const { toast } = useToast()
  const lastNotificationId = useRef(0)

  // Poll for notifications every 2 seconds
  useEffect(() => {
    const pollNotifications = async () => {
      try {
        const response = await api.getNotifications({
          since_id: lastNotificationId.current,
          unread_only: true,
          limit: 10
        })

        const notifications = response?.notifications || []

        if (Array.isArray(notifications) && notifications.length > 0) {
          // Show toast for each new notification
          notifications.forEach((notif: any) => {
            if (notif && notif.title) {
              toast({
                title: notif.title,
                description: notif.message || "",
                variant: notif.status === "error" ? "destructive" : notif.status === "warning" ? "default" : "default",
              })

              // Update last notification ID
              if (notif.id && notif.id > lastNotificationId.current) {
                lastNotificationId.current = notif.id
              }
            }
          })

          // Mark notifications as read
          notifications.forEach((notif: any) => {
            if (notif && notif.id) {
              api.markNotificationRead(notif.id).catch(() => {})
            }
          })
        }
      } catch (error) {
        // Silently fail - don't spam errors
        console.error("Error polling notifications:", error)
      }
    }

    // Initial poll
    pollNotifications()

    // Poll every 2 seconds
    const interval = setInterval(pollNotifications, 2000)

    return () => clearInterval(interval)
  }, [toast])

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        collapsed={sidebarCollapsed}
        onCollapsedChange={setSidebarCollapsed}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <NavigationTabs currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 overflow-auto p-6">
          {currentTab === "search" && <SearchTab />}
          {currentTab === "data" && <DataTab />}
          {currentTab === "upload" && <UploadTab />}
          {currentTab === "settings" && <SettingsTab />}
        </main>
      </div>

      <Toaster />
    </div>
  )
}
