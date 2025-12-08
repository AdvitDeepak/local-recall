"use client"

import { cn } from "@/lib/utils"
import { Search, Database, Upload, Settings, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SidebarProps {
  currentTab: string
  onTabChange: (tab: string) => void
  collapsed: boolean
  onCollapsedChange: (collapsed: boolean) => void
}

export function Sidebar({ currentTab, onTabChange, collapsed, onCollapsedChange }: SidebarProps) {
  const menuItems = [
    { id: "search", label: "Search & Query", icon: Search },
    { id: "data", label: "Data Browser", icon: Database },
    { id: "upload", label: "Upload", icon: Upload },
    { id: "settings", label: "Settings", icon: Settings },
  ]

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

      <nav className="flex-1 p-2 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentTab === item.id

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={cn(
                "flex items-center w-full p-3 rounded-lg transition-colors",
                "hover:bg-accent hover:text-accent-foreground",
                isActive && "bg-primary text-primary-foreground hover:bg-primary/90",
                collapsed && "justify-center"
              )}
            >
              <Icon className={cn("h-5 w-5", !collapsed && "mr-3")} />
              {!collapsed && <span>{item.label}</span>}
            </button>
          )
        })}
      </nav>

      <div className="p-4 border-t text-xs text-muted-foreground">
        {!collapsed && <p>Privacy-first RAG system</p>}
      </div>
    </div>
  )
}
