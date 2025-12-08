"use client"

import { useToast, useToastStore } from "@/lib/hooks/use-toast"
import { Toast } from "@/components/ui/toast"

export function Toaster() {
  const { toasts } = useToast()
  const { removeToast } = useToastStore()

  return (
    <div className="fixed top-0 right-0 z-50 flex max-h-screen w-full flex-col-reverse p-4 sm:top-0 sm:right-0 sm:flex-col md:max-w-[420px]">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={removeToast} />
      ))}
    </div>
  )
}
