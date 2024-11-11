'use client'

import dynamic from 'next/dynamic'

const PRAgentUI = dynamic(() => import('./pr-ai-agent'), { 
  ssr: false,
  loading: () => <div>Loading...</div>
})

export default function ClientPage() {
  return <PRAgentUI />
} 