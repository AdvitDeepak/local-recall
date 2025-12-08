import * as React from "react"
import { cn } from "@/lib/utils"
import { X } from "lucide-react"

export interface Toast {
  id: string
  title?: string
  description?: string
  variant?: "default" | "success" | "warning" | "destructive"
}

interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  toast: Toast
  onClose: (id: string) => void
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ className, toast, onClose, ...props }, ref) => {
    React.useEffect(() => {
      const timer = setTimeout(() => {
        onClose(toast.id)
      }, 5000)

      return () => clearTimeout(timer)
    }, [toast.id, onClose])

    const variantStyles = {
      default: "border-border bg-card",
      success: "border-green-500 bg-green-50 dark:bg-green-950",
      warning: "border-amber-500 bg-amber-50 dark:bg-amber-950",
      destructive: "border-red-500 bg-red-50 dark:bg-red-950",
    }

    return (
      <div
        ref={ref}
        className={cn(
          "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all",
          variantStyles[toast.variant || "default"],
          className
        )}
        {...props}
      >
        <div className="grid gap-1">
          {toast.title && (
            <div className="text-sm font-semibold">{toast.title}</div>
          )}
          {toast.description && (
            <div className="text-sm opacity-90">{toast.description}</div>
          )}
        </div>
        <button
          onClick={() => onClose(toast.id)}
          className="absolute right-2 top-2 rounded-md p-1 opacity-0 transition-opacity hover:opacity-100 group-hover:opacity-100"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    )
  }
)
Toast.displayName = "Toast"

export { Toast }
