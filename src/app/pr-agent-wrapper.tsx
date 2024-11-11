'use client'

import ClientOnly from './components/client-only'
import PRAgentUI from './pr-ai-agent'

export default function PRAgentWrapper() {
  return (
    <ClientOnly>
      <PRAgentUI />
    </ClientOnly>
  )
} 