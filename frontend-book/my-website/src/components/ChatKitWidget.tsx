import React, { useState, useRef, useEffect } from 'react';

const API_URL = 'http://127.0.0.1:8000/api/v1/chat';

const ChatKitWidget = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Generate session ID if not exists
  useEffect(() => {
    if (!sessionId) {
      setSessionId(Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15));
    }
  }, [sessionId]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Send message handler
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessageText = inputValue.trim();

    // Add user message
    const userMessage = { role: 'user', content: userMessageText, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get selected text
      const selectedText = window.getSelection().toString().trim();

      // Payload for the API call
      const payload = {
        session_id: sessionId,
        message: selectedText ? `${userMessageText} - Context: ${selectedText}` : userMessageText,
        mode: selectedText ? "selected-text" : "full-book"
      };

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // Add assistant response to chat
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        sources: data.sources || [],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to chat
      const errorMessage = {
        role: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div style={{
      height: 'calc(100vh - var(--ifm-navbar-height))',
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <div style={{
        flex: 1,
        padding: '1rem',
        overflowY: 'auto',
        backgroundColor: '#f9f9f9',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
      }}>
        {messages.length === 0 ? (
          <div style={{
            textAlign: 'center',
            color: '#666',
            fontStyle: 'italic',
            marginTop: '20px',
            padding: '1rem'
          }}>
            <h3>Welcome to the Physical AI Assistant! 🚀</h3>
            <p>Ask me anything about:</p>
            <ul style={{textAlign: 'left', maxWidth: '500px', margin: '1rem auto', paddingLeft: '1.5rem'}}>
              <li>Physical AI concepts and architecture</li>
              <li>Humanoid robotics and control systems</li>
              <li>ROS 2 fundamentals</li>
              <li>Digital twin simulation</li>
              <li>Vision-Language-Action systems</li>
              <li>Capstone AI robot pipelines</li>
            </ul>
            <p>I'm trained on the entire Physical AI & Humanoid Robotics curriculum.</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              style={{
                maxWidth: '85%',
                padding: '0.75rem 1rem',
                borderRadius: '12px',
                backgroundColor:
                  msg.role === 'user' ? '#007cba' :
                  msg.role === 'error' ? '#ffcdd2' : '#e3f2fd',
                color: msg.role === 'user' ? 'white' :
                      msg.role === 'error' ? '#c62828' : '#1a237e',
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                wordWrap: 'break-word',
                position: 'relative',
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '0.5rem',
                fontSize: '0.85rem',
                fontWeight: 'bold',
              }}>
                <span style={{
                  color: msg.role === 'user' ? 'rgba(255, 255, 255, 0.8)' :
                         msg.role === 'error' ? '#c62828' : '#666',
                }}>
                  {msg.role === 'user' ? '👤 You' : msg.role === 'error' ? '❌ Error' : '🤖 Assistant'}
                </span>
                <span style={{ color: '#999' }}>{formatTime(msg.timestamp)}</span>
              </div>
              <div style={{ lineHeight: '1.5' }}>
                {msg.content}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div style={{
                  marginTop: '0.75rem',
                  paddingTop: '0.75rem',
                  borderTop: '1px dashed #ddd',
                  fontSize: '0.85rem',
                }}>
                  <details>
                    <summary>Sources ({msg.sources.length})</summary>
                    <ul style={{ marginTop: '0.5rem', paddingLeft: '1.25rem' }}>
                      {msg.sources.map((source, idx) => (
                        <li key={idx}>
                          <strong>Source {idx + 1}:</strong> {source.content_snippet}
                        </li>
                      ))}
                    </ul>
                  </details>
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div style={{
            maxWidth: '85%',
            padding: '0.75rem 1rem',
            borderRadius: '12px',
            backgroundColor: '#e3f2fd',
            color: '#1a237e',
            alignSelf: 'flex-start',
            display: 'flex',
            gap: '5px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <span style={{ width: '8px', height: '8px', backgroundColor: '#999', borderRadius: '50%', display: 'inline-block', animation: 'typing 1.4s infinite ease-in-out' }}></span>
              <span style={{ width: '8px', height: '8px', backgroundColor: '#999', borderRadius: '50%', display: 'inline-block', animation: 'typing 1.4s infinite ease-in-out', animationDelay: '0.2s' }}></span>
              <span style={{ width: '8px', height: '8px', backgroundColor: '#999', borderRadius: '50%', display: 'inline-block', animation: 'typing 1.4s infinite ease-in-out', animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div style={{
        padding: '10px',
        backgroundColor: 'white',
        borderTop: '1px solid #e0e0e0',
      }}>
        <div style={{ display: 'flex', gap: '5px' }}>
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about Physical AI, robotics, ROS 2, digital twins..."
            rows={2}
            style={{
              flex: 1,
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              resize: 'none',
              fontSize: '14px',
              maxHeight: '80px',
            }}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim()}
            style={{
              padding: '10px 15px',
              backgroundColor: '#007cba',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
            }}
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes typing {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-5px); }
        }
      `}</style>
    </div>
  );
};

export default ChatKitWidget;
