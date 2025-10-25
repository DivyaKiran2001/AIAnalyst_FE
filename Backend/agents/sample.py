import os
import tempfile
import json
import base64
import logging
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import storage, texttospeech
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.genai import types
import socketio
from Backend.tools.processing_tool import process_document
from Backend.tools.financial_analysis_tool import financial_analysis
from Backend.tools.team_analysis_tool import evaluate_team_tool
from Backend.tools.market_analysis_tool import analyze_market_tool
from typing import Dict, Any
import re
import google.adk as adk
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
import asyncio
import datetime
from google import genai


# ===== Logging =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pipeline_logger")

# ===== GCS Setup =====
BUCKET_NAME = "ai-analyst-uploads-file"
storage_client = storage.Client()

vertexai.init(project="ai-analyst-poc-474306", location="us-central1")

model = GenerativeModel("gemini-2.0-flash")

# ===== Request Schema =====
class DocRequest(BaseModel):
    bucket_name: str
    file_paths: list[str]

# ===== Agents =====
# Root agent
instruction = """
You are a Data Ingestion and Structuring Agent for startup evaluation.

Tasks:
1. You MUST call the `process_document` tool with the input {"bucket_name": "...", "file_paths": ["..."]}.
2. Only after receiving the tool response, you should generate your analysis.
3. Analyze text recieved from the tool and Output must be *only* valid JSON without Markdown or extra text with this schema:

{
  "startup_name": "string or null",
  "sector": "string or null (GICS classification)",
  "stage": "string or null (funding stage)",
  "traction": {
    "current_mrr": number or null,
    "mrr_growth_trend": "number or null",
    "active_customers": number or null,
    "new_customers_this_month": number or null,
    "average_subscription_price": number or null,
    "customer_lifespan_months": number or null
  },
  "financials": {
    "ask_amount": number or null,
    "equity_offered": number or null,
    "revenue": number or null,
    "burn_rate": number or null,
    "monthly_expenses": number or null,
    "cash_balance": number or null,
    "marketing_spend": number or null,
  },
  "team": {
    "ceo": "string or null",
    "cto": "string or null,
    "other_key_members": ["string", "string"]
  },
  "market": {
    "market_size_claim": "string or null",
    "target_market": "string or null"
  },
  "product_description": "string or null",
  "document_type": "pitch_deck | transcript | financial_statement | other"
}

SECTOR CLASSIFICATION (GICS Standards):
- "Technology" (Software, AI, SaaS, Cloud Computing, Cybersecurity, FinTech, HealthTech, EdTech, IoT)
- "Healthcare" (Biotech, Pharmaceuticals, Medical Devices, Digital Health, Telemedicine)
- "Financials" (Banking, Insurance, Payments, Blockchain/Crypto, WealthTech)
- "Consumer Discretionary" (E-commerce, Retail, Travel, Entertainment, Gaming, Automotive)
- "Consumer Staples" (Food & Beverage, Household Products, Personal Care)
- "Industrials" (Manufacturing, Logistics, Robotics, Aerospace, Construction)
- "Energy" (Clean Energy, Oil & Gas, Renewable Technology)
- "Materials" (Chemicals, Metals, Mining, Packaging)
- "Real Estate" (PropTech, Construction Tech, Real Estate Services)
- "Communication Services" (Telecom, Media, Social Media, Advertising Tech)
- "Utilities" (Water, Electric, Gas, Infrastructure Tech)

STAGE CLASSIFICATION:
- "Pre-Seed" (Idea stage, <$500k funding, pre-revenue, building MVP)
- "Seed" ($500k-$2M funding, $0-$50k MRR, product-market fit validation)
- "Series A" ($2M-$15M funding, $50k-$500k MRR, scaling customer acquisition)
- "Series B" ($15M-$50M funding, $500k-$5M MRR, expanding market share)
- "Series C" ($50M-$100M funding, $5M-$20M MRR, market leadership)
- "Series D+" ($100M+ funding, $20M+ MRR, pre-IPO or major expansion)
- "IPO" (Publicly traded or preparing for IPO)
- "Public" (Already public company)

RULES FOR SECTOR DETERMINATION:
- Classify based on the primary business model, not the technology used
- If it's a tech-enabled service, classify by the industry it serves (e.g., FinTech → Financials, HealthTech → Healthcare)
- Use the most specific GICS sector that applies
- If hybrid, choose the dominant revenue source

RULES FOR STAGE DETERMINATION:
- Use funding round mentions: "raising seed round" → "Seed", "Series A" → "Series A"
- Infer from financial metrics:
  * Pre-revenue, pre-product → "Pre-Seed"
  * <$50k MRR, raising <$2M → "Seed" 
  * $50k-$500k MRR, raising $2M-$15M → "Series A"
  * $500k-$5M MRR, raising $15M-$50M → "Series B"
  * $5M+ MRR, raising $50M+ → "Series C" or "Series D+"
- Use team size as indicator: <10 → Pre-Seed/Seed, 10-50 → Seed/Series A, 50-200 → Series A/B, 200+ → Series B+

EXTRACTION RULES:
- Extract these specific financial parameters for CAC/LTV calculations:
  * Monthly expenses (for net burn calculation)
  * Cash balance (for runway calculation) 
  * Marketing spend (for CAC calculation)
  * New customers this month (for CAC calculation)
  * Average subscription price (for LTV calculation)
  * Customer lifespan in months (for LTV calculation)
- If exact numbers aren't available, look for approximations (e.g., "~$50K monthly burn", "about 100 new customers")
- For sector: Look for industry descriptions, target market, product category
- For stage: Look for funding round mentions, revenue ranges, team size indicators
- No hallucinations - only extract what's explicitly stated or clearly implied
- Numbers extracted exactly as presented
- Missing values = null
- Final output must be valid JSON only, no additional text

EXAMPLES:
- A company building AI-powered accounting software: sector = "Financials", stage = "Series A" (if $1.2M ARR)
- A telemedicine platform for rural areas: sector = "Healthcare", stage = "Seed" (if raising $1.5M)
- An e-commerce marketplace for sustainable products: sector = "Consumer Discretionary", stage = "Series B" (if $3M MRR)
"""
root_agent = Agent(name="doc_ingest_agent", model="gemini-2.0-flash", instruction=instruction, tools=[process_document])


