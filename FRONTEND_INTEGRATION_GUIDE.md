# Frontend Integration Guide

Quick reference for building the frontend for the Digital Twin AI Agent.

---

## 🔌 API Endpoint

**Base URL:** `http://localhost:8000`

### POST /query - Send a Query

**Send this request for each user message:**

```javascript
const response = await axios.post('http://localhost:8000/query', {
    query: "What's the current temperature?",
    entity_context: {
        entity_id: 40976504,
        entity_name: "Heat Exchanger HX00-A3",
        entity_type: "HeatExchanger"
    },
    session_id: "entity-40976504"  // Use entity_id as session identifier
});

// Response
console.log(response.data.response);  // The AI's answer
```

**Request fields:**
- `query` (required): User's question
- `entity_context.entity_id` (required): Entity ID to ask about
- `entity_context.entity_name`, `entity_context.entity_type` (optional): Entity details
- `session_id` (optional): Use `entity-${entityId}` to maintain conversation memory. If not sent, backend uses `"default"` and conversations won't have context between messages

---

## 📊 Digital Twin Entities

| ID | Name | Type |
|---|---|---|
| 12288 | Heat Exchanger HX17-A1 | HeatExchanger |
| 24808 | Equipment Unit EU-24808 | Equipment |
| 40976504 | Heat Exchanger HX00-A3 | HeatExchanger |
| 28904 | Equipment Unit EU-28904 | Equipment |
| 40964304 | Equipment Unit EU-40964304 | Equipment |

---

## 💬 How to Build a Conversation

Store messages in state and display them as a list:

```javascript
import React, { useState } from 'react';
import axios from 'axios';

const ChatInterface = () => {
    const [selectedEntity, setSelectedEntity] = useState(null);
    const [messages, setMessages] = useState([]);
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSendMessage = async () => {
        if (!query.trim() || !selectedEntity) return;

        // Add user message to conversation
        const userMessage = { role: 'user', content: query };
        setMessages(prev => [...prev, userMessage]);
        setQuery('');
        setIsLoading(true);

        try {
            // Make API call
            const response = await axios.post('http://localhost:8000/query', {
                query,
                entity_context: {
                    entity_id: selectedEntity.id,
                    entity_name: selectedEntity.name,
                    entity_type: selectedEntity.type
                },
                session_id: `entity-${selectedEntity.id}`  // Keep same session for context
            });

            // Add AI response to conversation
            const assistantMessage = {
                role: 'assistant',
                content: response.data.response
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            // Remove user message if API fails
            setMessages(prev => prev.slice(0, -1));
            alert('Error: ' + error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSelectEntity = (entity) => {
        setSelectedEntity(entity);
        setMessages([]);  // Clear chat when switching entity
    };

    return (
        <div>
            {/* Entity selector */}
            <select onChange={(e) => {
                const entity = ENTITIES.find(e => e.id === parseInt(e.target.value));
                handleSelectEntity(entity);
            }}>
                <option>Select an entity...</option>
                {ENTITIES.map(e => (
                    <option key={e.id} value={e.id}>{e.name}</option>
                ))}
            </select>

            {/* Display messages */}
            <div className="messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
            </div>

            {/* Input */}
            <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={!selectedEntity || isLoading}
                placeholder="Ask about the entity..."
            />
            <button onClick={handleSendMessage} disabled={!selectedEntity || isLoading}>
                {isLoading ? 'Loading...' : 'Send'}
            </button>
        </div>
    );
};

const ENTITIES = [
    { id: 12288, name: 'Heat Exchanger HX17-A1', type: 'HeatExchanger' },
    { id: 24808, name: 'Equipment Unit EU-24808', type: 'Equipment' },
    { id: 40976504, name: 'Heat Exchanger HX00-A3', type: 'HeatExchanger' },
    { id: 28904, name: 'Equipment Unit EU-28904', type: 'Equipment' },
    { id: 40964304, name: 'Equipment Unit EU-40964304', type: 'Equipment' }
];
```

**That's it!** The key points:
- Keep `messages` state for displaying the conversation
- When user sends a message, add it to `messages` immediately
- Call the API with `session_id: entity-${entityId}`
- When response comes back, add the AI's response to `messages`
- Clear `messages` when switching to a new entity

---

## 🛠 Setup

1. Install axios: `npm install axios`
2. Start backend: `uvicorn api:app --host 0.0.0.0 --port 8000 --reload`
3. Test the API: Visit `http://localhost:8000/docs`

