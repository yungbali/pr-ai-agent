'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Loader2, Send, Upload, Sparkles } from "lucide-react"
import ReactMarkdown from 'react-markdown'
import { motion, AnimatePresence } from 'framer-motion'
import ClientOnly from './components/client-only'

type Message = {
  type: 'user' | 'ai'
  content: string
  id: string
  modelInfo?: {
    name: string
    temperature: number
    maxTokens: number
  }
}

type PRTask = {
  name: string;
  description: string;
  prompt: string;
};

type PRTasks = {
  [key: string]: PRTask;
};

export default function PRAgentUI() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [selectedTask, setSelectedTask] = useState('sentiment_analysis');
  const [availableTasks, setAvailableTasks] = useState<PRTasks>({});

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Fetch available PR tasks
    fetch('http://localhost:8000/api/pr-tasks')
      .then(res => res.json())
      .then(data => setAvailableTasks(data.tasks));
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      setFile(files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() && !file) return

    const userMessage: Message = {
      type: 'user',
      content: input,
      id: `user-${Date.now()}`
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);
    const formData = new FormData();
    formData.append('query', input);
    formData.append('task_type', selectedTask);
    if (file) {
      formData.append('file', file);
    }

    try {
      const res = await fetch('http://localhost:8000/api/pr-agent', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error('Failed to get response from AI agent');
      }

      const data = await res.json();
      
      // Handle the response based on task type and model
      let responseContent = '';
      let modelInfo = null;

      if (data.response && typeof data.response === 'object') {
        // Extract model information
        modelInfo = {
          name: data.response.model_used,
          temperature: data.response.parameters.temperature,
          maxTokens: data.response.parameters.max_tokens
        };

        // Handle different response types
        if (data.response.image_url) {
          responseContent = `![Generated Image](${data.response.image_url})`;
        } else if (data.response.embedding) {
          responseContent = '```json\n' + JSON.stringify(data.response.embedding, null, 2) + '\n```';
        } else {
          responseContent = data.response.analysis || 
                           data.response.content || 
                           data.response.response ||
                           JSON.stringify(data.response);
        }
      } else {
        responseContent = data.response || 'No response content';
      }

      const aiMessage: Message = {
        type: 'ai',
        content: responseContent,
        id: `ai-${Date.now()}`,
        modelInfo: modelInfo ?? undefined
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        type: 'ai',
        content: error instanceof Error ? error.message : 'An error occurred while processing your request.',
        id: `error-${Date.now()}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setInput('');
      setFile(null);
    }
  }

  return (
    <ClientOnly>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="w-[800px] backdrop-blur-sm bg-white/80 dark:bg-gray-900/80 shadow-xl hover:shadow-2xl transition-shadow duration-300">
          <CardHeader className="border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-500 animate-pulse" />
              <CardTitle className="bg-gradient-to-r from-blue-500 to-purple-500 text-transparent bg-clip-text">
                PR AI Agent
              </CardTitle>
            </div>
            <CardDescription className="text-gray-600 dark:text-gray-300">
              Ask questions about your code or get PR review feedback
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 p-6">
            <div className="h-[500px] overflow-y-auto space-y-4 p-4 border rounded-lg bg-gray-50 dark:bg-gray-800 shadow-inner">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className={`flex ${
                      message.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 shadow-md hover:shadow-lg transition-all duration-200 ${
                        message.type === 'user'
                          ? 'bg-blue-500 text-white transform hover:-translate-y-1'
                          : 'bg-white dark:bg-gray-700 transform hover:-translate-y-1'
                      }`}
                    >
                      {message.type === 'ai' && message.modelInfo && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                          Using {message.modelInfo.name} (temp: {message.modelInfo.temperature})
                        </div>
                      )}
                      {message.type === 'ai' && isLoading ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span>AI is thinking...</span>
                        </div>
                      ) : (
                        <ReactMarkdown className="prose dark:prose-invert max-w-none">
                          {message.content}
                        </ReactMarkdown>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
            <motion.form 
              onSubmit={handleSubmit} 
              className="space-y-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex gap-2">
                <select
                  value={selectedTask}
                  onChange={(e) => setSelectedTask(e.target.value)}
                  className="w-full p-2 border rounded"
                >
                  {Object.entries(availableTasks).map(([key, task]) => (
                    <option key={key} value={key}>
                      {task.name} - {task.description}
                    </option>
                  ))}
                </select>
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  className="shadow-sm hover:shadow transition-shadow duration-200"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  className="shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1"
                >
                  <Upload className="h-4 w-4" />
                </Button>
                <Button 
                  type="submit" 
                  size="icon"
                  disabled={isLoading}
                  className="shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileChange}
                accept=".js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.cs,.go,.rb,.php"
              />
              {file && (
                <div className="text-sm text-muted-foreground">
                  Selected file: {file.name}
                </div>
              )}
            </motion.form>
          </CardContent>
        </Card>
      </motion.div>
    </ClientOnly>
  )
}