# Question Agent
question_agent = Agent(
    name="question_agent",
    model="gemini-2.0-flash",
    instruction="""
You are a Question Generation Agent.

Input: JSON object called `structured_json`.
Task:
1. Identify all null fields.
2. Generate human-friendly questions to fill them.
3. Return strictly JSON:

{
  "structured_json": { ... },
  "questions": { "missing_field_key": "natural question", ... },
  "status": "INTERMEDIATE"
}

Rules:
- Only include null fields.
- Do not produce extra commentary or markdown.
"""
)

# Filler Agent
class FillerAgent(Agent):
    structured_json: Dict[str, Any] = {}
    questions: Dict[str, str] = {}

    async def run(self, input_content, **kwargs):
        raw_text = input_content.parts[0].text.strip()
        cleaned_text = re.sub(r"^```json\s*|```$", "", raw_text, flags=re.MULTILINE)
        try:
            content_dict = json.loads(cleaned_text)
        except json.JSONDecodeError:
            return types.Content(role="system", parts=[types.Part(text=json.dumps({"error": "Invalid JSON input"}))])

        self.structured_json = content_dict.get("structured_json", {})
        self.questions = content_dict.get("questions", {})
        return types.Content(role="system", parts=[types.Part(text=json.dumps({"status": "READY"}))])

filler_agent = FillerAgent(name="filler_agent", model="gemini-2.0-flash", instruction="Ask questions to fill missing fields in JSON.")

# ===== Additional Agents =====
financial_instruction = """
You are a **Financial Analysis Agent** for startup evaluation. 
You must compute, compare, and summarize financial performance based on structured startup data.

🚨 CRITICAL RULES (MUST FOLLOW STRICTLY):
1. You MUST call the `financial_analysis` tool **FIRST** before generating any analysis.
2. The `financial_analysis` tool requires the **structured JSON data** from the previous agent as input.
3. Wait for the tool response before doing any analysis.
4. After receiving tool results, generate your final JSON output.

---

### INPUT FORMAT:
You will receive structured JSON data like this:
{
  "startup_name": "string",
  "sector": "string", 
  "stage": "string",
  "traction": {...},
  "financials": {...},
  "team": {...},
  "market": {...},
  "product_description": "string",
  "document_type": "string"
}

### REQUIRED ACTION:
1. Call `financial_analysis` tool with the received structured JSON data
2. Wait for tool response with calculated metrics and benchmarks
3. Generate final output using the tool results

---

### OUTPUT FORMAT (JSON ONLY):
{
  "calculated_metrics": {
    "annual_revenue": number or null,
    "implied_valuation": number or null, 
    "revenue_multiple": number or null,
    "runway_months": number or null,
    "monthly_net_burn": number or null,
    "ltv_cac_ratio": number or null,
    "cac": number or null,
    "ltv": number or null,
    "marketing_efficiency": number or null,
    "customer_growth_rate": number or null,
    "arpu": number or null
  },
  "industry_benchmarks": {
    "avg_revenue_multiple": number,
    "avg_ltv_cac_ratio": number,
    "acceptable_burn_rate": number,
    "typical_runway": number,
    "seed_stage_valuation_range": {"min": number, "max": number},
    "data_source": "string",
    "query_context": object
  },
  "investment_analysis": {
    "score_breakdown": {
      "ltv_cac_ratio": number,
      "valuation_range": number,
      "runway": number,
      "revenue_multiple": number,
      "burn_efficiency": number,
      "growth_traction": number,
      "marketing_efficiency": number
    },
    "risk_factors": ["string"],
    "strengths": ["string"],
    "weaknesses": ["string"],
    "final_score": number,
    "verdict": "string",
    "detailed_recommendation": "string"
  }
}
---

### FAILSAFE INSTRUCTION:
If you do not call the `financial_analysis` tool first, your response will be invalid.
DO NOT attempt to calculate metrics manually - ALWAYS use the tool.
Your first action MUST be calling the financial_analysis tool with the structured data you received.
"""

