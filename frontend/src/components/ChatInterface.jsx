import React, { useState } from 'react';
import DigitalTwinSelector from './DigitalTwinSelector';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { sendMessage } from '../services/api';
import { AlertCircle } from 'lucide-react';
import './ChatInterface.css';

const ChatInterface = () => {
    const [selectedTwin, setSelectedTwin] = useState(null);
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSendMessage = async (query) => {
        if (!selectedTwin) {
            setError('Please select a digital twin first');
            return;
        }

        // Add user message
        const userMessage = { role: 'user', content: query };
        setMessages(prev => [...prev, userMessage]);
        setError(null);
        setIsLoading(true);

        try {
            const response = await sendMessage(query, selectedTwin.id);

            // Add assistant message
            const assistantMessage = {
                role: 'assistant',
                content: response.response
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (err) {
            setError(err.message);
            // Remove the user message if API call failed
            setMessages(prev => prev.slice(0, -1));
        } finally {
            setIsLoading(false);
        }
    };

    const handleSelectTwin = (twin) => {
        setSelectedTwin(twin);
        setMessages([]);
        setError(null);
    };

    return (
        <div className="chat-interface">
            {/* Sidebar with selector */}
            <div className="sidebar">
                <div className="sidebar-header">
                    <h2>Digital Twins</h2>
                    <p>Select an entity to chat with</p>
                </div>
                <DigitalTwinSelector
                    selectedTwin={selectedTwin}
                    onSelectTwin={handleSelectTwin}
                />
            </div>

            {/* Main chat area */}
            <div className="main-content">
                <div className="chat-header">
                    <div className="header-content">
                        <h1>
                            {selectedTwin
                                ? `${selectedTwin.name}`
                                : 'Digital Twin AI Assistant'}
                        </h1>
                        <p>
                            {selectedTwin
                                ? `ID: ${selectedTwin.id} • ${selectedTwin.type}`
                                : 'Select a digital twin to start chatting'}
                        </p>
                    </div>
                </div>

                {error && (
                    <div className="error-message">
                        <AlertCircle size={20} />
                        <span>{error}</span>
                    </div>
                )}

                <div className="chat-container">
                    <MessageList messages={messages} />
                    <MessageInput
                        onSendMessage={handleSendMessage}
                        disabled={!selectedTwin}
                        isLoading={isLoading}
                    />
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
