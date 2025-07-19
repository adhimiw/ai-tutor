import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader, Paperclip, X, Wifi, WifiOff, AlertCircle } from 'lucide-react'
import axios from 'axios'
import FileUpload from '../components/FileUpload'

const ChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hello! I'm Neto, your AI tutor powered by Google Gemini 2.5 Flash with vector memory. I can remember our previous conversations and help you learn more effectively. What would you like to learn about today?",
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('connected')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Health check on component mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/memory/stats', {
          timeout: 5000
        })
        if (response.status === 200) {
          setConnectionStatus('connected')
          console.log('Backend health check passed:', response.data)
        }
      } catch (error) {
        console.warn('Backend health check failed:', error.message)
        setConnectionStatus('disconnected')
      }
    }

    checkBackendHealth()
  }, [])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if ((!inputMessage.trim() && selectedFiles.length === 0) || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      files: selectedFiles.map(file => ({
        name: file.name,
        type: file.type,
        size: file.size
      })),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentMessage = inputMessage
    const currentFiles = [...selectedFiles]
    setInputMessage('')
    setSelectedFiles([])
    setShowFileUpload(false)
    setIsLoading(true)

    try {
      setConnectionStatus('connecting')

      // Prepare form data for file upload
      const formData = new FormData()
      formData.append('message', currentMessage)
      formData.append('conversationId', conversationId || '')
      formData.append('userId', 'anonymous') // TODO: Implement proper user authentication

      // Add files to form data
      currentFiles.forEach((file, index) => {
        formData.append('files', file)
      })

      // Call the enhanced API with vector memory and file support
      const response = await axios.post('http://localhost:5000/api/chat', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 30000 // 30 second timeout
      })

      setConnectionStatus('connected')

      if (response.data.success) {
        const aiResponse = {
          id: Date.now() + 1,
          type: 'ai',
          content: response.data.response,
          timestamp: new Date(),
          filesProcessed: response.data.filesProcessed || 0
        }

        setMessages(prev => [...prev, aiResponse])

        // Update conversation ID if it's a new conversation
        if (!conversationId && response.data.conversationId) {
          setConversationId(response.data.conversationId)
        }
      } else {
        throw new Error(response.data.error || 'Failed to get response')
      }

      setIsLoading(false)
    } catch (error) {
      console.error('Error sending message:', error)
      setConnectionStatus('error')

      // Show detailed error message to user
      let errorMessage = 'Sorry, I encountered an error while processing your message. Please try again.'

      if (error.response) {
        // Server responded with error status
        errorMessage = `Server error: ${error.response.data?.error || error.response.statusText}`
        setConnectionStatus('connected') // Server is responding, just an error
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'Unable to connect to the server. Please check your internet connection and try again.'
        setConnectionStatus('disconnected')
      } else if (error.code === 'ECONNABORTED') {
        // Request timeout
        errorMessage = 'Request timed out. The server might be busy. Please try again.'
        setConnectionStatus('timeout')
      } else {
        // Something else happened
        errorMessage = `Error: ${error.message}`
      }

      const errorResponse = {
        id: Date.now() + 1,
        type: 'ai',
        content: errorMessage,
        timestamp: new Date(),
        isError: true,
        retryData: {
          message: currentMessage,
          files: currentFiles
        }
      }
      setMessages(prev => [...prev, errorResponse])
      setIsLoading(false)
    }
  }

  const handleRetry = async (retryData) => {
    // Remove the error message
    setMessages(prev => prev.filter(msg => !msg.isError))

    // Retry the message
    setInputMessage(retryData.message)
    setSelectedFiles(retryData.files || [])

    // Trigger send message
    const fakeEvent = { preventDefault: () => {} }
    await handleSendMessage(fakeEvent)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card h-[600px] md:h-[700px] lg:h-[800px] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Neto - AI Tutor
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Powered by Google Gemini 2.5 Pro
              </p>
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {connectionStatus === 'connected' && (
              <div className="flex items-center space-x-1 text-green-600">
                <Wifi className="w-4 h-4" />
                <span className="text-xs">Connected</span>
              </div>
            )}
            {connectionStatus === 'connecting' && (
              <div className="flex items-center space-x-1 text-yellow-600">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-xs">Connecting...</span>
              </div>
            )}
            {(connectionStatus === 'disconnected' || connectionStatus === 'error' || connectionStatus === 'timeout') && (
              <div className="flex items-center space-x-1 text-red-600">
                <WifiOff className="w-4 h-4" />
                <span className="text-xs">
                  {connectionStatus === 'timeout' ? 'Timeout' : 'Disconnected'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl ${
                message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-blue-600' 
                    : 'bg-gradient-to-r from-purple-500 to-pink-500'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-white" />
                  )}
                </div>
                
                <div className={`rounded-lg px-4 py-2 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                }`}>
                  {message.content && <p className="text-sm">{message.content}</p>}

                  {/* File attachments */}
                  {message.files && message.files.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {message.files.map((file, index) => (
                        <div key={index} className={`text-xs px-2 py-1 rounded ${
                          message.type === 'user'
                            ? 'bg-blue-500 bg-opacity-50'
                            : 'bg-gray-200 dark:bg-gray-600'
                        }`}>
                          📎 {file.name} ({Math.round(file.size / 1024)}KB)
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Files processed indicator for AI responses */}
                  {message.type === 'ai' && message.filesProcessed > 0 && (
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      ✅ Analyzed {message.filesProcessed} file{message.filesProcessed > 1 ? 's' : ''}
                    </div>
                  )}

                  {/* Retry button for error messages */}
                  {message.isError && message.retryData && (
                    <button
                      onClick={() => handleRetry(message.retryData)}
                      className="mt-2 text-xs bg-red-100 hover:bg-red-200 text-red-700 px-2 py-1 rounded transition-colors"
                      disabled={isLoading}
                    >
                      🔄 Retry
                    </button>
                  )}

                  <p className={`text-xs mt-1 ${
                    message.type === 'user'
                      ? 'text-blue-100'
                      : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="flex items-start space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
                  <div className="flex items-center space-x-2">
                    <Loader className="w-4 h-4 animate-spin text-gray-500" />
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Neto is thinking...
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* File Upload Area */}
        <AnimatePresence>
          {showFileUpload && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t border-gray-200 dark:border-gray-700 p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                  Attach Files
                </h3>
                <button
                  onClick={() => setShowFileUpload(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <FileUpload
                onFilesSelected={setSelectedFiles}
                maxFiles={3}
                maxSize={20 * 1024 * 1024}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setShowFileUpload(!showFileUpload)}
              className={`relative p-2 rounded-md transition-colors ${
                showFileUpload || selectedFiles.length > 0
                  ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-400'
                  : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
              }`}
              disabled={isLoading}
            >
              <Paperclip className="w-4 h-4" />
              {selectedFiles.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {selectedFiles.length}
                </span>
              )}
            </button>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask me anything about learning, programming, or any subject..."
              className="input-field flex-1"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={(!inputMessage.trim() && selectedFiles.length === 0) || isLoading}
              className="btn-primary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          {/* Selected files preview */}
          {selectedFiles.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-md px-2 py-1 text-xs"
                >
                  <span className="text-gray-600 dark:text-gray-300">
                    📎 {file.name}
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      const newFiles = selectedFiles.filter((_, i) => i !== index)
                      setSelectedFiles(newFiles)
                    }}
                    className="text-gray-400 hover:text-red-600 ml-1"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </form>
      </motion.div>
    </div>
  )
}

export default ChatPage