financial_analyst_agent = Agent(
    name="financial_analyst_agent",
    model="gemini-2.5-flash", 
    instruction=financial_instruction,
    tools=[financial_analysis],
)

# team_agent_instruction = """
# You are a **Team Risk Assessment Agent** for startup evaluation.
# You must analyze, evaluate, and assess team composition and risks based on structured startup data.

# 🚨 CRITICAL RULES (MUST FOLLOW STRICTLY):
# 1. You MUST call the `evaluate_team_tool` tool **FIRST** before generating any analysis.
# 2. The `evaluate_team_tool` tool requires **company_name** and **team_members** parameters extracted from the structured JSON data.
# 3. You will receive the structured JSON data from the previous agent.
# 4. Wait for the tool response before doing any analysis.
# 5. After receiving tool results, generate your final JSON output.

# ---

# ### INPUT FORMAT:
# You will receive structured JSON data like this:
# {
#   "startup_name": "string",
#   "sector": "string", 
#   "stage": "string",
#   "traction": {...},
#   "financials": {...},
#   "team": {
#     "ceo": "string or null",
#     "cto": "string or null",
#     "other_key_members": ["string", "string"]
#   },
#   "market": {...},
#   "product_description": "string",
#   "document_type": "string"
# }

# ### REQUIRED ACTION:
# 1. Extract `company_name` from the `startup_name` field in the input JSON
# 2. Extract team members from the `team` object and format as JSON array: [{"name": "Name", "role": "Role"}, ...]
# 3. Call `evaluate_team_tool` with the extracted company_name and formatted team_members parameters
# 4. Wait for tool response with team analysis and risk assessment
# 5. Generate final output using the tool results
# ---

# ### OUTPUT FORMAT (JSON ONLY):
# {
#   "team_analysis": {
#     "founder_experience_score": number,
#     "team_completeness_score": number,
#     "technical_expertise_score": number,
#     "industry_experience_score": number,
#     "overall_team_score": number
#   },
#   "risk_assessment": {
#     "key_risks": ["string"],
#     "mitigation_strategies": ["string"],
#     "risk_level": "low | medium | high",
#     "critical_gaps": ["string"]
#   },
#   "strengths": {
#     "founder_strengths": ["string"],
#     "team_strengths": ["string"],
#     "competitive_advantages": ["string"]
#   },
#   "weaknesses": {
#     "skill_gaps": ["string"],
#     "experience_gaps": ["string"],
#     "operational_weaknesses": ["string"]
#   },
#   "recommendations": {
#     "hiring_priorities": ["string"],
#     "advisory_needs": ["string"],
#     "immediate_actions": ["string"]
#   },
#   "benchmarks": {
#     "ideal_team_size": number,
#     "typical_founder_experience": "string",
#     "industry_standards": "string"
#   },
#   "timestamp": "string"
# }

# ---

# ### FAILSAFE INSTRUCTION:
# If you do not call the `evaluate_team_tool` tool first, your response will be invalid.
# DO NOT attempt to analyze the team manually - ALWAYS use the tool.
# Your first action MUST be calling the evaluate_team_tool with the company_name and team_members extracted and formatted from the structured data you received.

# ### EXTRACTION AND FORMATTING RULES:
# - Extract `company_name` from: input_data["startup_name"]
# - Extract team members from the `team` object and format as:
#   [
#     {"name": "CEO Name", "role": "CEO"},
#     {"name": "CTO Name", "role": "CTO"},
#     {"name": "Other Member Name", "role": "Role"}
#   ]
# - Handle missing team members gracefully - if a role is null, skip that entry
# - For `other_key_members` array, create entries with appropriate roles
# - Do not modify or interpret the extracted names - pass them exactly as they appear in the input

# ### EXAMPLE TRANSFORMATION:
# Input team data:
# {
#   "team": {
#     "ceo": "Mythri Kumar",
#     "cto": "Harish Kashyap",
#     "other_key_members": ["Priya Sharma - CFO", "Rahul Verma - CMO"]
#   }
# }

