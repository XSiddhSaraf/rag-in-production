"""Azure OpenAI client wrapper with retry logic and prompt templates."""

from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from config import settings
from loguru import logger
import json
import time


class LLMClient:
    """Azure OpenAI client for RAG pipeline."""
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        logger.info(f"Initializing LLM client: endpoint={settings.azure_openai_endpoint}, deployment={settings.azure_openai_deployment_name}")
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            timeout=60.0,
            max_retries=0,  # We handle retries ourselves
        )
        self.deployment_name = settings.azure_openai_deployment_name
        self.max_retries = 3
        self.retry_delay = 2
    
    def _retry_with_exponential_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry logic."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
    
    def analyze_project(
        self,
        technical_doc_text: str,
        eu_context: List[str],
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Analyze project for AI presence and risks."""
        
        context_str = "\n\n".join([f"[Context {i+1}]\n{ctx}" for i, ctx in enumerate(eu_context)])
        
        prompt = f"""You are an AI compliance expert analyzing technical documents against the EU AI Act.

**EU AI Act Context:**
{context_str}

**Technical Document to Analyze:**
{technical_doc_text[:8000]}

**Task:**
Analyze the technical document and provide a structured JSON response with the following:

1. **project_name**: Extract or infer the project name
2. **description**: A brief 2-3 sentence description of the project
3. **contains_ai**: Boolean indicating if the project contains AI/ML components
4. **ai_confidence**: Confidence score (0.0-1.0) for AI detection
5. **high_risks**: Array of high-risk items based on EU AI Act
6. **low_risks**: Array of low-risk items based on EU AI Act

For each risk, provide:
- description: What the risk is
- category: EU AI Act category (e.g., "Prohibited AI", "High-Risk AI")
- eu_act_reference: Relevant article/section from EU AI Act
- confidence_score: How confident you are (0.0-1.0)

**Output Format (JSON):**
```json
{{
  "project_name": "...",
  "description": "...",
  "contains_ai": true/false,
  "ai_confidence": 0.0-1.0,
  "high_risks": [
    {{
      "description": "...",
      "category": "...",
      "eu_act_reference": "Article X",
      "confidence_score": 0.0-1.0
    }}
  ],
  "low_risks": [...]
}}
```

Respond ONLY with valid JSON, no additional text."""

        logger.info(f"Calling Azure OpenAI for project analysis (deployment={self.deployment_name})...")
        response = self._retry_with_exponential_backoff(
            self.client.chat.completions.create,
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert AI compliance analyst. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens,
        )
        
        content = response.choices[0].message.content
        logger.info(f"LLM Analysis completed. Tokens used: {response.usage.total_tokens}")
        logger.debug(f"Raw LLM response: {content[:500]}")
        
        return self._parse_json(content)
    
    def judge_analysis(
        self,
        technical_doc: str,
        analysis_result: Dict[str, Any],
        eu_context: List[str]
    ) -> Dict[str, Any]:
        """Use LLM as a judge to evaluate the analysis quality."""
        
        context_str = "\n\n".join(eu_context[:3])  # Use top 3 contexts
        
        prompt = f"""You are evaluating the quality of an AI compliance analysis.

**Original Technical Document (excerpt):**
{technical_doc[:4000]}

**EU AI Act Context:**
{context_str}

**Analysis Result to Evaluate:**
{json.dumps(analysis_result, indent=2)}

**Evaluation Criteria:**
1. **Accuracy (0-1)**: Are the identified AI components and risks accurate?
2. **Completeness (0-1)**: Did the analysis cover all relevant aspects?
3. **Consistency (0-1)**: Are the risk classifications consistent with EU AI Act?

Provide scores and reasoning in JSON format:

```json
{{
  "accuracy_score": 0.0-1.0,
  "completeness_score": 0.0-1.0,
  "consistency_score": 0.0-1.0,
  "overall_score": 0.0-1.0,
  "reasoning": "Detailed explanation of scores..."
}}
```

Respond ONLY with valid JSON."""

        logger.info("Calling Azure OpenAI for LLM-as-judge evaluation...")
        response = self._retry_with_exponential_backoff(
            self.client.chat.completions.create,
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert evaluator. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        
        content = response.choices[0].message.content
        logger.info("LLM judge evaluation completed.")
        return self._parse_json(content)
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Strip markdown code fences if present
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])  # Remove first and last line
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}\nContent: {content[:500]}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text."""
        logger.info(f"Getting embedding for text (length={len(text)})...")
        response = self._retry_with_exponential_backoff(
            self.client.embeddings.create,
            model=settings.azure_openai_embedding_deployment,
            input=text[:8000]  # Truncate to avoid token limit
        )
        logger.info("Embedding generated successfully.")
        return response.data[0].embedding


# Global LLM client instance
llm_client = LLMClient()
