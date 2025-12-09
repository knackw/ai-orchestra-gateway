# API Usage Examples

## New Endpoints - AI-006 & GDPR-001/002/003

This document provides usage examples for the newly implemented API endpoints.

---

## 1. Vision API - Image Analysis

### Endpoint
```
POST /api/v1/vision
```

### Headers
```
X-License-Key: your-license-key-here
Content-Type: application/json
```

### Request Body
```json
{
  "prompt": "What is in this image? Describe it in detail.",
  "image_url": "https://example.com/image.jpg",
  "provider": "scaleway",
  "model": "pixtral-12b-2409",
  "eu_only": true
}
```

### Response
```json
{
  "content": "This image shows a beautiful sunset over the ocean with orange and pink hues in the sky...",
  "tokens_used": 234,
  "credits_deducted": 234,
  "pii_detected": false,
  "provider_used": "scaleway",
  "model_used": "pixtral-12b-2409",
  "eu_compliant": true,
  "fallback_applied": false
}
```

### Available Vision Models
- `pixtral-12b-2409` - Mistral's vision model (128k context)
- `mistral-small-3.2-24b-instruct-2506` - Multimodal (128k context)
- `gemma-3-27b-it` - Google Gemma 3 multimodal (40k context)
- `holo2-30b-a3b` - Advanced multimodal (22k context)

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/vision" \
  -H "X-License-Key: your-license-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Describe this image",
    "image_url": "https://example.com/image.jpg",
    "provider": "scaleway"
  }'
```

---

## 2. Audio Transcription API

### Endpoint
```
POST /api/v1/audio/transcriptions
```

### Headers
```
X-License-Key: your-license-key-here
Content-Type: multipart/form-data
```

### Form Data
```
file: audio.wav (binary)
model: whisper-large-v3 (optional)
provider: scaleway (optional, default)
eu_only: false (optional)
```

### Response
```json
{
  "text": "Hello, this is a test transcription of the audio file.",
  "tokens_used": 45,
  "credits_deducted": 55,
  "provider_used": "scaleway",
  "model_used": "whisper-large-v3",
  "eu_compliant": true
}
```

### Available Transcription Models
- `whisper-large-v3` - OpenAI Whisper (30s chunks, 25MB max)
- `voxtral-small-24b-2507` - Mistral's audio model (30min max, 30s chunks, 25MB max)

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/audio/transcriptions" \
  -H "X-License-Key: your-license-key" \
  -F "file=@audio.wav" \
  -F "model=whisper-large-v3" \
  -F "provider=scaleway"
```

### Python Example
```python
import requests

with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/audio/transcriptions",
        headers={"X-License-Key": "your-license-key"},
        files={"file": f},
        data={
            "model": "whisper-large-v3",
            "provider": "scaleway",
            "eu_only": "true"
        }
    )
print(response.json()["text"])
```

---

## 3. Embeddings API

### Endpoint
```
POST /api/v1/embeddings
```

### Headers
```
X-License-Key: your-license-key-here
Content-Type: application/json
```

### Request Body
```json
{
  "input": [
    "Machine learning is a subset of artificial intelligence.",
    "Natural language processing enables computers to understand text."
  ],
  "model": "qwen3-embedding-8b",
  "provider": "scaleway",
  "eu_only": true
}
```

### Response
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, -0.456, 0.789, ...],
      "index": 0
    },
    {
      "object": "embedding",
      "embedding": [0.234, -0.567, 0.890, ...],
      "index": 1
    }
  ],
  "model": "qwen3-embedding-8b",
  "credits_deducted": 10,
  "provider_used": "scaleway",
  "eu_compliant": true
}
```

### Available Embedding Models
- `qwen3-embedding-8b` - Alibaba's embedding (32k context, 32-4096 dimensions)
- `bge-multilingual-gemma2` - BAAI multilingual (8k context, 3584 dimensions fixed)

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/embeddings" \
  -H "X-License-Key: your-license-key" \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["Hello world", "Test text"],
    "model": "qwen3-embedding-8b"
  }'
```

### Python Example
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/embeddings",
    headers={"X-License-Key": "your-license-key"},
    json={
        "input": ["Text to embed 1", "Text to embed 2"],
        "model": "qwen3-embedding-8b",
        "provider": "scaleway"
    }
)