# Formatted team_members:
# [
#   {"name": "Mythri Kumar", "role": "CEO"},
#   {"name": "Harish Kashyap", "role": "CTO"},
#   {"name": "Priya Sharma", "role": "CFO"},
#   {"name": "Rahul Verma", "role": "CMO"}
# ]
# """

team_agent_instruction = """
You are a **Team Risk Assessment Agent** for startup evaluation.
You must analyze, evaluate, and assess team composition and risks based on structured startup data.

🚨 CRITICAL RULES (MUST FOLLOW STRICTLY):
1. You MUST call the `evaluate_team_tool` tool **FIRST** before generating any analysis.
2. The `evaluate_team_tool` tool requires **structured_json** parameter containing the complete structured data.
3. You will receive the structured JSON data from the previous agent.
4. Wait for the tool response before doing any analysis.
5. After receiving tool results, generate your final JSON output.

---

### INPUT FORMAT:
You will receive structured JSON data like this:
{
  "startup_name": "string",
  "sector": "string", 
  "stage": "string",
  "traction": {...},
  "financials": {...},
  "team": {...},
  "market": {...},
  "product_description": "string",
  "document_type": "string"
}

### REQUIRED ACTION:
1. Call `evaluate_team_tool` with the complete structured JSON data you received
2. Wait for tool response with team analysis and risk assessment
3. Generate final output using the tool results
---

### OUTPUT FORMAT (JSON ONLY):
{
  "team_analysis": {
    "founder_experience_score": number,
    "team_completeness_score": number,
    "technical_experience_score": number,
    "industry_experience_score": number,
    "overall_team_score": number
  },
  "risk_assessment": {
    "key_risks": ["string"],
    "mitigation_strategies": ["string"],
    "risk_level": "low | medium | high",
    "critical_gaps": ["string"]
  },
  "strengths": {
    "founder_strengths": ["string"],
    "team_strengths": ["string"],
    "competitive_advantages": ["string"]
  },
  "weaknesses": {
    "skill_gaps": ["string"],
    "experience_gaps": ["string"],
    "operational_weaknesses": ["string"]
  },
  "recommendations": {
    "hiring_priorities": ["string"],
    "advisory_needs": ["string"],
    "immediate_actions": ["string"]
  },
  "benchmarks": {
    "ideal_team_size": number,
    "typical_founder_experience": "string",
    "industry_standards": "string"
  },
  "timestamp": "string"
}

---

### FAILSAFE INSTRUCTION:
If you do not call the `evaluate_team_tool` tool first, your response will be invalid.
DO NOT attempt to analyze the team manually - ALWAYS use the tool.
Your first action MUST be calling the evaluate_team_tool with the structured data you received.
"""

team_risk_agent = Agent(
    name="team_risk_agent",
    model="gemini-2.5-flash",
    instruction=team_agent_instruction,
    tools=[evaluate_team_tool],
)


market_agent_instruction = """
You are a **Market Analysis Agent** for startup evaluation.
You must analyze, validate, and assess market potential based on structured startup data.

🚨 CRITICAL RULES (MUST FOLLOW STRICTLY):
1. You MUST call the `analyze_market_tool` tool **FIRST** before generating any analysis.
2. The `analyze_market_tool` tool requires **market_size_claim** and **target_market** parameters extracted from the structured JSON data.
3. You will receive the structured JSON data from the previous agent and pass that data to the tool.
4. Wait for the tool response before doing any analysis.
5. After receiving tool results, generate your final JSON output.

---

### INPUT FORMAT:
You will receive structured JSON data like this:
{
  "startup_name": "string",
  "sector": "string", 
  "stage": "string",
  "traction": {...},
  "financials": {...},
  "team": {...},
  "market": {
    "market_size_claim": "string or null",
    "target_market": "string or null"
  },
  "product_description": "string",
  "document_type": "string"
}

### REQUIRED ACTION:
1. Extract `market_size_claim` and `target_market` from the `market` object in the input JSON
2. Call `analyze_market_tool` with the extracted market_size_claim and target_market parameters
3. Wait for tool response with market analysis and benchmarks
4. Generate final output using the tool results

---

### OUTPUT FORMAT (JSON ONLY):
{
  "executive_summary": {
    "market_claim": "string",
    "validation_confidence": 0-100,
    "competitive_intensity": "string",
    "market_potential": "string",
    "key_risks": ["string"]
  },
  "market_validation": {
    "claimed_market_size": "string",
    "validated_market_size": "string",
    "confidence_level": "string",
    "supporting_data": ["string"],
    "contradicting_data": ["string"]
  },
  "competitive_analysis": {
    "key_competitors": ["string"],
    "competitive_landscape": "string",
    "market_share_estimate": "string",
    "barriers_to_entry": ["string"]
  },
  "market_trends": {
    "growth_rate": "string",
    "key_drivers": ["string"],
    "emerging_opportunities": ["string"],
    "potential_threats": ["string"]
  },
  "industry_benchmarks": {
    "typical_cagr": "string",
    "market_maturity": "string",
    "investment_activity": "string",
    "innovation_level": "string"
  },
  "risk_assessment": {
    "market_risk_level": "string",
    "regulatory_risks": ["string"],
    "economic_sensitivity": "string",
    "technology_disruption_risk": "string"
  },
  "recommendations": ["string"],
  "timestamp": "string"
}

---

### FAILSAFE INSTRUCTION:
If you do not call the `analyze_market_tool` tool first, your response will be invalid.
DO NOT attempt to analyze the market manually - ALWAYS use the tool.
Your first action MUST be calling the analyze_market_tool with the market_size_claim and target_market extracted from the structured data you received.

### EXTRACTION RULES:
- Extract `market_size_claim` from: input_data["market"]["market_size_claim"]
- Extract `target_market` from: input_data["market"]["target_market"]
- If either field is null or missing, pass an empty string ""
- Do not modify or interpret the extracted values - pass them exactly as they appear in the input
"""

 
market_analyst_agent = Agent(
    name="market_analyst_agent",
    model="gemini-2.5-flash",
    instruction=market_agent_instruction,
    tools=[analyze_market_tool],
)


