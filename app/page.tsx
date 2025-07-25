'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import Header from '@/components/Header'

export default function Home() {
  return (
    <main className="min-h-screen">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              漢方AI診断システム
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              あなたの症状に基づいて、最適な漢方治療法をご提案します
            </p>
          </div>
          <ChatInterface />
        </div>
      </div>
    </main>
  )
}