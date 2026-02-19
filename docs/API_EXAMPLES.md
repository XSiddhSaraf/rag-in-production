# API Examples

This document provides examples of interacting with the EU AI Act Compliance Analyzer API.

## Base URL

**Local Development**: `http://localhost:8000`  
**Production**: `https://your-backend-url.azurecontainerapps.io`

## Authentication

Currently, the API does not require authentication for local development. For production deployments, consider adding API keys or OAuth.

## Endpoints

### 1. Health Check

Check if the API is running and vector database is ready.

**Request:**
```bash
curl -X GET http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_db_status": "ready",
  "llm_status": "ready"
}
```

### 2. Index EU AI Act

Index the EU_AI_ACT.pdf into the vector database. This should be done once after deployment.

**Request:**
```bash
curl -X POST http://localhost:8000/api/index-eu-act
```

**Response:**
```json
{
  "status": "success",
  "message": "Indexed 245 chunks from EU AI Act",
  "chunks": 245
}
```

**Force Re-index:**
```bash
curl -X POST "http://localhost:8000/api/index-eu-act?force_reindex=true"
```

### 3. Vector Database Statistics

Get statistics about the indexed documents.

**Request:**
```bash
curl -X GET http://localhost:8000/api/vector-stats
```

**Response:**
```json
{
  "collection_name": "eu_ai_act",
  "total_documents": 245,
  "indexed": true
}
```

### 4. Upload Document for Analysis

Upload a technical document (PDF or Word) for compliance analysis.

**Request:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/your/document.pdf"
```

**Response:**
```json
{
  "job_id": "a7b3c4d5-e6f7-8g9h-0i1j-2k3l4m5n6o7p",
  "status": "pending",
  "message": "File uploaded successfully. Analysis started."
}
```

### 5. Get Analysis Results

Poll this endpoint to get the analysis results. Status will change from `pending` → `processing` → `completed`.

**Request:**
```bash
curl -X GET http://localhost:8000/api/analyze/a7b3c4d5-e6f7-8g9h-0i1j-2k3l4m5n6o7p
```

**Response (Processing):**
```json
{
  "job_id": "a7b3c4d5-e6f7-8g9h-0i1j-2k3l4m5n6o7p",
  "status": "processing",
  "created_at": "2026-02-14T14:30:00Z"
}
```

**Response (Completed):**
```json
{
  "job_id": "a7b3c4d5-e6f7-8g9h-0i1j-2k3l4m5n6o7p",
  "status": "completed",
  "created_at": "2026-02-14T14:30:00Z",
  "completed_at": "2026-02-14T14:32:15Z",
  "project_analysis": {
    "project_name": "Facial Recognition Border Control",
    "description": "AI-powered biometric identification system for automated border control using deep learning models.",
    "contains_ai": true,
    "ai_confidence": 0.95,
    "high_risks": [
      {
        "description": "Real-time biometric identification system in public spaces",
        "category": "Prohibited AI Practices",
        "level": "high",
        "eu_act_reference": "Article 5",
        "confidence_score": 0.92
      },
      {
        "description": "Automated decision-making for border control",
        "category": "High-Risk AI Systems",
        "level": "high",
        "eu_act_reference": "Article 6",
        "confidence_score": 0.88
      }
    ],
    "low_risks": [
      {
        "description": "Transparency requirements for AI system operations",
        "category": "Transparency Obligations",
        "level": "low",
        "eu_act_reference": "Article 9",
        "confidence_score": 0.75
      }
    ],
    "metadata": {
      "total_risks": 3,
      "high_risk_count": 2,
      "low_risk_count": 1
    }
  },
  "evaluation_metrics": {
    "faithfulness": 0.87,
    "answer_relevance": 0.92,
    "context_precision": 0.83,
    "context_recall": 0.89,
    "overall_score": 0.88
  },
  "llm_judge_result": {
    "accuracy_score": 0.90,
    "completeness_score": 0.85,
    "consistency_score": 0.88,
    "overall_score": 0.88,
    "reasoning": "The analysis correctly identified the facial recognition system as prohibited AI under Article 5. High-risk classification for border control is accurate per Article 6. Transparency obligations appropriately flagged. Minor improvement: could reference data protection requirements."
  }
}
```

**Response (Failed):**
```json
{
  "job_id": "a7b3c4d5-e6f7-8g9h-0i1j-2k3l4m5n6o7p",
  "status": "failed",
  "created_at": "2026-02-14T14:30:00Z",
  "completed_at": "2026-02-14T14:30:45Z",
  "error_message": "Failed to extract text from PDF: Unsupported encryption"
}
```

### 6. Download Excel Report

Download the generated Excel report for a completed job.

**Request:**
```bash
curl -X GET http://localhost:8000/api/download/a7b3c4d5-e6f7-8g9h-0i1j-2k3l4m5n6o7p \
  -o report.xlsx
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- File download

## Complete Workflow Example

