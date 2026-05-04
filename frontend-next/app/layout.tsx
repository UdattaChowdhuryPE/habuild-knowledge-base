import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Habuild HR Portal",
  description: "Your HR Companion — Get instant answers to all your HR policy questions",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50 h-full">{children}</body>
    </html>
  )
}
