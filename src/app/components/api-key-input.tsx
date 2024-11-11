'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

interface ApiKeyInputProps {
  onApiKeySubmit: (apiKey: string) => void
}

export function ApiKeyInput({ onApiKeySubmit }: ApiKeyInputProps) {
  const [apiKey, setApiKey] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (apiKey.trim()) {
      onApiKeySubmit(apiKey)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Enter OpenAI API Key</CardTitle>
          <CardDescription>
            Your API key is required to use the PR Agent. It will be stored in your browser session.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <Input
            type="password"
            placeholder="sk-..."
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            required
          />
          <Button type="submit" className="w-full">
            Start PR Agent
          </Button>
        </form>
      </Card>
    </div>
  )
} 