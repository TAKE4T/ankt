'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  text: string
  isBot: boolean
  timestamp: Date
}

interface ChatResponse {
  message: string
  diagnosis?: {
    primaryCondition: string
    recommendedHerbs: string[]
    treatmentPlan: string
  }
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'こんにちは！漢方AI診断システムへようこそ。\n\nあなたの体調に最適な漢方治療をご提案するため、いくつか質問をさせていただきます。\n\n最近の体調はいかがですか？疲れやだるさを感じることが多いでしょうか？\n\n（「はい」「いいえ」「時々あります」など、お気軽にお答えください）',
      isBot: true,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isBot: false,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputValue, messages }),
      })

      if (!response.ok) {
        throw new Error('API request failed')
      }

      const data: ChatResponse = await response.json()

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.message,
        isBot: true,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: '申し訳ございません。システムエラーが発生しました。しばらく経ってから再度お試しください。',
        isBot: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="bg-green-50 px-6 py-4 border-b border-green-100">
        <h2 className="text-lg font-semibold text-green-800">
          漢方AI診断チャット
        </h2>
        <p className="text-sm text-green-600 mt-1">
          症状を詳しく教えてください。AIが最適な漢方治療をご提案します。
        </p>
      </div>

      <div className="h-96 overflow-y-auto p-6 bg-gray-50">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.isBot
                    ? 'bg-white text-gray-800 shadow-sm border border-gray-200'
                    : 'bg-green-500 text-white'
                }`}
              >
                <p className="text-sm">{message.text}</p>
                <p className="text-xs mt-1 opacity-70">
                  {message.timestamp.toLocaleTimeString('ja-JP', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 shadow-sm border border-gray-200 rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="px-6 py-4 bg-white border-t border-gray-200">
        <div className="flex space-x-3">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="症状や体調について詳しく教えてください..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            送信
          </button>
        </div>
      </div>
    </div>
  )
}