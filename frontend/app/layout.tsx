import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Song Score AI - Analyze Your SUNO Tracks',
  description: 'AI-powered analysis for music tracks generated with SUNO. Get success predictions, persona reactions, and quality insights.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <nav className="border-b border-white/10 backdrop-blur-sm">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <a href="/" className="flex items-center space-x-2">
                  <span className="text-2xl">🎵</span>
                  <span className="text-xl font-bold text-white">Song Score AI</span>
                </a>
                <div className="text-sm text-gray-300">
                  Powered by AI
                </div>
              </div>
            </div>
          </nav>
          <main>{children}</main>
          <footer className="border-t border-white/10 mt-16">
            <div className="container mx-auto px-4 py-8 text-center text-gray-400 text-sm">
              Made for the SUNO AI music community
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
