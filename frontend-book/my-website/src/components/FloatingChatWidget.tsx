import React, { useState, useEffect, useRef } from 'react';

const API_URL = 'http://127.0.0.1:8000/api/v1/chat';

const FloatingChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const sessionIdRef = useRef('');

  useEffect(() => {
    // Generate a simple session ID if not exists
    if (!sessionIdRef.current) {
      sessionIdRef.current = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    }
  }, []);

  // Toggle chat window
  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          // Send both formats to support either backend version
          thread_id: sessionIdRef.current,
          session_id: sessionIdRef.current,
          input: userMessageText,
          message: userMessageText,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botResponseText = '';

      // Temporary bot message placeholder that we will update
      const botMessageId = Date.now();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        id: botMessageId
      }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'assistant.response') {
                botResponseText = data.content; // Backend sends full text in one go usually, but we overwrite
                
                // Update the last message
                setMessages(prev => prev.map(msg => 
                  (msg.id === botMessageId) 
                    ? { ...msg, content: botResponseText } 
                    : msg
                ));
              } else if (data.type === 'error') {
                 console.error("Backend error:", data.content);
                 botResponseText = "Error: " + data.content;
                 setMessages(prev => prev.map(msg => 
                  (msg.id === botMessageId) 
                    ? { ...msg, content: botResponseText, role: 'error' } 
                    : msg
                ));
              }
            } catch (e) {
              console.error('Error parsing JSON line:', e);
            }
          }
        }
      }

      setIsLoading(false);

    } catch (error) {
      console.error('Error sending message:', error);
      // Remove the empty bot placeholder if it exists and add error
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.role !== 'assistant' || msg.content !== '');
        return [...filtered, {
          role: 'error',
          content: 'Error connecting to the chatbot server. Is it running?',
          timestamp: new Date()
        }];
      });
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

  return (
    <>
      {!isOpen ? (
        // Floating button
        <button
          onClick={toggleChat}
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            backgroundColor: '#007cba',
            color: 'white',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            zIndex: 1000,
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          aria-label="Open chat"
        >
          💬
        </button>
      ) : (
        // Chat window
        <div
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            width: '350px',
            height: '500px',
            backgroundColor: 'white',
            borderRadius: '12px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.12)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
            border: '1px solid #e0e0e0',
          }}
        >
          {/* Header */}
          <div
            style={{
              backgroundColor: '#007cba',
              color: 'white',
              padding: '15px',
              borderTopLeftRadius: '12px',
              borderTopRightRadius: '12px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <h3 style={{ margin: 0, fontSize: '16px' }}>AI Assistant</h3>
            <button
              onClick={toggleChat}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '20px',
                cursor: 'pointer',
                padding: '0',
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              padding: '15px',
              overflowY: 'auto',
              backgroundColor: '#f9f9f9',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            {messages.length === 0 ? (
              <div
                style={{
                  textAlign: 'center',
                  color: '#666',
                  fontStyle: 'italic',
                  marginTop: '20px',
                }}
              >
                Start a conversation with our AI assistant!
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  style={{
                    maxWidth: '80%',
                    padding: '10px 15px',
                    borderRadius: '18px',
                    backgroundColor:
                      msg.role === 'user' ? '#007cba' : msg.role === 'error' ? '#ffcdd2' : '#e3f2fd',
                    color: msg.role === 'user' ? 'white' : msg.role === 'error' ? '#c62828' : '#1a237e',
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    wordWrap: 'break-word',
                  }}
                >
                  {msg.content}
                </div>
              ))
            )}
            {isLoading && messages.length > 0 && messages[messages.length - 1].role !== 'assistant' && (
              <div
                style={{
                  maxWidth: '80%',
                  padding: '10px 15px',
                  borderRadius: '18px',
                  backgroundColor: '#e3f2fd',
                  color: '#1a237e',
                  alignSelf: 'flex-start',
                  display: 'flex',
                  gap: '5px',
                }}
              >
                <div>Typing</div>
                <div>.</div>
                <div>.</div>
                <div>.</div>
              </div>
            )}
          </div>

          {/* Input */}
          <div
            style={{
              padding: '10px',
              backgroundColor: 'white',
              borderBottomLeftRadius: '12px',
              borderBottomRightRadius: '12px',
              borderTop: '1px solid #e0e0e0',
            }}
          >
            <div style={{ display: 'flex', gap: '5px' }}>
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                rows={1}
                style={{
                  flex: 1,
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '20px',
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
                  borderRadius: '20px',
                  cursor: 'pointer',
                  fontSize: '16px',
                }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingChatWidget;