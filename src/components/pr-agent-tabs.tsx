import * as React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { 
  BarChart2, 
  MessageSquare, 
  AlertTriangle, 
  Image as ImageIcon,
  TrendingUp 
} from "lucide-react"
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui/tabs"

const PR_AGENTS = {
  content_strategist: {
    icon: MessageSquare,
    title: "Content Strategist",
    description: "Content creation and brand voice management",
    inputPlaceholder: "What content would you like me to help with?",
    modelPreference: "gpt-4-turbo" // Better for creative and strategic tasks
  },
  crisis_manager: {
    icon: AlertTriangle,
    title: "Crisis Manager",
    description: "Crisis response and risk management",
    inputPlaceholder: "Describe the situation that needs addressing...",
    modelPreference: "gpt-4" // More controlled for sensitive content
  },
  media_relations: {
    icon: MessageSquare,
    title: "Media Relations",
    description: "Press releases and media communications",
    inputPlaceholder: "What would you like to communicate to the media?",
    modelPreference: "gpt-4-turbo"
  },
  analytics_expert: {
    icon: BarChart2,
    title: "Analytics Expert",
    description: "Content and sentiment analysis",
    inputPlaceholder: "What would you like me to analyze?",
    modelPreference: "claude-3" // Good for analytical tasks
  },
  visual_creator: {
    icon: ImageIcon,
    title: "Visual Creator",
    description: "Visual content generation and guidance",
    inputPlaceholder: "Describe the visual content you need...",
    modelPreference: "dall-e-3" // For image generation
  }
}

export function PRAgentTabs() {
  const [activeTask, setActiveTask] = React.useState("sentiment_analysis")
  const [input, setInput] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('query', input)
      formData.append('task_type', activeTask)

      const response = await fetch('http://localhost:8000/api/pr-agent', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()
      // Handle the response based on task type
      console.log(data)
      
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Tabs defaultValue="sentiment_analysis" className="w-full">
      <TabsList className="grid grid-cols-5 gap-4">
        {Object.entries(PR_AGENTS).map(([key, task]) => {
          const Icon = task.icon
          return (
            <TabsTrigger
              key={key}
              value={key}
              onClick={() => setActiveTask(key)}
              className="flex items-center gap-2"
            >
              <Icon className="w-4 h-4" />
              {task.title}
            </TabsTrigger>
          )
        })}
      </TabsList>

      {Object.entries(PR_AGENTS).map(([key, task]) => (
        <TabsContent key={key} value={key}>
          <Card>
            <CardContent className="space-y-4 pt-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <Textarea
                  placeholder={task.inputPlaceholder}
                  value={input}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
                  className="min-h-[100px]"
                />
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Processing..." : `Run ${task.title}`}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      ))}
    </Tabs>
  )
} 