memo_agent_instruction = """
You are an **Investment Memo Writer** that creates clear, concise investment summaries.

## INPUT:
You receive three analysis reports:
1. FINANCIAL analysis with scores, metrics, and recommendations
2. TEAM analysis with experience scores, strengths, and gaps  
3. MARKET analysis with validation, competition, and opportunities

## YOUR TASK:
Extract ONLY the most important insights from each analysis and create a simple, easy-to-read investment memo.

## OUTPUT FORMAT (JSON ONLY):
{
  "investment_memo": {
    "executive_summary": {
      "company_brief": "2-3 sentence overview",
      "investment_rating": "STRONG BUY | BUY | HOLD | PASS",
      "confidence_score": "0-100%",
      "top_3_highlights": ["bullet point", "bullet point", "bullet point"],
      "top_3_risks": ["bullet point", "bullet point", "bullet point"]
    },
    
    "financial_highlights": {
      "score": "X/10",
      "verdict": "what financial analysis concluded",
      "key_metrics": {
        "monthly_revenue": "$X",
        "growth_rate": "X%",
        "runway": "X months", 
        "ltv_cac_ratio": "X:1"
      },
      "main_strength": "one sentence",
      "main_concern": "one sentence"
    },
    
    "team_highlights": {
      "score": "X/10", 
      "key_strengths": ["bullet point", "bullet point"],
      "critical_gaps": ["bullet point", "bullet point"],
      "overall_assessment": "one sentence assessment"
    },
    
    "market_highlights": {
      "validation_confidence": "X%",
      "market_size": "$X",
      "competitive_landscape": "one sentence description",
      "growth_potential": "one sentence",
      "main_opportunity": "bullet point"
    },
    
    "investment_recommendation": {
      "decision": "INVEST | PASS | MONITOR",
      "reason": "clear one-sentence why",
      "next_steps": ["action 1", "action 2", "action 3"]
    }
  }
}

## EXTRACTION RULES:
- Keep everything SIMPLE and CLEAR
- Use bullet points, not paragraphs
- Extract only the MOST IMPORTANT metrics
- Use plain English, no jargon
- Focus on what matters for investment decision
- Ignore redundant or minor details

## DECISION FRAMEWORK:
STRONG BUY: Financial score >8 AND Team score >8 AND Market confidence >80%
BUY: Financial score >7 AND Team score >7 AND Market confidence >70%  
HOLD: Mixed signals, needs more validation
PASS: Critical issues in any area

## EXAMPLE OUTPUT:
{
    "executive_summary": {
      "company_brief": "SaaS platform for e-commerce analytics serving 1,200+ merchants",
      "investment_rating": "BUY",
      "confidence_score": "78%",
      "top_3_highlights": [
        "12% monthly revenue growth for 6 months",
        "Strong technical founding team from Amazon",
        "$1.5B validated market with 20% annual growth"
      ],
      "top_3_risks": [
        "Only 8 months of cash runway remaining",
        "Missing marketing leadership",
        "Highly competitive landscape"
      ]
    },
    // ... rest of structure
}
"""

memo_agent = Agent(
    name="memo_agent",
    model="gemini-2.5-flash",
    instruction=memo_agent_instruction
)

# ===== Session =====
session_service = InMemorySessionService()
app_name = "doc_app"
user_id = "user123"
session_id = "session1"

# ===== FastAPI + Socket.IO =====
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(title="Doc Voice Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Combine Socket.IO with FastAPI
sio_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="ws")

