import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [activeCardIndex, setActiveCardIndex] = useState(null);
  const [error, setError] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  
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
      setError(err.message || 'An error occurred while connecting to the RAG backend.');
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

  const handleClearChat = () => {
    setMessages([]);
    setSources([]);
    setActiveCardIndex(null);
    setError(null);
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Custom Inline Markdown Parser (handles **bold** and `code`)
  const parseInline = (text) => {
    const regex = /(\*\*.*?\*\*|`.*?`)/g;
    const parts = text.split(regex);
    
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} className="inline-code">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  // Custom block-level Markdown Parser (handles headers, lists, code blocks)
  const renderMarkdown = (text) => {
    if (!text) return '';
    
    const parts = text.split(/(```[\s\S]*?```)/g);
    
    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        const lines = part.slice(3, -3).trim().split('\n');
        let language = '';
        if (lines[0] && !lines[0].includes(' ') && lines[0].length < 15) {
          language = lines.shift();
        }
        const code = lines.join('\n');
        return (
          <pre key={index} className="code-block-container">
            {language && <div className="code-block-lang">{language}</div>}
            <code className="code-block">{code}</code>
          </pre>
        );
      } else {
        const lines = part.split('\n');
        return lines.map((line, lIdx) => {
          const trimmed = line.trim();
          if (trimmed.startsWith('### ')) {
            return <h4 key={lIdx} className="md-h4">{parseInline(trimmed.slice(4))}</h4>;
          }
          if (trimmed.startsWith('## ')) {
            return <h3 key={lIdx} className="md-h3">{parseInline(trimmed.slice(3))}</h3>;
          }
          if (trimmed.startsWith('# ')) {
            return <h2 key={lIdx} className="md-h2">{parseInline(trimmed.slice(2))}</h2>;
          }
          if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
            return <li key={lIdx} className="md-li">{parseInline(trimmed.slice(2))}</li>;
          }
          if (trimmed === '') {
            return <div key={lIdx} className="md-spacing" />;
          }
          return <p key={lIdx} className="md-p">{parseInline(line)}</p>;
        });
      }
    });
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="logo-icon">VM</div>
          <h1>Vulnerability RAG Assistant</h1>
        </div>
        <div className="header-actions">
          {messages.length > 0 && (
            <button className="clear-btn" onClick={handleClearChat}>
              🧹 Clear Chat
            </button>
          )}
          <div className="system-status">
            <div className="status-dot"></div>
            <span>Active</span>
          </div>
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
                <h3>Secure RAG Command Console</h3>
                <p>Submit questions about CVEs, hardening guidelines, or security metrics. The system will retrieve matching vector contexts and synthesize an answer.</p>
                <div className="suggested-queries">
                  <div className="suggestion" onClick={() => setQuery("What is SQL Injection?")}>
                    "What is SQL Injection?"
                  </div>
                  <div className="suggestion" onClick={() => setQuery("Explain Command Injection defenses")}>
                    "Explain Command Injection defenses"
                  </div>
                  <div className="suggestion" onClick={() => setQuery("What are the key statistics from the 2025 DBIR?")}>
                    "What are the statistics in the 2025 DBIR?"
                  </div>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => {
                const isError = msg.text.startsWith('⚠️ Error:');
                return (
                  <div key={idx} className={`message-wrapper ${msg.sender} ${isError ? 'error-message' : ''}`}>
                    <div className="message-meta">
                      {msg.sender === 'user' ? 'You' : 'Gemini'}
                    </div>
                    <div className={`message-bubble ${isError ? 'error-bubble' : ''}`}>
                      {msg.sender === 'assistant' ? renderMarkdown(msg.text) : msg.text}
                      
                      {msg.sender === 'assistant' && !isError && (
                        <button 
                          className="copy-btn" 
                          onClick={() => copyToClipboard(msg.text, idx)}
                          title="Copy Answer"
                        >
                          {copiedIndex === idx ? '✓ Copied' : '🗎 Copy'}
                        </button>
                      )}
                    </div>
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
                placeholder="Ask about cybersecurity vulnerabilities..."
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
            <p>Database chunks supporting the active response</p>
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
