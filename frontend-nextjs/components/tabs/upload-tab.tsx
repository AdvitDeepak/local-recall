"use client"

import { useState, useRef } from "react"
import { Upload as UploadIcon, File, FileText, X, Loader2, CheckCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { api } from "@/lib/api"
import { useToast } from "@/lib/hooks/use-toast"
import { cn } from "@/lib/utils"

interface UploadedFile {
  name: string
  size: number
  type: string
  content: string
}

export function UploadTab() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState("")
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    handleFiles(droppedFiles)
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      handleFiles(selectedFiles)
    }
  }

  const handleFiles = async (fileList: File[]) => {
    const validFiles = fileList.filter((file) =>
      file.name.match(/\.(txt|pdf|docx)$/i)
    )

    if (validFiles.length !== fileList.length) {
      toast({
        title: "Warning",
        description: "Only TXT, PDF, and DOCX files are supported",
        variant: "warning",
      })
    }

    const uploadedFiles: UploadedFile[] = []

    for (const file of validFiles) {
      const content = await file.text()
      uploadedFiles.push({
        name: file.name,
        size: file.size,
        type: file.type,
        content,
      })
    }

    setFiles((prev) => [...prev, ...uploadedFiles])
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault()
      const tag = tagInput.trim()
      if (tag && !tags.includes(tag)) {
        setTags([...tags, tag])
        setTagInput("")
      }
    }
  }

  const removeTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag))
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      toast({
        title: "Error",
        description: "Please select files to upload",
        variant: "destructive",
      })
      return
    }

    setUploading(true)

    try {
      for (const file of files) {
        await api.createEntry({
          text: file.content,
          source: "upload",
          tags: tags.length > 0 ? tags : undefined,
        })
      }

      toast({
        title: "Success",
        description: `${files.length} ${files.length === 1 ? "file" : "files"} uploaded successfully`,
        variant: "success",
      })

      setFiles([])
      setTags([])
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to upload files",
        variant: "destructive",
      })
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / (1024 * 1024)).toFixed(1) + " MB"
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle className="text-3xl">Upload Documents</CardTitle>
          <CardDescription>
            Upload TXT, PDF, or DOCX files to add them to your knowledge base
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div
            className={cn(
              "border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer",
              dragActive
                ? "border-primary bg-primary/5"
                : "border-muted-foreground/25 hover:border-primary/50"
            )}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <UploadIcon className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium mb-2">
              Drop files here or click to browse
            </p>
            <p className="text-sm text-muted-foreground">
              Supported formats: TXT, PDF, DOCX
            </p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.pdf,.docx"
              className="hidden"
              onChange={handleFileInput}
            />
          </div>

          {files.length > 0 && (
            <div className="space-y-2">
              <Label>Selected Files ({files.length})</Label>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 rounded-md bg-muted"
                  >
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-primary" />
                      <div>
                        <p className="text-sm font-medium">{file.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="tags">
              Tags (optional)
              <span className="text-xs text-muted-foreground ml-2">
                Press Enter or comma to add
              </span>
            </Label>
            <Input
              id="tags"
              placeholder="Add tags..."
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleAddTag}
            />
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="cursor-pointer hover:bg-destructive"
                    onClick={() => removeTag(tag)}
                  >
                    {tag}
                    <X className="h-3 w-3 ml-1" />
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <Button
            onClick={handleUpload}
            disabled={uploading || files.length === 0}
            className="w-full"
            size="lg"
          >
            {uploading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin mr-2" />
                Uploading...
              </>
            ) : (
              <>
                <UploadIcon className="h-5 w-5 mr-2" />
                Upload {files.length > 0 && `(${files.length})`}
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      <Card className="border-none shadow-lg">
        <CardHeader>
          <CardTitle>Tips</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
            <p>Files are processed and embedded automatically</p>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
            <p>Tags help organize and filter your documents</p>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
            <p>Uploaded content is searchable via semantic search</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
