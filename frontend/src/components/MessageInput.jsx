import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import './MessageInput.css';

const MessageInput = ({ onSendMessage, disabled, isLoading }) => {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !disabled && !isLoading) {
            onSendMessage(input);
            setInput('');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="message-input">
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={disabled ? "Select a digital twin to start chatting..." : "Ask a question..."}
                disabled={disabled || isLoading}
                className="input-field"
            />
            <button
                type="submit"
                disabled={!input.trim() || disabled || isLoading}
                className="send-button"
            >
                {isLoading ? <Loader2 className="loading-icon" size={20} /> : <Send size={20} />}
            </button>
        </form>
    );
};

export default MessageInput;
