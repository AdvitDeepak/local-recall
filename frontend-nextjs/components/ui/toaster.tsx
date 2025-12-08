"use client"

import { Toast, type Toast as ToastType } from "./toast"

interface ToasterProps {
  toasts: ToastType[]
  onClose: (id: string) => void
}

export function Toaster({ toasts, onClose }: ToasterProps) {
  return (
    <div className="fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:top-auto sm:right-0 sm:bottom-0 sm:left-auto sm:flex-col md:max-w-[420px]">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  )
}