embeddings = [item["embedding"] for item in response.json()["data"]]
print(f"Generated {len(embeddings)} embeddings")
```

---

## 4. Model Selection in Generate API

### Enhanced Generate Endpoint
```
POST /api/v1/generate
```

### Request with Model Selection
```json
{
  "prompt": "Explain quantum computing in simple terms.",
  "provider": "scaleway",
  "model": "qwen3-235b-a22b-instruct-2507",
  "eu_only": true
}
```

### Available Scaleway Chat Models
- `llama-3.1-8b-instruct` - Efficient 8B model (128k context)
- `llama-3.3-70b-instruct` - Large 70B model (100k context)
- `mistral-small-3.2-24b-instruct-2506` - Recommended (128k context)
- `qwen3-235b-a22b-instruct-2507` - Massive 235B model (250k context!)
- `qwen3-coder-30b-a3b-instruct` - Coding specialist (128k context)
- `deepseek-r1-distill-llama-70b` - Reasoning model (32k context)
- `gpt-oss-120b` - Large GPT-style model (128k context)
- `mistral-nemo-instruct-2407` - Mistral Nemo (128k context)

---

## 5. GDPR Compliance API

### 5.1 Get DPA Information

#### Endpoint
```
GET /api/v1/gdpr/dpa
```

#### Headers
```
X-License-Key: your-license-key-here
```

#### Response
```json
{
  "tenant_id": "tenant-123",
  "dpa_accepted": false,
  "dpa_accepted_at": null,
  "dpa_version": "1.0",
  "eu_only_enabled": false,
  "processor_info": {
    "available_processors": [
      {
        "name": "Scaleway SAS",
        "location": "France (Paris)",
        "gdpr_compliant": true,
        "certifications": ["ISO 27001"]
      }
    ]
  },
  "data_residency_options": [
    {"value": "eu_only", "label": "EU Only (GDPR Compliant)"},
    {"value": "global", "label": "Global (All Providers)"}
  ]
}
```

### 5.2 Accept DPA

#### Endpoint
```
POST /api/v1/gdpr/dpa/accept
```

#### Request Body
```json
{
  "accepted": true,
  "version": "1.0"
}
```

#### Response
```json
{
  "success": true,
  "message": "DPA version 1.0 accepted successfully",
  "dpa_accepted_at": "2025-12-08T22:00:00Z"
}
```

### 5.3 Get Processing Information

#### Endpoint
```
GET /api/v1/gdpr/processing-info/{provider}
```

#### Example
```
GET /api/v1/gdpr/processing-info/scaleway
```

#### Response
```json
{
  "provider": "scaleway",
  "region": "fr-par",
  "data_residency": "EU",
  "is_gdpr_compliant": true,
  "legal_basis": "contract",
  "data_retention_days": 0,
  "processor_name": "Scaleway SAS",
  "processor_location": "France (Paris)",
  "sub_processors": ["Scaleway Cloud Infrastructure (FR-PAR)"],
  "security_measures": [
    "TLS 1.3 encryption in transit",
    "AES-256 encryption at rest",
    "ISO 27001 certified",
    "Data stored in France",
    "No data retention policy"
  ],
  "data_subject_rights": [
    "Right to access",
    "Right to deletion",
    "Right to rectification",
    "Right to data portability",
    "Right to object"
  ]
}
```

### 5.4 Get Compliance Status

#### Endpoint
```
GET /api/v1/gdpr/compliance-status
```

#### Response
```json
{
  "providers": [
    {
      "name": "scaleway",
      "eu_compliant": true,
      "region": "fr-par",
      "data_residency": "EU",
      "processor_location": "France (Paris)"
    },
    {
      "name": "anthropic",
      "eu_compliant": false,
      "region": "us-east-1",
      "data_residency": "US",
      "processor_location": "United States"
    }
  ],
  "eu_compliant_providers": ["scaleway", "vertex_claude", "vertex_gemini"],
  "recommended_provider": "vertex_claude"
}
```

---

## EU-Only Mode Examples

### Automatic Fallback

When `eu_only: true` is set and a non-EU provider is requested, the system automatically falls back to an EU-compliant provider:

#### Request (Non-EU Provider)
```json
{
  "prompt": "Translate to German: Hello world",
  "provider": "anthropic",
  "eu_only": true
}
```

#### Response (Automatic Fallback)
```json
{
  "content": "Hallo Welt",
  "tokens_used": 25,
  "credits_deducted": 25,
  "pii_detected": false,
  "provider_used": "vertex_claude",
  "eu_compliant": true,
  "fallback_applied": true
}
```

---

## Rate Limits

- **Generate**: 100 requests/minute
- **Vision**: 50 requests/minute
- **Audio**: 30 requests/minute
- **Embeddings**: 100 requests/minute
- **GDPR DPA**: 20 requests/minute
- **GDPR Accept**: 5 requests/minute

---

## Error Responses

### Insufficient Credits (402)
```json
{
  "detail": "Insufficient credits. Current balance: 10, required: 50"
}
```

### Invalid License Key (403)
```json
{
  "detail": "Invalid or inactive license key"
}
```

### Rate Limit Exceeded (429)
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

### File Too Large (413)
```json
{
  "detail": "File too large. Maximum size is 25MB, got 30.5MB"
}
```

### Invalid Provider (400)
```json
{
  "detail": "Provider 'invalid' does not support vision. Use one of: scaleway, anthropic"
}
```

---

## Credit Costs

### Vision API
- Cost: 1 credit per token
- Average: 150-300 credits per request

### Audio API
- Base cost: 10 credits
- Additional: 1 credit per token of transcribed text
- Average: 50-100 credits per minute of audio

### Embeddings API
- Cost: 5 credits per text
- Batch discount: Same cost regardless of text length

### Generate API
- Cost: 1 credit per token
- Varies by model and prompt length

---

## Best Practices

1. **Use EU-Only Mode for GDPR Compliance**
   ```json
   {"eu_only": true}
   ```

2. **Select Appropriate Models**
   - Use smaller models for simple tasks to save credits
   - Use larger models (qwen3-235b) for complex reasoning

3. **Batch Embeddings Requests**
   - Send up to 100 texts in one request
   - More efficient than individual requests

4. **Optimize Audio Files**
   - Compress audio to reduce file size
   - Use 30-second chunks for best results

5. **Cache Embeddings**
   - Store embeddings for reuse
   - Reduces API calls and costs

6. **Monitor Credits**
   - Check response `credits_deducted` field
   - Track usage via analytics API

---

## Python SDK Example

```python
import requests

