import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: '漢方AI診断システム',
  description: '症状に基づいた漢方診断とオーダーメイド生薬提案システム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
          {children}
        </div>
      </body>
    </html>
  )
}