Here's a complete workflow from upload to download:

```bash
#!/bin/bash

# 1. Check API health
echo "Checking API health..."
curl -X GET http://localhost:8000/api/health

# 2. Index EU AI Act (first time only)
echo "Indexing EU AI Act..."
curl -X POST http://localhost:8000/api/index-eu-act

# 3. Upload document
echo "Uploading document..."
RESPONSE=$(curl -X POST http://localhost:8000/api/upload \
  -F "file=@sample_technical_doc.pdf" \
  -s)

# Extract job_id from response
JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# 4. Poll for completion
echo "Waiting for analysis to complete..."
while true; do
  STATUS=$(curl -s http://localhost:8000/api/analyze/$JOB_ID | jq -r '.status')
  echo "Status: $STATUS"
  
  if [ "$STATUS" == "completed" ] || [ "$STATUS" == "failed" ]; then
    break
  fi
  
  sleep 3
done

# 5. Get full results
echo "Fetching results..."
curl -X GET http://localhost:8000/api/analyze/$JOB_ID | jq .

# 6. Download Excel report
echo "Downloading Excel report..."
curl -X GET http://localhost:8000/api/download/$JOB_ID -o "report_${JOB_ID}.xlsx"

echo "Done! Report saved as report_${JOB_ID}.xlsx"
```

## Python Examples

### Using requests library

```python
import requests
import time
import json

BASE_URL = "http://localhost:8000"

# 1. Upload document
with open('sample_technical_doc.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    job_data = response.json()
    job_id = job_data['job_id']
    print(f"Job ID: {job_id}")

# 2. Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/api/analyze/{job_id}")
    result = response.json()
    status = result['status']
    print(f"Status: {status}")
    
    if status in ['completed', 'failed']:
        break
    
    time.sleep(3)

# 3. Get results
if result['status'] == 'completed':
    print("\nProject Analysis:")
    print(json.dumps(result['project_analysis'], indent=2))
    
    print("\nEvaluation Metrics:")
    print(json.dumps(result['evaluation_metrics'], indent=2))
    
    # 4. Download Excel
    response = requests.get(f"{BASE_URL}/api/download/{job_id}")
    with open(f'report_{job_id}.xlsx', 'wb') as f:
        f.write(response.content)
    print(f"\nReport saved: report_{job_id}.xlsx")
else:
    print(f"Analysis failed: {result.get('error_message')}")
```

## JavaScript/TypeScript Example

```typescript
const BASE_URL = 'http://localhost:8000';

async function analyzeDocument(filePath: string) {
  // 1. Upload document
  const formData = new FormData();
  formData.append('file', filePath);
  
  const uploadResponse = await fetch(`${BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  
  const { job_id } = await uploadResponse.json();
  console.log(`Job ID: ${job_id}`);
  
  // 2. Poll for completion
  let result;
  while (true) {
    const response = await fetch(`${BASE_URL}/api/analyze/${job_id}`);
    result = await response.json();
    console.log(`Status: ${result.status}`);
    
    if (result.status === 'completed' || result.status === 'failed') {
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 3000));
  }
  
  // 3. Return results
  return result;
}
```

## Error Handling

### Common Error Responses

**400 Bad Request - Invalid File Type:**
```json
{
  "detail": "Invalid file type. Allowed: pdf, docx, doc"
}
```

**400 Bad Request - File Too Large:**
```json
{
  "detail": "File too large. Max size: 50MB"
}
```

**404 Not Found - Job Not Found:**
```json
{
  "detail": "Job not found"
}
```

**400 Bad Request - Job Not Completed:**
```json
{
  "detail": "Job not completed. Current status: processing"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error message"
}
```

## Rate Limiting

Currently, there is no rate limiting implemented. For production deployments, consider:

- Adding rate limiting middleware
- Implementing request quotas
- Using Azure API Management

## Best Practices

1. **Polling Interval**: Wait at least 3 seconds between status checks
2. **File Validation**: Validate file type and size client-side before upload
3. **Error Handling**: Always check response status and handle errors gracefully
4. **Timeout**: Set reasonable timeouts for large document processing
5. **Job Cleanup**: Consider implementing job expiration (e.g., delete results after 24 hours)

## Postman Collection

Import this collection into Postman for easy testing:

```json
{
  "info": {
    "name": "EU AI Act Compliance Analyzer",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/api/health"
      }
    },
    {
      "name": "Index EU AI Act",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/index-eu-act"
      }
    },
    {
      "name": "Upload Document",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/upload",
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "/path/to/document.pdf"
            }
          ]
        }
      }
    },
    {
      "name": "Get Analysis",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/api/analyze/{{jobId}}"
      }
    },
    {
      "name": "Download Excel",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/api/download/{{jobId}}"
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000"
    },
    {
      "key": "jobId",
      "value": ""
    }
  ]
}
```

Save this as `postman_collection.json` and import into Postman.
