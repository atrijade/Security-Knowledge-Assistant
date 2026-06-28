import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [activeCardIndex, setActiveCardIndex] = useState(null);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom of the chat list
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userQuestion = query;
    setQuery('');
    setError(null);
    setLoading(true);

    // Add user message to chat history
    setMessages((prev) => [...prev, { sender: 'user', text: userQuestion }]);

    try {
      const response = await fetch('http://localhost:8080/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userQuestion }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // Update chat with LLM response
      setMessages((prev) => [...prev, { sender: 'assistant', text: data.answer }]);
      
      // Update context sources list
      setSources(data.chunks || []);
      setActiveCardIndex(null); // Reset highlighted card

    } catch (err) {
      console.error(err);
      setError(err.message || 'An error occurred while connecting to the backend.');
      setMessages((prev) => [
        ...prev,
        { 
          sender: 'assistant', 
          text: `⚠️ Error: ${err.message || 'Could not reach the RAG API server.'}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="logo-icon">VM</div>
          <h1>Vulnerability RAG Assistant</h1>
        </div>
        <div className="system-status">
          <div className="status-dot"></div>
          <span>Active</span>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="workspace">
        {/* Chat Console */}
        <section className="chat-console">
          <div className="messages-list">
            {messages.length === 0 ? (
              <div className="empty-state animate-fade-in">
                <div className="empty-icon">🛡️</div>
                <h3>Secure RAG Console</h3>
                <p>Submit questions about cybersecurity vulnerabilities or database details. The assistant will answer using vector knowledge bases.</p>
              </div>
            ) : (
              messages.map((msg, idx) => {
                const isError = msg.text.startsWith('⚠️ Error:');
                return (
                  <div key={idx} className={`message-wrapper ${msg.sender} ${isError ? 'error-message' : ''}`}>
                    <div className="message-meta">
                      {msg.sender === 'user' ? 'You' : 'Gemini'}
                    </div>
                    <div className={`message-bubble ${isError ? 'error-bubble' : ''}`}>{msg.text}</div>
                  </div>
                );
              })
            )}
            
            {loading && (
              <div className="loading-indicator animate-fade-in">
                <div className="spinner"></div>
                <span>Gemini is generating response...</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="input-area">
            <form onSubmit={handleSend} className="input-container">
              <input
                type="text"
                placeholder="Ask about vulnerabilities (e.g. What is SQL Injection?)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
              <button 
                type="submit" 
                className="send-button"
                disabled={loading || !query.trim()}
              >
                Send <span>⚡</span>
              </button>
            </form>
          </div>
        </section>

        {/* Sidebar - Retrieved Sources */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <h2>Retrieved Knowledge</h2>
            <p>Database chunks supporting the response</p>
          </div>

          <div className="sources-list">
            {sources.length === 0 ? (
              <div className="no-sources animate-fade-in">
                <p>Submit a question to see the matching vector database chunks here.</p>
              </div>
            ) : (
              sources.map((src, idx) => (
                <div 
                  key={idx} 
                  className={`source-card ${activeCardIndex === idx ? 'active' : ''}`}
                  onClick={() => setActiveCardIndex(activeCardIndex === idx ? null : idx)}
                >
                  <div className="source-meta">
                    <span className="source-title" title={src.source}>
                      📄 {src.source}
                    </span>
                    <span className={`source-distance ${src.distance < 0.35 ? 'cos' : ''}`}>
                      d: {src.distance.toFixed(4)}
                    </span>
                  </div>
                  <div className="source-snippet">{src.text}</div>
                </div>
              ))
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;
