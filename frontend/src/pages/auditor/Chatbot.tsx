import { useState, useRef, useEffect } from 'react'
import { Send, User, Bot, BookOpen, AlertCircle, FileText, ChevronRight, Info, Activity } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import api from '../../services/api/auth'

interface Message {
  id: string
  role: 'user' | 'ai'
  content: string
  timestamp: Date
  citations?: string[]
}

const AuditorChatbot = () => {
  const { user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'ai',
      content: "Welcome to the Deloitte AI Audit Assistant. I am trained on our firm's latest risk methodologies, compliance frameworks, and historical audit guidelines. How can I assist your investigation today?",
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const handleSendMessage = (e?: React.FormEvent) => {
    e?.preventDefault()
    
    if (!inputValue.trim()) return

    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, newUserMessage])
    setInputValue('')
    setIsTyping(true)

    // Simulate AI parsing rules and responding
    const fetchAiResponse = async () => {
      try {
        const response = await api.post('/chatbot/query', { query: inputValue })
        if (response.data) {
          const newAiMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'ai',
            content: response.data.text,
            citations: response.data.citations,
            timestamp: new Date()
          }
          setMessages(prev => [...prev, newAiMessage])
        }
      } catch (err) {
        console.error(err)
        // Fallback for demo without backend
        setTimeout(() => {
          const newAiMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'ai',
            content: "Based on Deloitte's Risk Assessment Framework, this is an offline mock response since the backend could not be reached.",
            citations: ["Offline Mode Cache"],
            timestamp: new Date()
          }
          setMessages(prev => [...prev, newAiMessage])
          setIsTyping(false)
        }, 1500)
      } finally {
        setIsTyping(false)
      }
    }
    fetchAiResponse()
  }

  const handleSuggestedQuery = (query: string) => {
    setInputValue(query)
    // Small delay to allow state to update before sending
    setTimeout(() => {
      const formEvent = new Event('submit', { bubbles: true, cancelable: true }) as unknown as React.FormEvent
      handleSendMessage(formEvent)
    }, 50)
  }

  return (
    <div className="flex h-full bg-slate-900 border-l border-slate-800">
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative">
        {/* Chat Header */}
        <div className="h-16 px-6 border-b border-slate-700/50 flex items-center justify-between bg-slate-900/50 backdrop-blur-md absolute top-0 w-full z-10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-teal-500/20 flex flex-col items-center justify-center border border-teal-500/30">
              <BookOpen className="w-4 h-4 text-teal-400" />
            </div>
            <div>
              <h2 className="text-white font-semibold">Rules & Regulations Assistant</h2>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                Deloitte Internal Knowledge Base Connected
              </div>
            </div>
          </div>
          <button className="text-slate-400 hover:text-white transition-colors">
            <Info className="w-5 h-5" />
          </button>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 pt-24 pb-32 scroll-smooth">
          <div className="max-w-3xl mx-auto space-y-8">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''} animate-fade-in`}>
                
                {/* Avatar */}
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 border border-blue-500 text-white' 
                    : 'bg-teal-500/20 border border-teal-500/30 text-teal-400'
                }`}>
                  {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>

                {/* Message Bubble */}
                <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[80%]`}>
                  <div className="flex items-center gap-2 mb-1 px-1">
                    <span className="text-sm font-medium text-slate-300">
                      {msg.role === 'user' ? (user?.firstName || 'Auditor') : 'AI Assistant'}
                    </span>
                    <span className="text-xs text-slate-500">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  
                  <div className={`p-4 rounded-2xl shadow-lg leading-relaxed text-sm ${
                    msg.role === 'user' 
                      ? 'bg-blue-600/20 border border-blue-500/30 text-blue-50 rounded-tr-sm' 
                      : 'bg-slate-800/80 border border-slate-700 text-slate-200 rounded-tl-sm'
                  }`}>
                    {msg.content}
                  </div>

                  {/* Citations */}
                  {msg.citations && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {msg.citations.map((cite, idx) => (
                        <div key={idx} className="flex items-center gap-1.5 px-2 py-1 bg-slate-800 border border-slate-700 rounded-md text-[10px] text-slate-400 uppercase tracking-wider font-mono">
                          <FileText className="w-3 h-3 text-teal-500" />
                          {cite}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-4 animate-fade-in">
                <div className="w-10 h-10 rounded-xl bg-teal-500/20 border border-teal-500/30 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-teal-400" />
                </div>
                <div className="bg-slate-800/80 border border-slate-700 rounded-2xl rounded-tl-sm p-4 flex items-center gap-2">
                  <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 w-full bg-gradient-to-t from-slate-900 via-slate-900 to-transparent pt-10 pb-6 px-6">
          <div className="max-w-3xl mx-auto">
            
            {/* Suggested Queries */}
            {messages.length === 1 && (
              <div className="flex gap-2 overflow-x-auto pb-4 no-scrollbar">
                {[
                  "Explain the rules for foreign vendor payments exceeding $50k.",
                  "What justifies a risk score of 90 on a duplicate invoice?",
                  "Show me the standard procedure for investigating off-hours processing."
                ].map((query, idx) => (
                  <button 
                    key={idx}
                    onClick={() => handleSuggestedQuery(query)}
                    className="flex-shrink-0 px-4 py-2 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 rounded-full transition-colors flex items-center gap-2 whitespace-nowrap"
                  >
                    <AlertCircle className="w-3 h-3 text-teal-500" />
                    {query}
                  </button>
                ))}
              </div>
            )}

            <form onSubmit={handleSendMessage} className="relative group">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about compliance rules, risk strategies, or investigation procedures..."
                className="w-full bg-slate-800/80 border border-slate-700 text-white rounded-2xl pl-5 pr-14 py-4 focus:outline-none focus:border-teal-500/50 focus:ring-1 focus:ring-teal-500/50 transition-all shadow-lg backdrop-blur-sm"
              />
              <button 
                type="submit"
                disabled={!inputValue.trim() || isTyping}
                className={`absolute right-2 top-2 bottom-2 aspect-square flex items-center justify-center rounded-xl transition-all ${
                  inputValue.trim() && !isTyping 
                    ? 'bg-teal-500 text-white shadow-[0_0_15px_theme("colors.teal.500/0.4")] hover:bg-teal-400' 
                    : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                }`}
              >
                <Send className="w-5 h-5 ml-1" />
              </button>
            </form>
            <div className="text-center mt-3">
              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold flex items-center justify-center gap-2">
                <Activity className="w-3 h-3 text-teal-500/50" />
                AI-Generated insights. Verify against official documentation.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Context/Knowledge Base */}
      <div className="w-80 hidden xl:flex flex-col bg-slate-900/50 border-l border-slate-800/50">
        <div className="p-6 border-b border-slate-800/50">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-2">Active Context</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            The AI is actively connected to the Firm's compliance graph databases. It automatically links responses to relevant sections in the methodolgy library.
          </p>
        </div>
        
        <div className="p-6 flex-1 overflow-y-auto">
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Referenced Documents</h4>
          <div className="space-y-3">
            {[
              { title: "Risk Framework 2024", type: "PDF", size: "2.4 MB" },
              { title: "Procurement Fraud v3", type: "DOCX", size: "1.1 MB" },
              { title: "AML Compliance Guidelines", type: "PDF", size: "5.7 MB" }
            ].map((doc, idx) => (
              <div key={idx} className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-xl hover:bg-slate-800 transition-colors cursor-pointer group">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-4 h-4 text-teal-500" />
                  </div>
                  <div>
                    <h5 className="text-sm font-medium text-slate-200 group-hover:text-teal-400 transition-colors">{doc.title}</h5>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-slate-500 font-mono bg-slate-900 px-1 rounded">{doc.type}</span>
                      <span className="text-[10px] text-slate-500">{doc.size}</span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-600 ml-auto mt-2 group-hover:text-teal-400 transition-colors" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  )
}

export default AuditorChatbot
