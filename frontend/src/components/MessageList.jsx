import React, { useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import './MessageList.css';

const MessageList = ({ messages }) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="message-list">
            {messages.length === 0 ? (
                <div className="empty-state">
                    <Bot size={48} className="empty-icon" />
                    <h3>Welcome to Digital Twin AI Assistant</h3>
                    <p>Select a digital twin above and start asking questions!</p>
                    <div className="example-queries">
                        <p><strong>Try asking:</strong></p>
                        <ul>
                            <li>"What's the current temperature?"</li>
                            <li>"Show me efficiency trends for last week"</li>
                            <li>"Analyze all KPIs for the past month"</li>
                        </ul>
                    </div>
                </div>
            ) : (
                messages.map((message, index) => (
                    <div key={index} className={`message ${message.role}`}>
                        <div className="message-icon">
                            {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>
                        <div className="message-content">
                            {message.role === 'assistant' ? (
                                <ReactMarkdown>{message.content}</ReactMarkdown>
                            ) : (
                                <p>{message.content}</p>
                            )}
                        </div>
                    </div>
                ))
            )}
            <div ref={messagesEndRef} />
        </div>
    );
};

export default MessageList;
