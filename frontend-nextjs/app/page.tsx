"use client"

import { useState } from "react"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { SearchTab } from "@/components/tabs/search-tab"
import { DataTab } from "@/components/tabs/data-tab"
import { UploadTab } from "@/components/tabs/upload-tab"
import { SettingsTab } from "@/components/tabs/settings-tab"
import { Toaster } from "@/components/ui/toaster"
import { useToastStore } from "@/lib/hooks/use-toast"

export default function Home() {
  const [currentTab, setCurrentTab] = useState("search")
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const { toasts, removeToast } = useToastStore()

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        collapsed={sidebarCollapsed}
        onCollapsedChange={setSidebarCollapsed}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-auto p-6">
          {currentTab === "search" && <SearchTab />}
          {currentTab === "data" && <DataTab />}
          {currentTab === "upload" && <UploadTab />}
          {currentTab === "settings" && <SettingsTab />}
        </main>
      </div>

      <Toaster toasts={toasts} onClose={removeToast} />
    </div>
  )
}
