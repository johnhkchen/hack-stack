# 🏢 SF Legacy Business Registry
> Full-stack demo showcasing modern RAG, search, and interactive data visualization

**Stack**: Astro + Svelte + FastAPI + LlamaIndex RAG + Docker

## ⚡ 30-Second Startup

```bash
git clone <repo>
cd hack-stack
just start
```

**That's it.** Working demo with SF business data, RAG assistant, and interactive search.

## 🎯 What You Get

This is a **complete business registry application** with:

- 🔍 **Intelligent Search** - Find businesses by name, type, or neighborhood
- 🤖 **RAG Assistant** - Natural language queries powered by LlamaIndex
- 📊 **Interactive Data Viz** - Neighborhood groupings with expandable cards
- 🎨 **Modern UI** - Astro + Svelte with PicoCSS for clean design
- 🛠️ **API Management** - Auto-discovery with YAML config override
- 📱 **Mobile Responsive** - Works perfectly on all devices

## 🏗️ Architecture Overview

### **Frontend (Astro + Svelte)**
```
├── Astro SSR Pages           # Server-side rendered routes
├── Svelte Islands           # Interactive components with state
├── Unified Search & List    # Single component for cross-island communication
└── PicoCSS Design System   # Clean, semantic styling
```

### **Backend (FastAPI + LlamaIndex)**
```
├── Business Data API        # CRUD operations on business registry
├── RAG Query Endpoint      # LlamaIndex-powered semantic search
├── Business Search API     # Full-text search with filters
├── Metrics & Health       # System monitoring and stats
└── Auto-Discovery Debug   # API endpoint management
```

### **Key Features You'll Learn**

#### **🔗 Svelte Island Communication**
- **Problem**: Astro islands can't communicate directly
- **Solution**: Unified components that manage both search and display
- **Learn**: How to structure reactive state across complex interactions

#### **🤖 RAG Implementation** 
- **LlamaIndex Integration**: Semantic search over business documents
- **Vector Storage**: Persistent embeddings for fast queries
- **Natural Language**: Users ask questions, get contextual answers with sources

#### **🎨 Progressive Enhancement**
- **Search-to-Card Navigation**: Search results scroll to and highlight specific cards
- **Neighborhood Expansion**: Automatically expands collapsed sections
- **Visual Feedback**: Smooth animations and highlight effects

#### **⚙️ API Auto-Discovery**
- **Dynamic Endpoint Detection**: FastAPI route introspection
- **YAML Configuration Override**: Manual categorization and organization
- **Health Monitoring**: Real-time endpoint testing and status

## 🚀 Quick Commands

```bash
# Development (hot reload)
just dev              # Start both frontend + backend
just frontend         # Astro dev server only  
just backend          # FastAPI dev server only

# Demo Preparation
just start            # Start + open browser
just build            # Production build and deploy
just check            # Health check all services

# Container Management  
docker compose up     # Full stack with networking
docker compose down   # Stop all services
```

## 📊 Live Demo Features

### **1. Business Search & Discovery**
- **What it does**: Type in business names, neighborhoods, or types
- **Technical**: Full-text search with autocomplete and filtering
- **Cool part**: Search results have "View Full Details" buttons that scroll to and highlight the actual business card

### **2. RAG Knowledge Assistant**
- **What it does**: Ask natural language questions about SF businesses
- **Technical**: LlamaIndex RAG with embeddings and context retrieval
- **Cool part**: Shows source businesses that contributed to the answer

### **3. Neighborhood Groupings**
- **What it does**: Businesses organized by neighborhood with stats
- **Technical**: Reactive Svelte components with expand/collapse
- **Cool part**: Auto-expands when search directs you to a specific business

### **4. Interactive Business Cards**
- **What it does**: Rich business profiles with cultural narratives
- **Technical**: Progressive disclosure with modals and detailed views
- **Cool part**: Modal overlays with full business history and contact info

### **5. API Debug Interface**
- **What it does**: Monitor and test all backend endpoints
- **Technical**: Auto-discovery with YAML config override
- **Cool part**: Real-time testing with organized collapsible sections

## 🛠️ What Developers Need to Know

### **Frontend Stack**
```typescript
// Astro for SSR + Static Generation
export default {
  output: 'server',      // SSR mode for dynamic content
  adapter: '@astrojs/node', // Node.js deployment
  integrations: ['@astrojs/svelte'] // Svelte islands
}

// Svelte for Interactive Components
<script>
  let searchQuery = '';
  let searchResults = [];
  
  async function searchBusinesses() {
    const response = await fetch('/api/search', { ... });
    searchResults = await response.json();
  }
</script>
```