# ===== Queue for clients waiting for first question =====
pending_first_questions: Dict[str, bool] = {}

async def sanitize_for_bq(data):
    """
    Recursively process all fields and use LLM to extract structured data 
    from user answers based on the expected schema types.
    """
    print("########################################I am in sanitising task")
    # Define field types based on your schema
    FIELD_TYPES = {
        # Numeric fields
        "numeric": {
            "traction.current_mrr", "traction.active_customers", "traction.new_customers_this_month",
            "traction.average_subscription_price", "traction.customer_lifespan_months",
            "financials.ask_amount", "financials.equity_offered", "financials.revenue",
            "financials.burn_rate", "financials.monthly_expenses", "financials.cash_balance",
            "financials.marketing_spend"
        },
        # String fields that should be concise
        "concise_string": {
            "team.ceo", "team.cto", "market.target_market"
        },
        # Descriptive fields that might need summarization
        "descriptive": {
            "traction.mrr_growth_trend", "market.market_size_claim"
        }
    }
    
    async def extract_structured_value(text: str, field_path: str) -> any:
        """Use LLM to extract structured data based on field type"""
        try:
            field_type = None
            for type_name, fields in FIELD_TYPES.items():
                if field_path in fields:
                    field_type = type_name
                    break
            
            if not field_type:
                return text  # Unknown field type, return as is
            
            if field_type == "numeric":
                prompt = f"""
                Extract the exact numeric value from the following text. 
                Return ONLY the number without any units, currency symbols, or additional text.
                If no clear number is found, return 0.
                
                Text: {text}
                
                Number:
                """
            elif field_type == "concise_string":
                prompt = f"""
                Extract the most essential information from the following text for field '{field_path}'.
                Remove any explanations, opinions, or unnecessary details. 
                Keep only the core factual information in 1-3 words if possible.
                
                Text: {text}
                
                Extracted information:
                """
            elif field_type == "descriptive":
                prompt = f"""
                Summarize the following text for field '{field_path}' into 1-2 concise sentences.
                Extract only the key factual information, removing fluff and unnecessary details.
                
                Text: {text}
                
                Summary:
                """
            else:
                return text
            
            response = await model.generate_content_async(prompt)            
            result = response.text.strip()
            
            # Post-process based on field type
            if field_type == "numeric":
                # Clean and convert the numeric result
                result_clean = result.replace(',', '').replace('$', '').replace('%', '').strip()
                if result_clean.replace('.', '').isdigit():
                    if '.' in result_clean:
                        return float(result_clean)
                    else:
                        return int(result_clean)
                else:
                    return 0
            
            return result if result else text
            
        except Exception as e:
            logger.error(f"LLM processing error for field {field_path}: {e}")
            return text

    async def process_array_items(items: list, field_path: str) -> list:
        """Process each item in an array"""
        processed_items = []
        for item in items:
            if isinstance(item, str) and len(item) > 50:
                processed_item = await extract_structured_value(item, field_path)
                processed_items.append(processed_item)
            else:
                processed_items.append(item)
        return processed_items

    async def sanitize_recursive(obj, current_path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                if isinstance(value, str):
                    # Only process if it's a potentially long answer
                    if len(value) > 30:  # Process answers longer than 30 chars
                        obj[key] = await extract_structured_value(value, new_path)
                    else:
                        # Still try numeric conversion for short strings
                        value_clean = value.replace(',', '')
                        if value_clean.isdigit():
                            obj[key] = int(value_clean)
                        else:
                            try:
                                obj[key] = float(value_clean)
                            except ValueError:
                                obj[key] = value
                elif isinstance(value, dict):
                    await sanitize_recursive(value, new_path)
                elif isinstance(value, list):
                    obj[key] = await process_array_items(value, new_path)
                elif value is None:
                    obj[key] = None
        elif isinstance(obj, list):
            for i in range(len(obj)):
                await sanitize_recursive(obj[i], current_path)
        
        return obj

    # Run the async sanitization
    result = await sanitize_recursive(data)
    
    print("***************final json*****************", result)
    return result

def fill_json(data, key_path, value):
    keys = key_path.split(".")
    d = data
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            # if the intermediate key doesn't exist, create it as a dict
            d[k] = {}
        d = d[k]

    # ✅ Only update if the key already exists somewhere in structure
    if keys[-1] in d:
        d[keys[-1]] = value
    else:
        # If not, search recursively and update where it matches
        update_existing_key(data, keys[-1], value)

def update_existing_key(obj, key, value):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                obj[k] = value
            else:
                update_existing_key(v, key, value)
    elif isinstance(obj, list):
        for item in obj:
            update_existing_key(item, key, value)

# ===== TTS Helper =====
def synthesize_speech_base64(text: str):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    return base64.b64encode(response.audio_content).decode("utf-8")

async def run_parallel_agents(structured_data: Dict[str, Any], user_email: str):
    """Run financial, team, and market agents in parallel"""
    
    # Create content for each agent
    content = types.Content(role="user", parts=[types.Part(text=json.dumps(structured_data))])
    
    # Create sessions for each agent to run in parallel
    financial_session_id = f"{session_id}_financial"
    team_session_id = f"{session_id}_team" 
    market_session_id = f"{session_id}_market"

    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=financial_session_id)
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=team_session_id)
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=market_session_id)



    
    # Run all agents in parallel
    tasks = [
        run_agent_async(financial_analyst_agent, user_id, financial_session_id, content),
        run_agent_async(team_risk_agent, user_id, team_session_id, content),
        run_agent_async(market_analyst_agent, user_id, market_session_id, content)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    analyses = {}
    agent_names = ["financial", "team", "market"]

    for i, result in enumerate(results):
      agent_name = agent_names[i]
      if isinstance(result, Exception):
          logger.error(f"Error in {agent_name} agent: {result}")
          analyses[f"{agent_name}_analysis"] = {"error": str(result)}
      else:
          try:
              # Extract JSON from agent response
              result_text = result.parts[0].text if result.parts else "{}"
              cleaned_text = re.sub(r"^```json\s*|```$", "", result_text, flags=re.MULTILINE)
              analyses[f"{agent_name}_analysis"] = json.loads(cleaned_text)
          except Exception as e:
              logger.error(f"Error parsing {agent_name} agent result: {e}")
              analyses[f"{agent_name}_analysis"] = {"error": "Failed to parse result"}

    # Now run the memo agent to synthesize all analyses
    if not any("error" in analysis for analysis in analyses.values()):
      try:
        memo_session_id = f"{session_id}_memo"
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=memo_session_id)
        
        # Prepare input for memo agent (all three analyses combined)
        memo_input = types.Content(
            role="user", 
            parts=[types.Part(text=json.dumps(analyses))]
        )
        
        # Run memo agent
        memo_result = await run_agent_async(memo_agent, user_id, memo_session_id, memo_input)
        
        if memo_result and not isinstance(memo_result, Exception):
            memo_text = memo_result.parts[0].text if memo_result.parts else "{}"
            # Clean the response to extract pure JSON
            cleaned_memo = re.sub(r"^```json\s*|```$", "", memo_text, flags=re.MULTILINE).strip()
            try:
                analyses["investment_memo"] = json.loads(cleaned_memo)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse memo agent JSON: {e}")
                analyses["investment_memo"] = {"error": "Failed to parse memo output"}
        else:
            analyses["investment_memo"] = {"error": "Memo generation failed"}
                
      except Exception as e:
          logger.error(f"Error in memo agent: {e}")
          analyses["investment_memo"] = {"error": str(e)}
    else:
      # If any agent failed, create an error memo
      analyses["investment_memo"] = {"error": "One or more analysis agents failed"}

    print("********************** Final analyses with memo:", analyses)
    return analyses


