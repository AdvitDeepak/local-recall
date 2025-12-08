"use client"

import { useState, useEffect } from "react"
import {
  Settings as SettingsIcon,
  Keyboard,
  Database,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  Plus,
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { api } from "@/lib/api"
import { useToast } from "@/lib/hooks/use-toast"
import type { Keybind } from "@/lib/types"

export function SettingsTab() {
  const [keybinds, setKeybinds] = useState<Keybind[]>([])
  const [loading, setLoading] = useState(true)
  const [platform, setPlatform] = useState<"macos" | "windows">("macos")
  const [newKeySequence, setNewKeySequence] = useState("")
  const [newAction, setNewAction] = useState("capture_selected")
  const [adding, setAdding] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    const detectPlatform = () => {
      const userAgent = window.navigator.userAgent.toLowerCase()
      if (userAgent.includes("mac")) {
        setPlatform("macos")
      } else {
        setPlatform("windows")
      }
    }

    detectPlatform()
    fetchKeybinds()
  }, [])

  const fetchKeybinds = async () => {
    try {
      const data = await api.getKeybinds()
      setKeybinds(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load keybinds",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const platformKeybinds = keybinds.filter((kb) => {
    const isMacOS = kb.key_sequence.includes("<cmd>")
    const isWindowsLinux = kb.key_sequence.includes("<ctrl>") && !kb.key_sequence.includes("<cmd>")

    if (platform === "macos") {
      return isMacOS
    } else {
      return isWindowsLinux
    }
  })

  const getActionLabel = (action: string) => {
    const labels: Record<string, string> = {
      capture_selected: "Capture Selected Text",
      capture_screenshot: "Capture Screenshot",
    }
    return labels[action] || action
  }

  const handleAddKeybind = async () => {
    if (!newKeySequence) {
      toast({
        title: "Error",
        description: "Please enter a key sequence",
        variant: "destructive",
      })
      return
    }

    setAdding(true)
    try {
      let keybind: Keybind
      if (newAction === "capture_selected") {
        keybind = await api.addSelectedTextKeybind(newKeySequence)
      } else {
        keybind = await api.addScreenshotKeybind(newKeySequence)
      }

      setKeybinds([...keybinds, keybind])
      setNewKeySequence("")
      setNewAction("capture_selected")

      toast({
        title: "Success",
        description: "Keybind added successfully. Restart the capture service for changes to take effect.",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add keybind",
        variant: "destructive",
      })
    } finally {
      setAdding(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle className="text-3xl flex items-center gap-2">
            <SettingsIcon className="h-8 w-8" />
            Settings
          </CardTitle>
          <CardDescription>Configure keybinds and view system information</CardDescription>
        </CardHeader>
      </Card>

      <Card className="border-none shadow-lg bg-amber-50 dark:bg-amber-950 border-amber-500">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5" />
            <div>
              <p className="font-medium text-amber-900 dark:text-amber-100">
                Restart Required
              </p>
              <p className="text-sm text-amber-800 dark:text-amber-200">
                Changes to keybinds require restarting the capture service to take effect
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Keyboard className="h-5 w-5" />
            Keybinds
          </CardTitle>
          <CardDescription>Current keyboard shortcuts for text capture</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <Tabs>
              <TabsList className="grid w-full grid-cols-2 max-w-md">
                <TabsTrigger
                  value="macos"
                  active={platform === "macos"}
                  onClick={() => setPlatform("macos")}
                >
                  macOS
                </TabsTrigger>
                <TabsTrigger
                  value="windows"
                  active={platform === "windows"}
                  onClick={() => setPlatform("windows")}
                >
                  Windows / Linux
                </TabsTrigger>
              </TabsList>

              <TabsContent value="macos" active={platform === "macos"}>
                <div className="space-y-4 mt-4">
                  {platformKeybinds.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                      No keybinds configured for macOS
                    </p>
                  ) : (
                    platformKeybinds.map((kb) => (
                      <div
                        key={kb.id}
                        className="flex items-center justify-between p-4 rounded-lg bg-muted"
                      >
                        <div>
                          <p className="font-medium">{getActionLabel(kb.action)}</p>
                          <p className="text-sm text-muted-foreground">
                            Press the keys simultaneously
                          </p>
                        </div>
                        <Badge variant="outline" className="font-mono text-base px-4 py-2">
                          {kb.key_sequence}
                        </Badge>
                      </div>
                    ))
                  )}

                  <div className="mt-6 p-4 border rounded-lg space-y-4">
                    <h3 className="font-semibold flex items-center gap-2">
                      <Plus className="h-4 w-4" />
                      Add New macOS Keybind
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="action-mac">Action</Label>
                        <Select
                          id="action-mac"
                          value={newAction}
                          onChange={(e) => setNewAction(e.target.value)}
                        >
                          <option value="capture_selected">Capture Selected Text</option>
                          <option value="capture_screenshot">Capture Screenshot</option>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="key-mac">Key Sequence</Label>
                        <Input
                          id="key-mac"
                          placeholder="<cmd>+<ctrl>+r"
                          value={newKeySequence}
                          onChange={(e) => setNewKeySequence(e.target.value)}
                        />
                      </div>
                    </div>
                    <Button
                      onClick={handleAddKeybind}
                      disabled={adding}
                      className="w-full"
                    >
                      {adding ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Adding...
                        </>
                      ) : (
                        <>
                          <Plus className="h-4 w-4 mr-2" />
                          Add Keybind
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="windows" active={platform === "windows"}>
                <div className="space-y-4 mt-4">
                  {platformKeybinds.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                      No keybinds configured for Windows/Linux
                    </p>
                  ) : (
                    platformKeybinds.map((kb) => (
                      <div
                        key={kb.id}
                        className="flex items-center justify-between p-4 rounded-lg bg-muted"
                      >
                        <div>
                          <p className="font-medium">{getActionLabel(kb.action)}</p>
                          <p className="text-sm text-muted-foreground">
                            Press the keys simultaneously
                          </p>
                        </div>
                        <Badge variant="outline" className="font-mono text-base px-4 py-2">
                          {kb.key_sequence}
                        </Badge>
                      </div>
                    ))
                  )}

                  <div className="mt-6 p-4 border rounded-lg space-y-4">
                    <h3 className="font-semibold flex items-center gap-2">
                      <Plus className="h-4 w-4" />
                      Add New Windows/Linux Keybind
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="action-win">Action</Label>
                        <Select
                          id="action-win"
                          value={newAction}
                          onChange={(e) => setNewAction(e.target.value)}
                        >
                          <option value="capture_selected">Capture Selected Text</option>
                          <option value="capture_screenshot">Capture Screenshot</option>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="key-win">Key Sequence</Label>
                        <Input
                          id="key-win"
                          placeholder="<ctrl>+<alt>+r"
                          value={newKeySequence}
                          onChange={(e) => setNewKeySequence(e.target.value)}
                        />
                      </div>
                    </div>
                    <Button
                      onClick={handleAddKeybind}
                      disabled={adding}
                      className="w-full"
                    >
                      {adding ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Adding...
                        </>
                      ) : (
                        <>
                          <Plus className="h-4 w-4 mr-2" />
                          Add Keybind
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          )}
        </CardContent>
      </Card>

      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            System Configuration
          </CardTitle>
          <CardDescription>Current system settings and configuration</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground mb-1">Embedding Model</p>
              <p className="font-medium">nomic-embed-text</p>
            </div>

            <div className="p-4 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground mb-1">Default LLM</p>
              <p className="font-medium">llama3.1:8b</p>
            </div>

            <div className="p-4 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground mb-1">Vector Store</p>
              <p className="font-medium">FAISS (Local)</p>
            </div>

            <div className="p-4 rounded-lg bg-muted">
              <p className="text-sm text-muted-foreground mb-1">Database</p>
              <p className="font-medium">SQLite</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle>OpenAI Configuration</CardTitle>
          <CardDescription>
            Optional: Configure OpenAI API for GPT models
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3 p-4 rounded-lg bg-muted">
            <div className="flex-1">
              <p className="font-medium mb-2">API Key Status</p>
              <div className="flex items-center gap-2">
                <XCircle className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Not configured (using Ollama only)
                </span>
              </div>
            </div>
          </div>

          <div className="text-sm text-muted-foreground space-y-2">
            <p>To use OpenAI models:</p>
            <ol className="list-decimal list-inside space-y-1 ml-2">
              <li>Get your API key from OpenAI</li>
              <li>Set the OPENAI_API_KEY environment variable</li>
              <li>Restart the backend service</li>
            </ol>
          </div>
        </CardContent>
      </Card>

      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle>About Local Recall</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
            <p>Privacy-first: All data stored locally</p>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
            <p>Semantic search powered by embeddings</p>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
            <p>RAG system with local or cloud LLMs</p>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
            <p>Keyboard shortcuts for quick capture</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