### **Backend Stack**
```python
# FastAPI with modern Python
from fastapi import FastAPI
from llama_index.core import VectorStoreIndex
import uvicorn

app = FastAPI()

# RAG Implementation
@app.post("/api/v2/rag/query")
async def rag_query(query: RagQueryRequest):
    response = index.as_query_engine().query(query.query)
    return {
        "response": str(response),
        "source_contexts": response.source_nodes
    }
```

### **Data Flow**
```
User Types Query → Svelte Component → FastAPI Endpoint → LlamaIndex → Vector DB
                                  ↓
User Sees Results ← UI Update ← JSON Response ← RAG Processing ← Embeddings
```

## 📁 Project Structure

```
hack-stack/
├── frontend/                    # Astro + Svelte
│   ├── src/
│   │   ├── components/         
│   │   │   ├── BusinessCard.svelte      # Rich business profiles
│   │   │   ├── NeighborhoodCard.svelte  # Collapsible neighborhood groups
│   │   │   ├── RagAssistant.svelte      # LlamaIndex RAG interface
│   │   │   ├── BusinessSearchAndList.svelte # Unified search + display
│   │   │   └── ApiTestsTable.svelte     # API debugging interface
│   │   ├── pages/
│   │   │   ├── index.astro              # Main homepage
│   │   │   └── debug.astro              # API management page
│   │   └── layouts/Layout.astro         # Shared page structure
├── backend/                     # FastAPI + LlamaIndex
│   ├── api/
│   │   ├── routes.py           # HTTP endpoints
│   │   ├── rag.py             # LlamaIndex RAG implementation
│   │   ├── debug.py           # Auto-discovery service
│   │   └── models.py          # Pydantic schemas
│   ├── data/                  # Business registry data
│   │   ├── businesses.json    # Mock business data
│   │   └── documents/         # RAG document storage
│   └── pyproject.toml         # uv dependency management
├── config/
│   └── debug.yaml             # API endpoint organization
├── docker-compose.yml         # Multi-service orchestration
├── justfile                   # Development commands
└── README.md                  # This file
```

## 🎯 Key Learning Outcomes

### **For Frontend Developers**
- **Astro Islands Architecture**: When to use SSR vs client-side hydration
- **Svelte State Management**: Reactive programming with cross-component communication
- **Progressive Enhancement**: Building features that work without JavaScript
- **API Integration**: Handling loading states, errors, and real-time updates

### **For Backend Developers**
- **FastAPI Patterns**: Route organization, dependency injection, error handling
- **RAG Implementation**: Vector databases, embeddings, and context retrieval
- **API Design**: RESTful endpoints with proper status codes and schemas
- **Service Architecture**: Auto-discovery, health checks, and monitoring

### **For Full-Stack Developers**
- **System Integration**: How frontend and backend communicate effectively
- **Data Flow**: From user interaction to database and back
- **Performance**: SSR for SEO, client-side hydration for interactivity
- **DevOps**: Docker containerization and production deployment

## 🚨 Demo Day Resilience

**Built for when everything goes wrong:**
- ✅ **Works offline** - Mock data enables full demo without internet
- ✅ **Fast startup** - 30 seconds from git clone to working demo
- ✅ **Self-contained** - Docker handles all dependencies
- ✅ **Error handling** - Graceful fallbacks for API failures
- ✅ **Mobile ready** - Responsive design works on any device

## 🎬 Development Timeline

**Hour 1: Setup & Data**
- Clone repository and start services
- Understand business data structure
- Explore the interactive UI components

**Hour 2: Backend APIs**
- Examine FastAPI endpoint structure
- Test RAG queries with different questions
- Use the debug interface to monitor API health

**Hour 3: Frontend Components** 
- Study Svelte component architecture
- Modify search functionality
- Customize business card layouts

**Hour 4: Integration & Deployment**
- Add new business data
- Customize RAG responses
- Deploy with Docker compose

## 💼 Technical Interview Talking Points

### **"How did you handle complex state management?"**
*"I used Svelte's reactive state within unified components to solve Astro island communication limitations. The search and business list share state in a single component, enabling features like scroll-to-card navigation."*

### **"How did you implement the RAG system?"**
*"Built with LlamaIndex for vector storage and retrieval. Users ask natural language questions, we embed the query, find similar business documents, and return contextual answers with source attribution."*

### **"How did you ensure mobile responsiveness?"**
*"Used PicoCSS for semantic styling with CSS Grid and Flexbox. Implemented responsive textareas, collapsible cards, and touch-friendly interactions. Tested on various screen sizes with proper breakpoints."*

### **"How did you handle API management?"**
*"Created an auto-discovery system that introspects FastAPI routes and organizes them via YAML configuration. The debug interface provides real-time endpoint testing with health monitoring."*

---

*Ready to explore? Run `just start` and visit the demo!*