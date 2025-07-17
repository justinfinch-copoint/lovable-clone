import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LOVABLE-CLONE v1.0 | Terminal',
  description: 'AI-POWERED CODE GENERATION TERMINAL - Powered by Claude SDK',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}