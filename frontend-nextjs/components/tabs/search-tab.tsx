"use client"

import { useState } from "react"
import { Search as SearchIcon, Loader2 } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { api } from "@/lib/api"
import { useToast } from "@/lib/hooks/use-toast"
import type { RAGResponse, SearchResult } from "@/lib/types"
import { formatDistanceToNow } from "date-fns"
import ReactMarkdown from "react-markdown"

export function SearchTab() {
  const [query, setQuery] = useState("")
  const [model, setModel] = useState("llama3.1:8b")
  const [useRag, setUseRag] = useState(true)
  const [streamEnabled, setStreamEnabled] = useState(true)
  const [k, setK] = useState(5)
  const [loading, setLoading] = useState(false)
  const [ragResponse, setRagResponse] = useState<RAGResponse | null>(null)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [streamingAnswer, setStreamingAnswer] = useState("")
  const { toast } = useToast()

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({ title: "Error", description: "Please enter a search query", variant: "destructive" })
      return
    }

    setLoading(true)
    setRagResponse(null)
    setSearchResults([])
    setStreamingAnswer("")

    try {
      if (useRag) {
        if (streamEnabled) {
          const eventSource = api.queryStream({ query, model, k })

          eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data)

            if (data.type === "answer_chunk") {
              setStreamingAnswer((prev) => prev + data.content)
            } else if (data.type === "metadata") {
              // Transform backend format to frontend format
              const transformedSources = data.sources.map((source: any) => ({
                entry: {
                  id: source.id,
                  source: source.source,
                  timestamp: source.timestamp
                },
                relevance_score: source.score
              }))
              setSearchResults(transformedSources)
            } else if (data.type === "done") {
              setLoading(false)
              eventSource.close()
            } else if (data.type === "error") {
              toast({
                title: "Error",
                description: data.content || "Streaming failed",
                variant: "destructive"
              })
              setLoading(false)
              eventSource.close()
            }
          }

          eventSource.onerror = () => {
            toast({ title: "Error", description: "Streaming failed", variant: "destructive" })
            setLoading(false)
            eventSource.close()
          }
        } else {
          const response = await api.query({ query, model, k })
          setRagResponse(response)
          setLoading(false)
        }
      } else {
        const results = await api.search(query, k)
        setSearchResults(results)
        setLoading(false)
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Search failed",
        variant: "destructive",
      })
      setLoading(false)
    }
  }

  const getRelevanceColor = (score: number) => {
    if (score > 0.8) return "bg-green-500"
    if (score > 0.6) return "bg-yellow-500"
    return "bg-orange-500"
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="border-none shadow-lg bg-gradient-to-br from-card via-card to-primary/5">
        <CardHeader>
          <CardTitle className="text-3xl">Search & Query</CardTitle>
          <CardDescription>Search your captured data with AI-powered semantic search</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex gap-3">
            <Input
              placeholder="What would you like to know?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="text-lg h-12"
            />
            <Button onClick={handleSearch} disabled={loading} size="lg" className="min-w-[120px]">
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <SearchIcon className="h-5 w-5 mr-2" />}
              {loading ? "Searching..." : "Search"}
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="model">Model</Label>
              <Select id="model" value={model} onChange={(e) => setModel(e.target.value)}>
                <optgroup label="Ollama">
                  <option value="llama3.1:8b">Llama 3.1 8B</option>
                  <option value="mistral">Mistral</option>
                  <option value="llama2">Llama 2</option>
                </optgroup>
                <optgroup label="OpenAI">
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </optgroup>
              </Select>
            </div>

            <div>
              <Label htmlFor="k">Number of Results: {k}</Label>
              <Slider id="k" min={1} max={10} value={k} onValueChange={setK} className="mt-2" />
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Switch checked={useRag} onCheckedChange={setUseRag} />
              <Label>Use RAG (AI Answers)</Label>
            </div>

            {useRag && (
              <div className="flex items-center gap-2">
                <Switch checked={streamEnabled} onCheckedChange={setStreamEnabled} />
                <Label>Stream Responses</Label>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {(ragResponse || streamingAnswer || searchResults.length > 0) && (
        <div className="space-y-4">
          {(ragResponse || streamingAnswer) && (
            <Card className="border-none shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  AI Answer
                  {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose dark:prose-invert max-w-none">
                  <ReactMarkdown>
                    {streamingAnswer || ragResponse?.answer || ""}
                  </ReactMarkdown>
                </div>
              </CardContent>
            </Card>
          )}

          {searchResults.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold mb-4">
                {useRag ? "Sources" : "Search Results"} ({searchResults.length})
              </h3>
              <div className="grid gap-4">
                {searchResults.map((result, index) => (
                  <Card key={result.entry.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">#{result.entry.id}</Badge>
                          <Badge>{result.entry.source}</Badge>
                          <div className="flex items-center gap-1">
                            <div
                              className={`h-2 w-2 rounded-full ${getRelevanceColor(
                                result.relevance_score
                              )}`}
                            />
                            <span className="text-sm text-muted-foreground">
                              {(result.relevance_score * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {formatDistanceToNow(new Date(result.entry.timestamp), {
                            addSuffix: true,
                          })}
                        </span>
                      </div>

                      {result.entry.content && (
                        <>
                          <p className="text-sm leading-relaxed mb-2">
                            {result.entry.content.length > 300
                              ? result.entry.content.substring(0, 300) + "..."
                              : result.entry.content}
                          </p>

                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>{result.entry.content.length} characters</span>
                            {result.entry.tags && result.entry.tags.length > 0 && (
                              <>
                                <span>•</span>
                                <div className="flex gap-1">
                                  {result.entry.tags.map((tag) => (
                                    <Badge key={tag} variant="secondary" className="text-xs">
                                      {tag}
                                    </Badge>
                                  ))}
                                </div>
                              </>
                            )}
                          </div>
                        </>
                      )}

                      {!result.entry.content && useRag && (
                        <p className="text-xs text-muted-foreground italic">
                          Source reference (content used in answer generation)
                        </p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
