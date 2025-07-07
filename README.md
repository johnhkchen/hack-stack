# 🚀 Hack Stack
> Portfolio-worthy hackathon demo with modern AI integration patterns

**Architecture**: Astro + Svelte + FastAPI + Docker + 5 Sponsor Technologies

## ⚡ 30-Second Startup

```bash
git clone <repo>
cd hack-stack
just start
```

**That's it.** Working demo with compelling data, beautiful UI, and AI integration.

## 🎯 Project Vision

This is **not just a hackathon project**. It's:

- 🎨 **Portfolio piece** - Demonstrates full-stack + AI capabilities
- 🏗️ **Architecture showcase** - Modern patterns that impress in interviews  
- 🛠️ **Development template** - Foundation for future rapid prototyping
- 💬 **Conversation starter** - Technical depth that launches careers

## 🏗️ Architecture Highlights

### **Microservices with Containerization**
```
┌─────────────────┐    ┌─────────────────┐
│  Astro + Svelte │────│   FastAPI       │
│  (Frontend)     │    │   (Backend)     │
│  Port 4321      │    │   Port 8000     │
└─────────────────┘    └─────────────────┘
          │                      │
    ┌─────┴──────┐        ┌──────┴──────┐
    │   Nginx    │        │  AI Vendors │
    │ (Prod only)│        │ (Protocols) │
    │  Port 80   │        └─────────────┘
    └────────────┘
```

### **Progressive Enhancement Strategy**
- **Layer 1**: Works with zero configuration (compelling mock data)
- **Layer 2**: Upgrades automatically when API keys detected
- **Layer 3**: Production monitoring and health checks

### **Protocol-Based Vendor Integration**
```python
class VendorProtocol(Protocol):
    async def process(self, operation: str, data: Dict) -> Dict: ...

# Enables seamless sponsor swapping
vendor = get_vendor("openai") or MockVendor()
result = await vendor.process("analyze", business_data)
```

## 🎪 Sponsor Technology Integration

### **1. OpenAI** - Business Analysis
- **Demo**: Analyze business sentiment and growth potential
- **Integration**: Real API calls with structured responses
- **Fallback**: Realistic mock analysis results

### **2. Anthropic** - Structured Data Extraction  
- **Demo**: Extract business categories and impact metrics
- **Integration**: Claude API for data structuring
- **Fallback**: Pre-generated structured business data

### **3. Weaviate** - Similarity Search
- **Demo**: "Find businesses like this one" semantic matching
- **Integration**: Vector database for business discovery
- **Fallback**: Mock similarity scoring algorithm

### **4. LlamaIndex** *(Integration Ready)*
- **Demo**: Document processing and business profile generation
- **Integration**: PDF processing pipeline
- **Fallback**: Rich mock business profiles

### **5. Additional Sponsor** *(Configurable)*
- **Demo**: Extensible vendor registry pattern
- **Integration**: Drop-in protocol implementation
- **Fallback**: Generic mock response system

## 🚀 Quick Commands

```bash
# Development (hot reload)
just dev              # Start both frontend + backend
just frontend         # Astro dev server only  
just backend          # FastAPI dev server only

# Demo Preparation
just demo             # Start + open browser
just check            # Health check all services
just build            # Production build

# Container Deployment  
docker compose up     # Full stack with networking
```

## 📊 Environment Detection

**Smart Mode Selection:**
- **Mock Mode**: No API keys → Instant demo with compelling data
- **Hybrid Mode**: Some API keys → Mix of real + mock responses  
- **Live Mode**: All API keys → Full sponsor integration

**Visual Indicators:**
- 🟢 Real vendor responses
- 🟡 Mock vendor responses  
- 🔴 Connection errors (graceful fallback)

## 🏢 Demo Business Data

**Compelling Stories That Resonate:**
- **Quantum Coffee Co.** - Physics meets caffeine (tech audience appeal)
- **Vinyl Rebellion Records** - Analog souls in digital world (nostalgia factor)
- **Midnight Ramen Lab** - Data science ramen perfection (hackathon theme)
- **Binary Bookshop** - Literature for digital age (intellectual appeal)

## 🎯 Technical Interview Talking Points

### **Frontend Architecture**
- "Server-side rendered with hydrated islands for performance"
- "Component-based architecture with clear separation of concerns"
- "Modern build tooling with hot reload and optimized production builds"

### **Backend Design**
- "Protocol-based vendor abstraction for easy sponsor integration"
- "Graceful degradation with automatic mock fallback"
- "Modern Python with uv for deterministic dependency management"

### **DevOps Patterns**
- "Containerized microservices with health checks"
- "Environment-based configuration with smart detection"
- "Single command deployment from development to production"

### **AI Integration**
- "Vendor-agnostic AI service layer with consistent interfaces"
- "Progressive enhancement from mock to live AI responses"
- "Error handling and rate limiting for production reliability"

## 🚨 Demo Day Resilience

**Built for Murphy's Law:**
- ✅ Works offline (no wifi required for basic demo)
- ✅ Works with missing API keys (automatic mock mode)
- ✅ Works on any laptop (Docker containers)
- ✅ Works under pressure (30-second startup)
- ✅ Works for team members (clear documentation)

## 📁 Project Structure

```
hack-stack/
├── frontend/                 # Astro + Svelte
│   ├── src/
│   │   ├── components/      # Reusable Svelte components
│   │   ├── pages/          # Astro page routes  
│   │   └── layouts/        # Shared page layouts
│   └── package.json        # Modern Node.js deps
├── backend/                  # FastAPI + uv
│   ├── api/
│   │   ├── routes.py       # HTTP endpoints
│   │   └── services.py     # Business logic
│   └── pyproject.toml      # Python dependencies
├── docker-compose.yml       # Multi-service orchestration
├── justfile                 # Development commands
└── README.md               # This file
```

## 🎬 4-Hour Implementation Timeline

**Hour 1: Foundation**
- ✅ Service architecture with Docker
- ✅ Health checks and networking
- ✅ Basic UI with mock data

**Hour 2: Sponsor Integration** 
- ✅ Vendor protocol implementation
- ✅ Mock/live mode switching
- ✅ AI analysis features

**Hour 3: Polish**
- ✅ Error handling and loading states
- ✅ Visual status indicators
- ✅ Responsive design

**Hour 4: Demo Prep**
- 🎯 Demo script and talking points
- 🎯 Sponsor-specific showcases
- 🎯 Deployment verification

## 💼 Portfolio Value

**This project demonstrates:**
- Full-stack development with modern tools
- Microservices architecture and containerization
- AI/ML integration patterns and error handling
- Protocol-driven design for extensibility
- Production deployment and monitoring
- Team collaboration and documentation

**Interview conversation starters:**
- "I built a hackathon platform that integrates 5 AI vendors..."
- "The architecture uses protocol-based abstraction to..."
- "We achieved 30-second deployment through..."
- "The progressive enhancement strategy means..."

---

*Built for hackathons where time matters, demos must work, and careers are launched.*