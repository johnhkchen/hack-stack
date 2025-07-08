# Hack-Stack 
> Write Code, Not Config

**Stack**: Astro + Svelte + FastAPI + LlamaIndex RAG + Docker

## 30-Second Startup

```bash
git clone https://github.com/johnhkchen/hack-stack.git
cd hack-stack
just up
```

**That's it.**

## What You Get:

```
hack-stack/
├── frontend/   
│   └── src/
│       ├── components/   <- 🎨 ADD YOUR UI COMPONENTS HERE
│       │   └── BusinessCard.svelte   <- Try editing me first!
│       └── pages/        <- 📱 YOUR MAIN PAGES GO HERE
│           └── index.astro
├── backend/
│   └── api/
│       └── routes.py     <- 🔧 ADD YOUR API ENDPOINTS HERE
└── data/                 <- 📊 YOUR DATA GOES HERE
```

# Today's Hackathon: 
## Weaviate + LlamaIndex Hacknight at Github

```
hack-stack/
├── frontend/src/
│   ├── components/
│   │   ├── AstroComponent.astro 
│   │   └── SvelteComponent.svelte     <- add your components here
│   └── pages/
│       └── index.astro             <- Start Here - just change the title, ez dopamine!
├── backend/
│   ├── api/
│   │   └── routes.py              <- Main API endpoints
│   └── data/
│       └── yourdata.json           <- store data for the backend

```

## Quick Commands

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

## **Frontend Stack**
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

## **Backend Stack**
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
