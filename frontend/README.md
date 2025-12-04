# Digital Twin AI Assistant - Frontend

A modern React chatbot interface for the Digital Twin AI Agent.

## Features

✨ **Beautiful UI** - Glassmorphism design with gradient background  
🤖 **Smart Chatbot** - Natural language queries with markdown responses  
🔄 **Entity Selection** - Dropdown to select from 5 digital twin entities  
📱 **Responsive** - Works on desktop and mobile  
🎨 **Modern Stack** - React + Vite for fast development  

## Quick Start

### Prerequisites
- Node.js 20+ 
- Backend running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Available Digital Twins

The app includes these pre-configured entities:

- **12288** - Heat Exchanger HX17-A1
- **24808** - Equipment Unit EU-24808
- **40976504** - Heat Exchanger HX00-A3
- **28904** - Equipment Unit EU-28904
- **40964304** - Equipment Unit EU-40964304

## Usage

1. **Select a Digital Twin** from the dropdown
2. **Ask questions** like:
   - "What's the current temperature?"
   - "Show me efficiency trends for last week"
   - "Analyze all KPIs for the past month"
3. **View responses** with formatted markdown

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx       # Main chat container
│   │   ├── DigitalTwinSelector.jsx # Entity dropdown
│   │   ├── MessageList.jsx         # Chat history
│   │   └── MessageInput.jsx        # Input field
│   ├── services/
│   │   └── api.js                  # Backend API calls
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

## Backend Integration

The frontend connects to the backend API at `http://localhost:8000/query`.

To change the API URL, edit `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:8000';
```

## Build for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Technologies

- **React 18** - UI library
- **Vite** - Build tool
- **Axios** - HTTP client
- **React-Markdown** - Markdown rendering
- **Lucide React** - Icons

## Features Highlight

### Markdown Support
AI responses support full markdown including:
- **Bold text**
- *Italic text*
- Lists
- Code blocks

### Smart Loading States
- Disabled input when no entity selected
- Loading spinner during API calls
- Error messages with retry

### Responsive Design
- Mobile-friendly layout
- Touch-optimized buttons
- Adaptive message widths

## Development

```bash
# Run dev server with hot reload
npm run dev

# Lint code
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

---

Built with ❤️ for Digital Twin Platform
