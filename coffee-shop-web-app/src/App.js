import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import './App.css';

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  // Check API connection on component mount
  useEffect(() => {
    checkConnection();
  }, []);

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const checkConnection = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setIsConnected(true);
      }
    } catch (error) {
      console.error('API connection failed:', error);
      setIsConnected(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input: {
            messages: [{ role: 'user', content: inputMessage }]
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Add bot response to chat
      const botMessage = {
        role: 'assistant',
        content: typeof data.response === 'string' ? data.response : JSON.stringify(data.response, null, 2),
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}. Make sure the FastAPI server is running on http://localhost:8000`,
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="chat-app">
      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <div className="header-content">
            <div className="header-info">
              <Bot className="header-icon" />
              <div className="header-text">
                <h1 className="header-title">MISS MARY COFFEE SHOP AI ASSISTANT</h1>
                <p className="connection-status">
                  {isConnected ? '🟢 Connected to API' : '🔴 API Disconnected'}
                </p>
              </div>
            </div>
            <button onClick={clearChat} className="clear-button">
              Clear Chat
            </button>
          </div>
        </div>

        {/* Messages Container */}
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <Bot className="welcome-icon" />
              <p className="welcome-title">Welcome to COFFEE SHOP AI ASSISTANT</p>
              <p className="welcome-subtitle">Start a conversation by typing a message below.</p>
              <div className="welcome-examples">
                <p className="examples-title">Example messages:</p>
                <p className="example-text">"Give me the best coffee in your shop for a romantic dinner"</p>
                <p className="example-text">"What services do you offer?"</p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message-wrapper ${message.role}`}>
                <div className={`message-bubble ${message.role} ${message.isError ? 'error' : ''}`}>
                  <div className="message-header">
                    {message.role === 'user' ? (
                      <User className="message-icon" />
                    ) : (
                      <Bot className="message-icon" />
                    )}
                    <span className="message-sender">
                      {message.role === 'user' ? 'You' : 'Agent'}
                    </span>
                  </div>
                  <p className="message-content">{message.content}</p>
                  <p className="message-timestamp">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p> 
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="message-wrapper assistant">
              <div className="message-bubble assistant loading">
                <div className="message-header">
                  <Bot className="message-icon" />
                  <span className="message-sender">Agent</span>
                </div>
                <div className="loading-content">
                  <Loader2 className="loading-spinner" />
                  <span className="loading-text">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="message-input"
              disabled={isLoading || !isConnected}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim() || !isConnected}
              className="send-button"
            >
              {isLoading ? (
                <Loader2 className="send-icon loading" />
              ) : (
                <Send className="send-icon" />
              )}
            </button>
          </div>
          {!isConnected && (
            <p className="connection-error">
              ⚠️ Cannot connect to API. Make sure FastAPI server is running on http://localhost:8000
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatApp;