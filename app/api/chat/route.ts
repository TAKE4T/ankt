import { NextRequest, NextResponse } from 'next/server'

interface Message {
  id: string
  text: string
  isBot: boolean
  timestamp: string
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, messages }: { message: string; messages: Message[] } = body

    // バックエンドAPIに転送
    const backendResponse = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        messages,
      }),
    })

    if (!backendResponse.ok) {
      throw new Error(`Backend API error: ${backendResponse.status}`)
    }

    const data = await backendResponse.json()

    return NextResponse.json(data)
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { 
        message: '申し訳ございません。システムエラーが発生しました。しばらく経ってから再度お試しください。',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}