# 🤖 GPT Prompt Engineering Analysis

## 📋 **Complete Prompt Flow**

### **1. URL Discovery Prompt** (`prompts/url_search.txt`)

```
Return ONLY valid JSON in the form {"urls": [ ... ]}.

TASK:
Given a topic, return {COUNT} relevant URLs for system design HLD/LLD.

RULES:
1. Output ONLY JSON.
2. Return exactly {COUNT} URLs.
3. Prefer reputable engineering/system design write-ups.
4. URLs must be fully qualified (https://...).

TOPIC:
{TOPIC}
```

**Example Input:** "Netflix Streaming Architecture"
**Example Output:**
```json
{
  "urls": [
    "https://netflixtechblog.com/netflix-system-architecture-overview",
    "https://medium.com/@system-design/netflix-streaming-system",
    "https://engineering.netflix.com/microservices-architecture",
    "https://aws.amazon.com/solutions/case-studies/netflix/",
    "https://blog.pragmaticengineer.com/netflix-system-design/"
  ]
}
```

---

### **2. Components Extraction Prompt** (`prompts/components_extraction.txt`)

```
You are a system design analysis engine.

Your task is to extract HIGH-LEVEL DESIGN (HLD) components and their relationships from the given text.

STRICT RULES:
1. Output ONLY valid JSON.
2. Do NOT include explanations, markdown, or extra text.
3. Do NOT include testing, interview prep, analytics dashboards, or UI menus.
4. Focus ONLY on HLD-level components (clients, services, gateways, databases, caches, queues, infra).
5. Normalize component names (Title Case).
6. Infer obvious missing components and relationships if required for system completeness.
7. Do NOT invent technologies not implied by the text.

OUTPUT JSON SCHEMA:
{
  "components": [
    {
      "id": "<snake_case_id>",
      "name": "<Human Readable Name>",
      "type": "<client|gateway|service|core_service|database|cache|queue|streaming|external_service|edge|infra>"
    }
  ],
  "relationships": [
    {
      "source": "<source_component_id>",
      "target": "<target_component_id>",
      "label": "<relationship_description>"
    }
  ]
}

TEXT TO ANALYZE:
<<<
{CLEANED_TEXT}
>>>
```

---

## 🔧 **Technical Implementation**

### **LLM Provider Integration** (`services/llm_provider.py`)

**Supports Multiple AI Providers:**
- ✅ **Google Gemini** (Primary)
- ✅ **OpenRouter** (Fallback)

**Key Features:**
- **JSON Validation**: `ensure_json()` extracts valid JSON from AI responses
- **Error Handling**: Robust timeout and error management
- **Flexible Models**: Configurable model selection

### **Prompt Processing** (`services/llm.py`)

```python
def extract_components_from_text(cleaned_text: str) -> dict:
    # Load prompt template
    prompt_path = root_dir / "prompts" / "components_extraction.txt"
    prompt_template = prompt_path.read_text(encoding="utf-8")
    
    # Inject cleaned text
    prompt = prompt_template.replace("{CLEANED_TEXT}", cleaned_text)
    
    # Get AI response
    client = get_llm_client()
    raw = client.generate_text(prompt)
    
    # Ensure valid JSON
    payload = ensure_json(raw)
    return json.loads(payload)
```

---

## 🎯 **Prompt Engineering Strategy**

### **1. Strict JSON Output**
- **No explanations** - Forces pure JSON response
- **Schema enforcement** - Exact structure required
- **Validation** - `ensure_json()` extracts JSON from any response

### **2. Component Type Classification**
**Supported Types:**
- `client` → Users, Mobile App, Web App
- `gateway` → API Gateway, Load Balancer, CDN
- `service` → Microservices, Business Logic
- `core_service` → Critical system services
- `database` → PostgreSQL, MongoDB, etc.
- `cache` → Redis, Memcached
- `queue` → Kafka, RabbitMQ
- `streaming` → Event streaming systems
- `external_service` → Third-party APIs
- `edge` → CDN, Edge computing
- `infra` → Kubernetes, Docker, etc.

