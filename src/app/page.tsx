import dynamic from 'next/dynamic'

const PRAgentUI = dynamic(() => import('./pr-ai-agent'), { 
  loading: () => <div className="flex items-center justify-center min-h-screen">Loading...</div>
})

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <PRAgentUI />
    </main>
  )
}