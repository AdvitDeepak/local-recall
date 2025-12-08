"use client"

import { useState, useEffect } from "react"
import { Trash2, Filter, FileText, Image as ImageIcon, Loader2, AlertCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { api } from "@/lib/api"
import { useToast } from "@/lib/hooks/use-toast"
import type { DataEntry } from "@/lib/types"
import { formatDistanceToNow } from "date-fns"

export function DataTab() {
  const [entries, setEntries] = useState<DataEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [source, setSource] = useState("")
  const [tag, setTag] = useState("")
  const [limit, setLimit] = useState(50)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const { toast } = useToast()

  const fetchData = async () => {
    setLoading(true)
    try {
      const params: any = { limit }
      if (source) params.source = source
      if (tag) params.tag = tag

      const data = await api.getData(params)
      setEntries(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleDelete = async () => {
    if (deleteId === null) return

    try {
      await api.deleteEntry(deleteId)
      setEntries(entries.filter((e) => e.id !== deleteId))
      toast({
        title: "Success",
        description: "Entry deleted successfully",
        variant: "success",
      })
      setDeleteId(null)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete entry",
        variant: "destructive",
      })
    }
  }

  const getSourceIcon = (source: string) => {
    if (source === "clipboard") return <FileText className="h-4 w-4" />
    if (source === "screenshot") return <ImageIcon className="h-4 w-4" />
    return <FileText className="h-4 w-4" />
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle className="text-3xl">Data Browser</CardTitle>
          <CardDescription>Browse and manage your captured data</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="source">Source</Label>
              <Select id="source" value={source} onChange={(e) => setSource(e.target.value)}>
                <option value="">All Sources</option>
                <option value="clipboard">Clipboard</option>
                <option value="screenshot">Screenshot</option>
              </Select>
            </div>

            <div>
              <Label htmlFor="tag">
                Tag
                <span className="text-xs text-muted-foreground ml-1">(for uploaded docs)</span>
              </Label>
              <Input
                id="tag"
                placeholder="Enter tag..."
                value={tag}
                onChange={(e) => setTag(e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="limit">Limit</Label>
              <Input
                id="limit"
                type="number"
                min={10}
                max={500}
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value) || 50)}
              />
            </div>
          </div>

          <Button onClick={fetchData} disabled={loading} className="w-full">
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Loading...
              </>
            ) : (
              <>
                <Filter className="h-4 w-4 mr-2" />
                Apply Filters
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : entries.length === 0 ? (
        <Card className="border-none shadow-lg">
          <CardContent className="py-12">
            <div className="text-center space-y-4">
              <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground" />
              <h3 className="text-lg font-semibold">No entries found</h3>
              <p className="text-muted-foreground">
                Start capturing text or upload documents to see them here
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold">
              {entries.length} {entries.length === 1 ? "Entry" : "Entries"}
            </h3>
          </div>

          <div className="grid gap-4">
            {entries.map((entry) => {
              const isExpanded = expandedId === entry.id
              const displayText = isExpanded
                ? entry.text
                : entry.text.length > 200
                ? entry.text.substring(0, 200) + "..."
                : entry.text

              return (
                <Card key={entry.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="outline">#{entry.id}</Badge>
                        <Badge className="flex items-center gap-1">
                          {getSourceIcon(entry.source)}
                          {entry.source}
                        </Badge>
                        {entry.tags && entry.tags.length > 0 && (
                          <>
                            {entry.tags.map((tag) => (
                              <Badge key={tag} variant="secondary">
                                {tag}
                              </Badge>
                            ))}
                          </>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground whitespace-nowrap">
                          {formatDistanceToNow(new Date(entry.timestamp), {
                            addSuffix: true,
                          })}
                        </span>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeleteId(entry.id)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <p className="text-sm leading-relaxed mb-2 whitespace-pre-wrap">
                      {displayText}
                    </p>

                    {entry.text.length > 200 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setExpandedId(isExpanded ? null : entry.id)}
                      >
                        {isExpanded ? "Show less" : "Read more"}
                      </Button>
                    )}

                    <div className="mt-2 text-xs text-muted-foreground">
                      {entry.char_count} characters
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}

      <Dialog open={deleteId !== null} onOpenChange={(open) => !open && setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Entry</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this entry? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
