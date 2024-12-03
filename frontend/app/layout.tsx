import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Recipe Assistant',
  description: 'AI-powered recipe assistant with ingredient substitutions',
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