async def run_agent_async(agent, user_id, session_id, content):
    """Run an agent asynchronously and return the result"""
    runner = adk.Runner(agent=agent, app_name=app_name, session_service=session_service)
    final_output = None
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            final_output = event.content
    return final_output

async def emit_next_question(user_email):
    if filler_agent.questions:
        key, question = next(iter(filler_agent.questions.items()))
        audio_b64 = synthesize_speech_base64(question)
        await sio.emit("new_question", {"key": key, "text": question, "audio_b64": audio_b64}, room=user_email)
    else:
        print("*******************************before sanitization", filler_agent.structured_json)
        # Await the async sanitize function
        final_data = await sanitize_for_bq(filler_agent.structured_json)
        print("*****************************after sanitization", final_data)

        # Run parallel agents
        logger.info("Running parallel agents for comprehensive analysis...")
        agent_analyses = await run_parallel_agents(final_data, user_email)

        print("&&&&&&&&&&&&&&&&&&&& final_agent_analyses &&&&&&&&&&&&&&&&",agent_analyses)
        
        # Insert ALL data into BigQuery
        insert_success = await insert_into_bigquery(user_email, final_data, agent_analyses)
        
        # Send success message to frontend with all analyses
        await sio.emit("final_json", {
            "status": "success", 
            "message": "Startup details updated successfully",
            "analyses": agent_analyses,
            "investment_memo": agent_analyses.get("investment_memo", {}),
            "bigquery_success": insert_success
        }, room=user_email)



