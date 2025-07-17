import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'GAMEABLE v1.0 | Terminal',
  description: 'PHASER GAME DEVELOPMENT TERMINAL - Build games with Claude SDK',
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