### **3. Relationship Extraction**
**Smart Labeling:**
- `queries` → Database interactions
- `publishes` → Event publishing
- `caches` → Caching operations
- `API calls` → Service communication
- `fetches` → Data retrieval

### **4. Quality Controls**
- ✅ **No test/interview content** - Filters out irrelevant data
- ✅ **HLD focus only** - Avoids low-level implementation details
- ✅ **Normalized names** - Consistent Title Case formatting
- ✅ **Inferred completeness** - Adds obvious missing components
- ✅ **Technology grounding** - Only uses mentioned technologies

---

## 📊 **Example GPT Response**

**Input Text:** "Netflix uses microservices architecture with API Gateway routing requests to user service for authentication, content service for catalog, and streaming service for video delivery. Redis caches user sessions. Kafka handles events. CDN delivers videos from S3 storage."

**GPT Output:**
```json
{
  "components": [
    {
      "id": "api_gateway",
      "name": "API Gateway", 
      "type": "gateway"
    },
    {
      "id": "user_service",
      "name": "User Service",
      "type": "service"
    },
    {
      "id": "content_service", 
      "name": "Content Service",
      "type": "service"
    },
    {
      "id": "streaming_service",
      "name": "Streaming Service", 
      "type": "service"
    },
    {
      "id": "redis_cache",
      "name": "Redis Cache",
      "type": "cache"
    },
    {
      "id": "kafka_queue",
      "name": "Kafka Queue", 
      "type": "queue"
    },
    {
      "id": "cdn",
      "name": "CDN",
      "type": "edge"
    },
    {
      "id": "s3_storage",
      "name": "S3 Storage",
      "type": "external_service"
    }
  ],
  "relationships": [
    {
      "source": "api_gateway",
      "target": "user_service",
      "label": "routes auth requests"
    },
    {
      "source": "api_gateway", 
      "target": "content_service",
      "label": "routes catalog requests"
    },
    {
      "source": "api_gateway",
      "target": "streaming_service", 
      "label": "routes video requests"
    },
    {
      "source": "user_service",
      "target": "redis_cache",
      "label": "caches sessions"
    },
    {
      "source": "streaming_service",
      "target": "kafka_queue",
      "label": "publishes events"
    },
    {
      "source": "cdn",
      "target": "s3_storage",
      "label": "fetches videos"
    }
  ]
}
```

---

## 🚀 **Conversion to Diagram**

**converter.py** takes this JSON and:

1. **Maps types to icons:**
   - `gateway` → AWS API Gateway icon
   - `service` → Server icon  
   - `cache` → Redis icon
   - `external_service` → S3 icon

2. **Groups into clusters:**
   - **Gateway Layer**: API Gateway
   - **Service Layer**: User, Content, Streaming services
   - **Data Layer**: Redis, Kafka
   - **External Services**: CDN, S3

3. **Creates relationships:**
   - Curved arrows with labels
   - Professional styling

4. **Generates PNG:**
   - High-quality diagram
   - Enterprise-ready output

---

## 💡 **Why This Works**

### **Prompt Engineering Excellence:**
- ✅ **Strict constraints** prevent hallucination
- ✅ **Clear schema** ensures consistent output  
- ✅ **Type system** enables smart icon mapping
- ✅ **Relationship labels** create meaningful connections
- ✅ **JSON-only output** enables reliable parsing

### **AI Provider Flexibility:**
- ✅ **Multi-provider support** (Gemini + OpenRouter)
- ✅ **Robust error handling** 
- ✅ **JSON extraction** from any response format
- ✅ **Configurable models** for different use cases

**This prompt engineering system is the secret sauce that makes your AI-powered diagram generation so reliable and professional!** 🎯