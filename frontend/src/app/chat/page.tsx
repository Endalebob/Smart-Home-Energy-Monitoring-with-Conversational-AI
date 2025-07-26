'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ExampleQuery {
  query: string;
  description: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [examples, setExamples] = useState<ExampleQuery[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const exampleQueries: ExampleQuery[] = [
    {
      query: "How much energy did my fridge use yesterday?",
      description: "Get energy consumption for a specific device"
    },
    {
      query: "Which devices are using the most power?",
      description: "Find your highest energy consumers"
    },
    {
      query: "Show me my energy summary for today",
      description: "Get an overview of today's energy usage"
    },
    {
      query: "Compare energy usage between my devices",
      description: "Compare consumption across devices"
    },
    {
      query: "What's the power consumption of my AC?",
      description: "Check specific device power usage"
    },
    {
      query: "How much energy did I use last month?",
      description: "Get historical energy data"
    }
  ];

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    setExamples(exampleQueries);
    
    // Add welcome message
    setMessages([{
      id: '1',
      type: 'assistant',
      content: "Hello! I'm your Smart Home Energy Assistant. I can help you understand your energy usage, compare devices, and provide insights about your smart home's power consumption. Try asking me questions like 'How much energy did my fridge use yesterday?' or 'Which devices are using the most power?'",
      timestamp: new Date()
    }]);
  }, [router]);

  // Redirect if not authenticated
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      console.log('Sending chat request with token:', token ? 'present' : 'missing');
      console.log('Request URL:', `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/query`);
      console.log('Request body:', { query: inputValue });
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: inputValue }),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (response.ok) {
        const data = await response.json();
        console.log('Chat response:', data); // Debug log
        
        // Handle different response structures
        const responseText = data.answer || data.response || data.message || data.content || JSON.stringify(data);
        
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: responseText,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorData = await response.json();
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `Sorry, I encountered an error: ${errorData.detail || 'Unable to process your request'}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I\'m having trouble connecting to the server. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (query: string) => {
    setInputValue(query);
  };



  const clearChat = () => {
    setMessages([{
      id: '1',
      type: 'assistant',
      content: "Hello! I'm your Smart Home Energy Assistant. I can help you understand your energy usage, compare devices, and provide insights about your smart home's power consumption. Try asking me questions like 'How much energy did my fridge use yesterday?' or 'Which devices are using the most power?'",
      timestamp: new Date()
    }]);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-lg h-[600px] flex flex-col">
              {/* Chat Header */}
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-medium text-gray-900">AI Energy Assistant</h2>
                  <p className="text-sm text-gray-500">Ask me anything about your energy usage</p>
                </div>
                <button
                  onClick={clearChat}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Clear Chat
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-indigo-200' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input Form */}
              <div className="px-6 py-4 border-t border-gray-200">
                <form onSubmit={handleSubmit} className="flex space-x-4">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Ask about your energy usage..."
                    className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !inputValue.trim()}
                    className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Send
                  </button>
                </form>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Example Queries</h3>
              <div className="space-y-3">
                {examples.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(example.query)}
                    className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <p className="text-sm font-medium text-gray-900 mb-1">
                      {example.query}
                    </p>
                    <p className="text-xs text-gray-500">
                      {example.description}
                    </p>
                  </button>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-900 mb-2">AI Capabilities</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• Energy usage analysis</li>
                  <li>• Device comparisons</li>
                  <li>• Historical data queries</li>
                  <li>• Power consumption insights</li>
                  <li>• Efficiency recommendations</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 