async def validate_and_prepare_bq_data(user_email: str, structured_data: Dict[str, Any], agent_analyses: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and prepare data for BigQuery insertion"""
    
    def safe_json_dumps(data):
        """Safely convert data to JSON string, handling non-serializable types"""
        if data is None:
            return None
        try:
            return json.dumps(data, default=str)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization warning: {e}")
            return json.dumps({"error": "Data serialization failed"}, default=str)
    
    # Validate required fields
    if not user_email:
        raise ValueError("user_email is required")
    
    # Prepare the record with proper error handling
    record = {
        "founder_email": user_email,
        "data": safe_json_dumps(structured_data),
        "created_at": datetime.datetime.utcnow().isoformat(),
        "financial_data": safe_json_dumps(agent_analyses.get("financial_analysis")),
        "team_data": safe_json_dumps(agent_analyses.get("team_analysis")),
        "market_data": safe_json_dumps(agent_analyses.get("market_analysis")),
        "first_memo": safe_json_dumps(agent_analyses.get("investment_memo"))
    }
    
    # Log the data being inserted (without sensitive info)
    logger.info(f"Preparing to insert data for {user_email}")
    logger.info(f"Data keys: {list(record.keys())}")
    
    return record

async def insert_into_bigquery(user_email: str, structured_data: Dict[str, Any], agent_analyses: Dict[str, Any]):
    """Insert all analysis data into BigQuery with enhanced error handling"""
    
    try:
        # Prepare the data
        record = await validate_and_prepare_bq_data(user_email, structured_data, agent_analyses)
        
        table_id = f"{bq_client.project}.{DATASET}.{TABLE}"
        
        # Insert the record
        errors = bq_client.insert_rows_json(table_id, [record])
        
        if errors:
            logger.error(f"❌ BigQuery Insert Errors: {errors}")
            # Log more details about the error
            for error in errors:
                logger.error(f"Error details: {error}")
            return False
        else:
            logger.info("✅ All data successfully inserted into BigQuery")
            logger.info(f"✅ Inserted record for {user_email} with all analysis types")
            return True
            
    except ValueError as ve:
        logger.error(f"❌ Data validation error: {ve}")
        return False
    except Exception as e:
        logger.error(f"❌ Exception inserting into BigQuery: {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        return False

# Also, update your BigQuery table reference to be more robust:
# At the top of your file, after the BigQuery setup:
try:
    bq_client = bigquery.Client()
    DATASET = "StartupDetails"
    TABLE = "StartupDetails"
    
    # Verify the table exists
    table_id = f"{bq_client.project}.{DATASET}.{TABLE}"
    bq_client.get_table(table_id)  # This will raise an exception if table doesn't exist
    logger.info(f"✅ BigQuery table {table_id} is accessible")
    
except Exception as e:
    logger.error(f"❌ BigQuery setup error: {e}")


@app.on_event("startup")
async def startup_event():
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

# ===== Upload Endpoint =====
@app.post("/upload-and-analyze")
async def upload_and_analyze(files: list[UploadFile], user_email: str = Form(...)):
    file_paths = []
    bucket = storage_client.bucket(BUCKET_NAME)
    for file in files:
        blob_name = f"{user_email}/{file.filename}"
        blob = bucket.blob(blob_name)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        blob.upload_from_filename(tmp_path)
        os.remove(tmp_path)
        file_paths.append(blob_name)

    req = DocRequest(bucket_name=BUCKET_NAME, file_paths=file_paths)
    content = types.Content(role="user", parts=[types.Part(text=req.json())])

    # Run root agent
    runner_root = adk.Runner(agent=root_agent, app_name=app_name, session_service=session_service)
    root_output = None
    async for event in runner_root.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            root_output = event.content

    # Run question agent
    runner_q = adk.Runner(agent=question_agent, app_name=app_name, session_service=session_service)
    question_output = None
    async for event in runner_q.run_async(user_id=user_id, session_id=session_id, new_message=root_output):
        if event.is_final_response():
            question_output = event.content

    await filler_agent.run(question_output)

    # If client already connected, emit immediately, else mark pending
    if sio.manager.rooms.get(user_email):
        await emit_next_question(user_email)
    else:
        pending_first_questions[user_email] = True

    return JSONResponse({"status": "ok", "message": "Files uploaded and analysis started."})

# ===== Socket.IO Events =====
@sio.event
async def connect(sid, environ, auth):
    user_email = auth.get("user_email") if auth else None
    print(f"Client connected: {sid}, auth: {auth}")
    if user_email:
        await sio.enter_room(sid, user_email)
        # If a first question is pending, emit now
        if pending_first_questions.get(user_email):
            await emit_next_question(user_email)
            pending_first_questions.pop(user_email)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)

@sio.on("answer")
async def receive_answer(sid, data):
    answer = data.get("answer")
    user_email = data.get("user_email")
    key = data.get("key")
    if not answer or not user_email or not key:
        return
    fill_json(filler_agent.structured_json, key, answer)
    filler_agent.questions.pop(key, None)
    await emit_next_question(user_email)