"use client"

import { Search, Database, Upload, Settings } from "lucide-react"
import { cn } from "@/lib/utils"

interface NavigationTabsProps {
  currentTab: string
  onTabChange: (tab: string) => void
}

export function NavigationTabs({ currentTab, onTabChange }: NavigationTabsProps) {
  const tabs = [
    { id: "search", label: "Search & Query", icon: Search },
    { id: "data", label: "Data Browser", icon: Database },
    { id: "upload", label: "Upload", icon: Upload },
    { id: "settings", label: "Settings", icon: Settings },
  ]

  return (
    <div className="border-b bg-card">
      <div className="flex gap-1 px-6">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = currentTab === tab.id

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={cn(
                "flex items-center gap-2 px-6 py-4 border-b-2 transition-colors font-medium",
                isActive
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/50"
              )}
            >
              <Icon className="h-5 w-5" />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