class AIGatewayClient:
    def __init__(self, license_key: str, base_url: str = "http://localhost:8000"):
        self.license_key = license_key
        self.base_url = base_url
        self.headers = {
            "X-License-Key": license_key,
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, provider: str = "scaleway", model: str = None, eu_only: bool = True):
        """Generate text response."""
        response = requests.post(
            f"{self.base_url}/api/v1/generate",
            headers=self.headers,
            json={
                "prompt": prompt,
                "provider": provider,
                "model": model,
                "eu_only": eu_only
            }
        )
        return response.json()

    def analyze_image(self, prompt: str, image_url: str, model: str = "pixtral-12b-2409"):
        """Analyze image with vision model."""
        response = requests.post(
            f"{self.base_url}/api/v1/vision",
            headers=self.headers,
            json={
                "prompt": prompt,
                "image_url": image_url,
                "provider": "scaleway",
                "model": model,
                "eu_only": True
            }
        )
        return response.json()

    def transcribe_audio(self, audio_file_path: str):
        """Transcribe audio file."""
        with open(audio_file_path, "rb") as f:
            response = requests.post(
                f"{self.base_url}/api/v1/audio/transcriptions",
                headers={"X-License-Key": self.license_key},
                files={"file": f},
                data={"provider": "scaleway", "eu_only": "true"}
            )
        return response.json()

    def create_embeddings(self, texts: list[str]):
        """Generate embeddings for texts."""
        response = requests.post(
            f"{self.base_url}/api/v1/embeddings",
            headers=self.headers,
            json={
                "input": texts,
                "provider": "scaleway",
                "eu_only": True
            }
        )
        return response.json()

    def get_dpa_status(self):
        """Get DPA acceptance status."""
        response = requests.get(
            f"{self.base_url}/api/v1/gdpr/dpa",
            headers=self.headers
        )
        return response.json()

    def accept_dpa(self):
        """Accept Data Processing Agreement."""
        response = requests.post(
            f"{self.base_url}/api/v1/gdpr/dpa/accept",
            headers=self.headers,
            json={"accepted": True, "version": "1.0"}
        )
        return response.json()


# Usage
client = AIGatewayClient(license_key="your-license-key")

# Generate text
result = client.generate("Explain AI in simple terms")
print(result["content"])

# Analyze image
result = client.analyze_image("What's in this image?", "https://example.com/image.jpg")
print(result["content"])

# Transcribe audio
result = client.transcribe_audio("audio.wav")
print(result["text"])

# Generate embeddings
result = client.create_embeddings(["Hello world", "Test text"])
print(f"Generated {len(result['data'])} embeddings")

# Check DPA status
dpa = client.get_dpa_status()
if not dpa["dpa_accepted"]:
    client.accept_dpa()
```

---

## Testing

Use the OpenAPI documentation to test endpoints:
- Development: http://localhost:8000/docs
- Provides interactive API testing
- Shows request/response schemas
- Includes examples for all endpoints

---

## Support

For issues or questions:
1. Check API documentation: `/docs`
2. Review error responses for details
3. Contact support with request ID (from response headers)
