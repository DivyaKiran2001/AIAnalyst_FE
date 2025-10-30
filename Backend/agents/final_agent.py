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
# import datetime
from google import genai



from fastapi import FastAPI, HTTPException
from fastapi import Request as FastAPIRequest
from google.auth.transport.requests import Request as GoogleRequest
from google.auth.transport.requests import Request
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pymongo.errors import CollectionInvalid
import os
from bson import ObjectId
import smtplib
import random
import string
from email.mime.text import MIMEText
from datetime import datetime, timedelta,time
import socketio
import json
import pytz
# from datetime import datetime
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow


# ===== Logging =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pipeline_logger")

# ===== GCS Setup =====
BUCKET_NAME = "ai-analyst-uploads-files1"
storage_client = storage.Client()

vertexai.init(project="intense-subject-470817-v2", location="us-central1")

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

# Normalize startup name from AI
def normalize_name(name: str) -> str:
    return "".join(name.lower().split())  # removes spaces and lowercases

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
You are an *Investment Memo Writer* that creates clear, concise investment summaries.

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
      "sector": "sector name from input",
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
      "sector":"SaaS",
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
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# MongoDB Atlas Connection
# -------------------------
MONGO_URI = "mongodb+srv://divyakirantatikonda_db_user:hQZOVv9ROilEKN4j@cluster0.l492nrq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["StartupAnalyst"]


# Create users collection with schema validation (run only once)
try:
    db.create_collection(
        "Users",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "uid","password","role"],
                "properties": {
                    "email": {"bsonType": "string"},
                    "uid": {"bsonType": "string"},
                    "password": {"bsonType": "string"},
                    "role": {"bsonType": "string"}
                }
            }
        }
    )
except Exception:
    # collection already exists
    pass


# FounderDetails Collection
try:
    db.create_collection(
        "FounderDetails",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "yourName",
                    "emailId",
                    "gender",
                    "phoneNumber",
                    "linkedinUrl",
                    "singleFounder",
                    "role",
                ],
                "properties": {
                    "yourName": {"bsonType": "string"},
                    "emailId": {"bsonType": "string"},
                    "gender": {"bsonType": "string"},
                    "phoneNumber": {"bsonType": "string"},
                    "linkedinUrl": {"bsonType": "string"},
                    "singleFounder": {"bsonType": "string"},
                    "referrer": {"bsonType": ["string", "null"]},
                    "role": {"bsonType": "string"},
                    "uid": {"bsonType": "string"},
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
    )
    print("✅ 'FounderDetails' collection created with schema.")
except Exception:
    print("ℹ️ 'FounderDetails' collection already exists.")

# try:
#     db.create_collection(
#         "StartupDetails",
#         validator={
#             "$jsonSchema": {
#                 "bsonType": "object",
#                 "required": [
#                     "startupName",
#                     "registeredName",
#                     "incorporationMonth",
#                     "incorporationYear",
#                     "about",
#                     "emailId",
#                     "uid",
#                     "createdAt"
#                 ],
#                 "properties": {
#                     "startupName": {"bsonType": "string"},
#                     "registeredName": {"bsonType": "string"},
#                     "incorporationMonth": {"bsonType": "string"},
#                     "incorporationYear": {"bsonType": "string"},
#                     "about": {"bsonType": "string"},

#                     # Founder identity
#                     "emailId": {"bsonType": "string"},
#                     "uid": {"bsonType": "string"},

#                     # Uploaded Files Section
#                     "uploadedFiles": {
#                         "bsonType": "array",
#                         "items": {
#                             "bsonType": "object",
#                             "required": ["fileName", "gcsUrl"],
#                             "properties": {
#                                 "fileName": {"bsonType": "string"},
#                                 "gcsUrl": {"bsonType": "string"},
#                                 "uploadedAt": {"bsonType": "date"}
#                             }
#                         }
#                     },

#                     "createdAt": {"bsonType": "date"},
#                     "updatedAt": {"bsonType": "date"},
#                 },
#             }
#         },
#     )
#     print("✅ 'StartupDetails' collection created with updated schema.")
# except Exception:
#     print("ℹ️ 'StartupDetails' collection already exists.")

# ---------------------------
# 2️⃣ Update schema validation
# ---------------------------
try:
    db.command({
        "collMod": "StartupDetails",
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "startupName",
                    "registeredName",
                    "incorporationMonth",
                    "incorporationYear",
                    "about",
                    "emailId",
                    "uid",
                    "createdAt"
                ],
                "properties": {
                    "startupName": {"bsonType": "string"},
                    "registeredName": {"bsonType": "string"},
                    "incorporationMonth": {"bsonType": "string"},
                    "incorporationYear": {"bsonType": "string"},
                    "about": {"bsonType": "string"},

                    # Founder identity
                    "emailId": {"bsonType": "string"},
                    "uid": {"bsonType": "string"},

                    # Uploaded Files Section
                    "uploadedFiles": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["fileName", "gcsUrl"],
                            "properties": {
                                "fileName": {"bsonType": "string"},
                                "gcsUrl": {"bsonType": "string"},
                                "uploadedAt": {"bsonType": "date"}
                            }
                        }
                    },

                    # BigQuery Analysis Data
                    "bigqueryData": {
                        "bsonType": "object",
                        "properties": {
                            "financial_data": {"bsonType": "string"},
                            "team_data": {"bsonType": "string"},
                            "market_data": {"bsonType": "string"},
                            "first_memo": {"bsonType": "string"}
                        }
                    },

                    "createdAt": {"bsonType": "date"},
                    "updatedAt": {"bsonType": "date"},
                }
            }
        },
        "validationLevel": "moderate"  # Allows existing documents without new fields
    })
    print("✅ 'StartupDetails' collection schema updated successfully!")
except Exception as e:
    print(f"❌ Failed to update schema: {e}")

try:
    db.create_collection(
        "InvestorInterests",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["startupName", "founderEmail", "investorEmail", "status", "createdAt"],
                "properties": {
                    "startupName": {"bsonType": "string"},
                    "founderEmail": {"bsonType": "string"},
                    "investorEmail": {"bsonType": "string"},
                    "status": {"bsonType": "string"},  # e.g., "interested", "chatting", "closed"
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
    )
    print("✅ 'InvestorInterests' collection created with schema validation.")
except Exception:
    print("ℹ️ 'InvestorInterests' collection already exists.")


# ----------------- Create Chats collection with schema validation -----------------
# try:
#     db.create_collection(
#         "Chats",
#         validator={
#             "$jsonSchema": {
#                 "bsonType": "object",
#                 "required": ["participants", "messages", "createdAt"],
#                 "properties": {
#                     "participants": {
#                         "bsonType": "array",
#                         "minItems": 2,
#                         "items": {"bsonType": "string"}  # emails or UIDs
#                     },
#                     "messages": {
#                         "bsonType": "array",
#                         "items": {
#                             "bsonType": "object",
#                             "required": ["senderId", "text", "timestamp"],
#                             "properties": {
#                                 "senderId": {"bsonType": "string"},
#                                 "text": {"bsonType": "string"},
#                                 "timestamp": {"bsonType": "date"},
#                             },
#                         },
#                     },
#                     "createdAt": {"bsonType": "date"},
#                 },
#             }
#         },
#     )
#     print("✅ 'Chats' collection created with schema validation")
# except Exception:
#     print("ℹ️ 'Chats' collection already exists")


try:
    db.create_collection(
        "Chats",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["participants", "messages", "createdAt", "startupName"],
                "properties": {
                    "startupName": {"bsonType": "string"},
                    "participants": {
                        "bsonType": "array",
                        "minItems": 2,
                        "items": {"bsonType": "string"}
                    },
                    "messages": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "required": ["senderId", "text", "timestamp"],
                            "properties": {
                                "senderId": {"bsonType": "string"},
                                "text": {"bsonType": "string"},
                                "timestamp": {"bsonType": "date"}
                            },
                        },
                    },
                    "createdAt": {"bsonType": "date"},
                },
            }
        },
    )
    print("✅ 'Chats' collection created with startupName field")
except Exception:
    print("ℹ️ 'Chats' collection already exists")


# ----------------- Create Meetings Collection with Schema -----------------
try:
    db.create_collection(
        "Meetings",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["startupName", "founderEmail", "investorEmail", "proposedDateTime", "status", "createdAt"],
                "properties": {
                    "startupName": {"bsonType": "string"},
                    "founderEmail": {"bsonType": "string"},
                    "investorEmail": {"bsonType": "string"},
                    "proposedDateTime": {"bsonType": "date"},
                    "status": {"bsonType": "string"},  # "pending", "accepted", "declined"
                    "createdAt": {"bsonType": "date"}
                },
            }
        },
    )
    print("✅ 'Meetings' collection created with schema validation.")
except Exception:
    print("ℹ️ 'Meetings' collection already exists.")

try:
    db.create_collection(
        "UserGoogleCredentials",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "credentials"],
                "properties": {
                    "email": {"bsonType": "string"},
                    "credentials": {"bsonType": "object"},
                },
            }
        },
    )
    print("✅ 'UserGoogleCredentials' collection created.")
except Exception:
    print("ℹ️ 'UserGoogleCredentials' collection already exists.")

try:
    db.create_collection(
        "FounderSlots",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["founderEmail", "date", "startTime", "endTime", "status", "createdAt"],
                "properties": {
                    "founderEmail": {"bsonType": "string"},
                    "date": {"bsonType": "string"},  # YYYY-MM-DD
                    "startTime": {"bsonType": "date"},
                    "endTime": {"bsonType": "date"},
                    "status": {"bsonType": "string"},  # "available", "booked"
                    "createdAt": {"bsonType": "date"}
                },
            }
        },
    )
    print("✅ 'FounderSlots' collection created with schema validation.")
except CollectionInvalid:
    print("ℹ️ 'FounderSlots' collection already exists.")

founder_slots_collection = db["FounderSlots"]
chat_collection = db["Chats"]
users_collection = db["Users"]
interests_collection=db["InvestorInterests"]

founder_collection = db["FounderDetails"]
startup_collection = db["StartupDetails"]
meetings_collection = db["Meetings"]
user_credentials_collection = db["UserGoogleCredentials"]


# ------------------ Google OAuth Setup ------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = "http://localhost:8000/api/google/oauth2callback"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


from pydantic import BaseModel
class FounderDetails(BaseModel):
    yourName: str
    emailId: EmailStr
    gender: str
    phoneNumber: str
    linkedinUrl: str
    singleFounder: str
    referrer: str | None = None

class StartupDetails(BaseModel):
   
    startupName: str
    registeredName: str
    incorporationMonth: str
    incorporationYear: str
    about: str
    emailId:str

# --- Pydantic Model ---
class Interest(BaseModel):
    startupName: str
    founderEmail: str
    investorEmail: str
    status: str = "pending"
    createdAt: datetime | None = None

    
class AcceptInterest(BaseModel):
    founderEmail: str
    investorEmail: str
    startupName: str 
class MeetingRequest(BaseModel):
    startupName: str
    founderEmail: EmailStr
    investorEmail: EmailStr
    proposedDateTime: datetime

class RespondMeeting(BaseModel):
    meetingId: str
    action: str  # accept or decline


class OAuthRequest(BaseModel):
    email: EmailStr



# Combine Socket.IO with FastAPI
# sio_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="ws")
sio_app = socketio.ASGIApp(sio, app)

import firebase_admin
from firebase_admin import credentials, auth
cred = credentials.Certificate(
    r"D:\GenAI_Exchange\AIAnalyst_FE\Backend\aianalyst-61509-firebase-adminsdk-fbsvc-17fb406b27.json"
)
firebase_admin.initialize_app(cred)


# ----------------- Helper Functions -----------------
def check_investor_interest(founder_email, investor_email):
    """Check if investor is allowed to request a meeting."""
    record = interests_collection.find_one({
        "founderEmail": founder_email,
        "investorEmail": investor_email,
        "status": "accepted"
    })
    return record is not None

def check_time_conflict(email, proposed_datetime, duration_minutes=30, exclude_meeting_id=None):
    start = proposed_datetime
    end = proposed_datetime + timedelta(minutes=duration_minutes)

    query = {
        "$or": [
            {"founderEmail": email},
            {"investorEmail": email}
        ],
        "status": {"$in": ["pending", "accepted"]},
        "$expr": {
            "$and": [
                {"$lt": ["$proposedDateTime", end]},
                {"$gt": ["$endTime", start]}
            ]
        }
    }

    # 👇 exclude the same meeting being accepted
    if exclude_meeting_id:
        query["_id"] = {"$ne": ObjectId(exclude_meeting_id)}

    meeting_conflict = meetings_collection.find_one(query)
    return meeting_conflict is not None

@app.get("/api/founder/slots")
def get_slots(founderEmail: str, date: str):
    """
    Retrieve all available slots for a founder on a specific date.
    If slots do not exist yet, generate them automatically.
    Only return slots with status 'available'.
    """
    # Parse date
    try:
        base_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Fetch existing available slots
    available_slots = list(founder_slots_collection.find(
        {"founderEmail": founderEmail, "date": date, "status": "available"}
    ))

    if available_slots:
        # Convert ObjectId and datetime to string for JSON
        for slot in available_slots:
            slot["_id"] = str(slot["_id"])
            slot["startTime"] = slot["startTime"].astimezone(pytz.timezone("Asia/Kolkata")).isoformat()
            slot["endTime"] = slot["endTime"].astimezone(pytz.timezone("Asia/Kolkata")).isoformat()
            slot["createdAt"] = slot["createdAt"].isoformat()
        return {"date": date, "slots": available_slots}

    # Check if any slots exist at all
    existing_slots = list(founder_slots_collection.find(
        {"founderEmail": founderEmail, "date": date}
    ))
    if existing_slots:
        # Slots exist but none are available
        return {"date": date, "slots": []}

    # No slots exist, generate automatically
    ist = pytz.timezone("Asia/Kolkata")
    start_time = ist.localize(datetime.combine(base_date, time(9, 0)))
    end_time = ist.localize(datetime.combine(base_date, time(18, 0)))
    lunch_start = ist.localize(datetime.combine(base_date, time(13, 0)))
    lunch_end = ist.localize(datetime.combine(base_date, time(14, 0)))

    slot_duration = timedelta(minutes=30)
    slots_to_insert = []
    current = start_time

    while current < end_time:
        next_slot = current + slot_duration
        # Skip lunch
        if next_slot <= lunch_start or current >= lunch_end:
            slot_doc = {
                "founderEmail": founderEmail,
                "date": date,
                "startTime": current,
                "endTime": next_slot,
                "status": "available",
                "createdAt": datetime.utcnow()
            }
            slots_to_insert.append(slot_doc)
        current = next_slot

    if not slots_to_insert:
        raise HTTPException(status_code=400, detail="No valid slots generated.")

    # Insert slots in MongoDB
    result = founder_slots_collection.insert_many(slots_to_insert)

    # Convert inserted slots to JSON-friendly format
    for slot, oid in zip(slots_to_insert, result.inserted_ids):
        slot["_id"] = str(oid)
        slot["startTime"] = slot["startTime"].isoformat()
        slot["endTime"] = slot["endTime"].isoformat()
        slot["createdAt"] = slot["createdAt"].isoformat()

    return {"date": date, "slots": slots_to_insert}


def get_calendar_service(user_email):
    creds_data = user_credentials_collection.find_one({"email": user_email})
    print(creds_data)
    if not creds_data or "credentials" not in creds_data:
        raise HTTPException(
            status_code=401,
            detail=f"Google authorization expired for {user_email}. Please reconnect your calendar."
        )

    creds_dict = creds_data["credentials"]

    # Fix expiry for Google API
    if "expiry" in creds_dict:
        if isinstance(creds_dict["expiry"], datetime):
            creds_dict["expiry"] = creds_dict["expiry"].replace(microsecond=0).isoformat() + "Z"
            print("EXPIRY",creds_dict["expiry"])
        elif isinstance(creds_dict["expiry"], str) and "." in creds_dict["expiry"]:
            creds_dict["expiry"] = creds_dict["expiry"].split(".")[0] + "Z"

    # Create Credentials object
    creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
    print("CCCCCCCCCCCCCCC",creds)

    # Auto-refresh token if expired
    if creds.expired and creds.refresh_token:
        print("REFRESHING TOKEN...........................")
        try:
            creds.refresh(Request())
            # Save updated credentials back to DB
            user_credentials_collection.update_one(
                {"email": user_email},
                {"$set": {"credentials": json.loads(creds.to_json())}}
            )
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Google authorization expired for {user_email}. Please reconnect your calendar."
            )
        print("SAVED NEW TOKEN")

    return build("calendar", "v3", credentials=creds)

@app.get("/api/google/authorize")
def authorize_google(email: str):
    """
    Redirect user to Google OAuth consent screen.
    Role is optional and defaults to founder.
    """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=email
    )
    print(authorization_url)
    # ✅ Redirect browser to Google consent screen
    return RedirectResponse(url=authorization_url)
    # return {"auth_url": authorization_url}


@app.get("/api/google/oauth2callback")
def oauth2callback(code: str, state: str):
    """
    Callback from Google with code.
    Save credentials and redirect user to dashboard.
    """
    try:
        email = state       # just use state as email
        role = "founder"    # default role

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Save credentials in MongoDB
        user_credentials_collection.update_one(
            {"email": email},
            {"$set": {"credentials": json.loads(creds.to_json())}},
            upsert=True
        )

        dashboard_url = "http://localhost:3000/f-dashboard?calendarConnected=true"
        return RedirectResponse(url=dashboard_url)

       
    except Exception as e:
        print("❌ OAuth Callback Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google/is_connected")
def is_connected(email: str):
    user = user_credentials_collection.find_one({"email": email})
    return {"connected": bool(user)}

@app.get("/api/founder/interested-investors")
async def get_interested_investors(founderEmail: str):
    interests = list(interests_collection.find({"founderEmail": founderEmail}, {"_id": 0}))
    print(interests)
    return {"investors": interests}
    
def verify_firebase_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        print("✅ Valid Firebase token:", decoded_token)
        return decoded_token
    except Exception as e:
        print("❌ Token verification error:", e)
        raise HTTPException(status_code=401, detail="Invalid Firebase token")



# -------------------------
# Auth Endpoint
# -------------------------
@app.post("/api/auth")
async def auth_user(request: FastAPIRequest):
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        print("No bearer...")
        raise HTTPException(status_code=401, detail="Missing auth token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)

    user_data = await request.json()
    print(user_data)
    email = user_data.get("email")
    password = user_data.get("password")
    role = user_data.get("role", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not role:
        raise HTTPException(status_code=400, detail="Role is required")


    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        # Update role if different
        if existing_user.get("role") != role:
            users_collection.update_one({"email": email}, {"$set": {"role": role}})
        return {"status": "success", "user": {"email": email, "role": existing_user.get("role")}}

    users_collection.insert_one({
        "uid": decoded_token["uid"],
        "email": email,
        "password": password or "",
        "role": role
    })

    print(f"Inserted user: {email} as {role}")

    return {"status": "success", "user": {"email": email, "role": role}}

@app.post("/api/founder-details")
async def add_founder_details(request: FastAPIRequest, data: FounderDetails):
    """Store founder profile details"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Firebase token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)
    uid = decoded_token["uid"]

    existing = founder_collection.find_one({"emailId": data.emailId})
    if existing:
        return {"message": "Founder profile already exists", "founder_id": str(existing["_id"])}

    founder_doc = data.dict()
    founder_doc["uid"] = uid
    founder_doc["role"] = "founder"
    founder_doc["createdAt"] = datetime.utcnow()

    result = founder_collection.insert_one(founder_doc)
    return {"message": "Founder details saved", "founder_id": str(result.inserted_id)}

@app.get("/api/founder/{email}")
def get_founder(email: str):
    """Fetch founder details"""
    founder = founder_collection.find_one({"emailId": email})
    if not founder:
        raise HTTPException(status_code=404, detail="Founder not found")
    founder["_id"] = str(founder["_id"])
    return founder

@app.post("/api/startup-details")
async def add_startup_details(request: FastAPIRequest, data: StartupDetails):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Firebase token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)
    uid = decoded_token["uid"]
    # email = decoded_token.get("email")  # Get email from logged-in user
    email = data.emailId
    print("Email",email)

    # Check if startup for this email already exists
    # existing = startup_collection.find_one({"emailId": email})
    # if existing:
    #     return {"message": "Startup already exists", "startup_id": str(existing["_id"])}

    # ✅ Check unique combination of founder + startupName
    normalized_name = normalize_name(data.startupName)
    # existing = startup_collection.find_one({"emailId": email, "startupName": data.startupName})
    # Check if startup already exists
    existing = startup_collection.find_one({
        "emailId": email,
        "startupName": {"$regex": f"^{normalized_name}$", "$options": "i"}
    })
    if existing:
        return {"message": "Startup already exists", "startup_id": str(existing["_id"])}

    startup_doc = data.dict()
    startup_doc["uid"] = uid
    startup_doc["startupName"] = normalized_name
    startup_doc["emailId"] = email  # auto-set from logged-in user
    startup_doc["createdAt"] = datetime.utcnow()


    result = startup_collection.insert_one(startup_doc)
    return {"message": "Startup details saved", "startup_id": str(result.inserted_id)}

# -------------------------
# Get Startup Details by Email
# -------------------------
# @app.get("/api/startup-details")
# def get_startup_details(request: FastAPIRequest):
#     auth_header = request.headers.get("Authorization")
#     if not auth_header or not auth_header.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Missing Firebase token")

#     token = auth_header.split(" ")[1]
#     decoded_token = verify_firebase_token(token)
#     email = decoded_token.get("email")  # Get email from logged-in user

#     startup = startup_collection.find_one({"emailId": email})
#     if not startup:
#         raise HTTPException(status_code=404, detail="Startup not found")

#     startup["_id"] = str(startup["_id"])
#     return startup


@app.get("/api/startup-details")
def get_startup_details(request: FastAPIRequest):
    auth_header = request.headers.get("Authorization")
    print(">>> Auth Header Received:", auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Firebase token")

    token = auth_header.split(" ")[1]
    decoded_token = verify_firebase_token(token)
    email = decoded_token.get("email")  # Get email of logged-in founder

    startups = list(startup_collection.find({"emailId": email}))  # ✅ Fetch ALL startups

    if not startups:
        return []  # Return empty list if none yet

    # Convert ObjectId → string
    for s in startups:
        s["_id"] = str(s["_id"])

    return startups  # ✅ return list

@app.get("/api/startups")
def get_startups():
    startups = list(startup_collection.find({}, {"_id": 0}))
    return startups

# ------------------ Create Meeting ------------------
@app.post("/api/meetings")
def create_meeting(meeting: MeetingRequest):
    if not check_investor_interest(meeting.founderEmail, meeting.investorEmail):
        raise HTTPException(status_code=403, detail="Investor not allowed to request meeting")

    if check_time_conflict(meeting.founderEmail, meeting.proposedDateTime) or \
       check_time_conflict(meeting.investorEmail, meeting.proposedDateTime):
        raise HTTPException(status_code=409, detail="Meeting time conflicts with another meeting")

    meeting_end = meeting.proposedDateTime + timedelta(minutes=30)

    meeting_doc = {
        "startupName": meeting.startupName,
        "founderEmail": meeting.founderEmail,
        "investorEmail": meeting.investorEmail,
        "proposedDateTime": meeting.proposedDateTime,
        "endTime": meeting_end,
        "status": "pending",
        "createdAt": datetime.utcnow()
    }

    # Insert into Meetings collection
    result = meetings_collection.insert_one(meeting_doc)
    meeting_id = result.inserted_id

    # Update FounderSlots — mark slot as "booked"
    slot_update = founder_slots_collection.update_one(
        {
            "founderEmail": meeting.founderEmail,
            "startTime": {"$lte": meeting.proposedDateTime},
            "endTime": {"$gt": meeting.proposedDateTime},
            "status": "available"
        },
        {"$set": {"status": "booked"}}
    )

     # Debug info (optional)
    if slot_update.modified_count == 0:
        print(f"⚠️ No matching available slot found for {meeting.founderEmail} at {meeting.proposedDateTime}")

    meeting_doc["_id"] = str(meeting_id)
    return {"message": "✅ Meeting created successfully", "meeting": meeting_doc}
    # meeting_doc = meeting.dict()




@app.post("/api/meetings/respond")
def respond_meeting(response: RespondMeeting):
    # Fetch the meeting
    meeting = meetings_collection.find_one({"_id": ObjectId(response.meetingId)})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if response.action == "accept":
        # Check time conflicts
        if check_time_conflict(meeting["founderEmail"], meeting["proposedDateTime"], exclude_meeting_id=response.meetingId) or \
           check_time_conflict(meeting["investorEmail"], meeting["proposedDateTime"], exclude_meeting_id=response.meetingId):
            raise HTTPException(status_code=409, detail="Meeting time conflicts with another meeting")

        # Get calendar service for founder only (organizer)
        founder_service = get_calendar_service(meeting["founderEmail"])

         # Set 30-min duration
        start_time = meeting["proposedDateTime"]
        end_time = meeting["proposedDateTime"] + timedelta(minutes=30)
        # Prepare Google Calendar event
        event_body = {
            'summary': f"Startup Meeting - {meeting['startupName']}",
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata'
            },
            'attendees': [{'email': meeting['investorEmail']}],
            'conferenceData': {
                'createRequest': {
                    'requestId': str(response.meetingId),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        # Insert event in founder's Google Calendar
        created_event = founder_service.events().insert(
            calendarId="primary",
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates="all"
        ).execute()

        hangout_link = created_event.get('hangoutLink')

        # Update Meetings table
        meetings_collection.update_one(
            {"_id": ObjectId(response.meetingId)},
            {"$set": {"status": "accepted", "hangoutLink": hangout_link, "endTime": end_time}}
        )

        # Update FounderSlots again if needed
        founder_slots_collection.update_one(
            {
                "founderEmail": meeting["founderEmail"],
                "startTime": {"$lte": start_time},
                "endTime": {"$gt": start_time}
            },
            {"$set": {"status": "booked"}}
        )

        return {"message": "✅ Meeting accepted and event added to calendar", "hangoutLink": hangout_link}

    elif response.action == "decline":
        meetings_collection.update_one(
            {"_id": ObjectId(response.meetingId)},
            {"$set": {"status": "declined"}}
        )

        # Free up the slot again
        founder_slots_collection.update_one(
            {
                "founderEmail": meeting["founderEmail"],
                "startTime": {"$lte": meeting["proposedDateTime"]},
                "endTime": {"$gt": meeting["proposedDateTime"]}
            },
            {"$set": {"status": "available"}}
        )

        return {"message": "Meeting declined and slot released"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    #     # Prepare event body
    #     event_body = {
    #         'summary': f"Startup Meeting - {meeting['startupName']}",
    #         'start': {
    #             'dateTime': meeting['proposedDateTime'].isoformat(),
    #             'timeZone': 'Asia/Kolkata'
    #         },
    #         'end': {
    #             'dateTime': (meeting['proposedDateTime'] + timedelta(hours=1)).isoformat(),
    #             'timeZone': 'Asia/Kolkata'
    #         },
    #         'attendees': [
    #             {'email': meeting['investorEmail']}  # only invite investor
    #         ],
    #         'conferenceData': {
    #             'createRequest': {
    #                 'requestId': str(response.meetingId),
    #                 'conferenceSolutionKey': {'type': 'hangoutsMeet'}
    #             }
    #         }
    #     }

    #     # Insert event in founder's calendar
    #     created_event = founder_service.events().insert(
    #         calendarId="primary",
    #         body=event_body,
    #         conferenceDataVersion=1,
    #         sendUpdates="all"  # sends invites to attendee
    #     ).execute()

    #     hangout_link = created_event.get('hangoutLink')

    #     # Update MongoDB meeting
    #     meetings_collection.update_one(
    #         {"_id": ObjectId(response.meetingId)},
    #         {"$set": {"status": "accepted", "hangoutLink": hangout_link}}
    #     )

    #     return {"message": "Meeting accepted", "hangoutLink": hangout_link}

    # elif response.action == "decline":
    #     meetings_collection.update_one(
    #         {"_id": ObjectId(response.meetingId)},
    #         {"$set": {"status": "declined"}}
    #     )
    #     return {"message": "Meeting declined"}

    # else:
    #     raise HTTPException(status_code=400, detail="Invalid action")

# ------------------ Fetch Meetings ------------------
@app.get("/api/meetings/founder/{founder_email}")
def get_founder_meetings(founder_email: str):
    meetings = list(meetings_collection.find({"founderEmail": founder_email}))
    for m in meetings:
        m["_id"] = str(m["_id"])
        m["proposedDateTime"] = m["proposedDateTime"].astimezone(pytz.UTC).isoformat()
        m["endTime"] = m["endTime"].astimezone(pytz.UTC).isoformat()
    
    return {"meetings": meetings}
    # for m in meetings:
    #     m["_id"] = str(m["_id"])
    # return meetings

@app.get("/api/meetings/investor/{investor_email}")
def get_investor_meetings(investor_email: str):
    meetings = list(meetings_collection.find({"investorEmail": investor_email}))
    for m in meetings:
        m["_id"] = str(m["_id"])
        m["proposedDateTime"] = m["proposedDateTime"].astimezone(pytz.UTC).isoformat()
        m["endTime"] = m["endTime"].astimezone(pytz.UTC).isoformat()
    
    return {"meetings": meetings}
    # for m in meetings:
    #     m["_id"] = str(m["_id"])
    # return meetings
# ----------------- Socket.IO Events -----------------
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# @sio.event
# async def join_room(sid, data):
#     """
#     User joins a room
#     data: { "participants": ["founderEmail", "investorEmail"] }
#     """
#     participants = sorted(data["participants"])  # sort to make room unique
#     room = "_".join(participants)
#     await sio.save_session(sid, {"room": room})
#     sio.enter_room(sid, room)
#     print(f"{sid} joined room {room}")

# @sio.event
# async def send_message(sid, data):
#     participants = sorted(data["participants"])
#     room = "_".join(participants)

#     # ✅ Store as datetime for MongoDB
#     message_doc = {
#         "senderId": data["senderId"],
#         "text": data["text"],
#         "timestamp": datetime.utcnow()  # <-- keep as datetime
#     }

#     # Save to MongoDB
#     chat_doc = chat_collection.find_one({"participants": participants})
#     if chat_doc:
#         chat_collection.update_one(
#             {"participants": participants},
#             {"$push": {"messages": message_doc}}
#         )
#     else:
#         chat_collection.insert_one({
#             "participants": participants,
#             "messages": [message_doc],
#             "createdAt": datetime.utcnow()
#         })

#     # ✅ Emit to clients (convert datetime to ISO string)
#     message_emit = message_doc.copy()
#     message_emit["timestamp"] = message_emit["timestamp"].isoformat()
#     await sio.emit("receive_message", message_emit, room=room)


# # ----------------- API to fetch chat history -----------------
# from typing import List
# from fastapi import Query


# @app.get("/api/chat/")
# def get_chat_history(participants: List[str] = Query(...)):
#     participants_sorted = sorted(participants)
#     chat = chat_collection.find_one({"participants": participants_sorted})
#     if chat:
#         chat["_id"] = str(chat["_id"])
#         for msg in chat["messages"]:
#             msg["timestamp"] = msg["timestamp"].isoformat()+ "Z" # convert datetime -> string
#         return chat
#     return {"participants": participants_sorted, "messages": []}


@sio.event
async def join_room(sid, data):
    """
    data: { "participants": ["founderEmail", "investorEmail"], "startupName": "StartupName" }
    """
    participants = sorted(data["participants"])
    startup_name = data.get("startupName", "unknown_startup")
    room = "_".join(participants + [startup_name])
    await sio.save_session(sid, {"room": room})
    sio.enter_room(sid, room)
    print(f"{sid} joined room {room}")


@sio.event
async def send_message(sid, data):
    participants = sorted(data["participants"])
    startup_name = data.get("startupName", "unknown_startup")
    room = "_".join(participants + [startup_name])

    message_doc = {
        "senderId": data["senderId"],
        "text": data["text"],
        "timestamp": datetime.utcnow()
    }

    # Save to MongoDB with startupName
    chat_doc = chat_collection.find_one({"participants": participants, "startupName": startup_name})
    if chat_doc:
        chat_collection.update_one(
            {"participants": participants, "startupName": startup_name},
            {"$push": {"messages": message_doc}}
        )
    else:
        chat_collection.insert_one({
            "participants": participants,
            "startupName": startup_name,
            "messages": [message_doc],
            "createdAt": datetime.utcnow()
        })

    message_emit = message_doc.copy()
    message_emit["timestamp"] = message_emit["timestamp"].isoformat()
    await sio.emit("receive_message", message_emit, room=room)


from typing import List
from fastapi import Query

@app.get("/api/chat/")
def get_chat_history(participants: List[str] = Query(...), startupName: str = Query(...)):
    participants_sorted = sorted(participants)
    chat = chat_collection.find_one({"participants": participants_sorted, "startupName": startupName})
    if chat:
        chat["_id"] = str(chat["_id"])
        for msg in chat["messages"]:
            msg["timestamp"] = msg["timestamp"].isoformat() + "Z"
        return chat
    return {"participants": participants_sorted, "messages": []}


# ----------------- Example MongoDB document -----------------
"""
Chats collection schema:

{
    "_id": ObjectId(),
    "participants": ["founder@example.com", "investor@example.com"],
    "messages": [
        {
            "senderId": "founder123",
            "text": "Hello, I’m interested in funding your startup",
            "timestamp": datetime.utcnow()
        },
        {
            "senderId": "investor456",
            "text": "Great! Let’s discuss further",
            "timestamp": datetime.utcnow()
        }
    ],
    "createdAt": datetime.utcnow()
}
"""

# --- POST: create interest ---
@app.post("/api/interests")
def create_interest(interest: Interest):
    existing = interests_collection.find_one({
        "startupName": interest.startupName,
        "founderEmail": interest.founderEmail,
        "investorEmail": interest.investorEmail
    })
    if existing:
        raise HTTPException(status_code=400, detail="Interest already exists")

    interest_data = interest.dict()
    if not interest_data.get("createdAt"):
        interest_data["createdAt"] = datetime.utcnow()
    result=interests_collection.insert_one(interest_data)
        # Add _id as string for JSON response
    interest_data["_id"] = str(result.inserted_id)

    return interest_data


@app.get("/api/interests")
def get_interests(investorEmail: str):
    records = list(interests_collection.find({"investorEmail": investorEmail}, {"_id": 0}))
    return records  # <-- returns array directly




# @app.post("/api/interests/accept")
# def accept_interest(data: AcceptInterest):
#     result = interests_collection.update_one(
#         {"founderEmail": data.founderEmail, "investorEmail": data.investorEmail},
#         {"$set": {"status": "accepted"}}
#     )

#     if result.matched_count == 0:
#         raise HTTPException(status_code=404, detail="Interest not found")

#     return {"message": "Interest accepted"}
@app.post("/api/interests/accept")
def accept_interest(data: AcceptInterest):
    result = interests_collection.update_one(
        {
            "founderEmail": data.founderEmail,
            "investorEmail": data.investorEmail,
            "startupName": data.startupName,  # ✅ Include startupName
        },
        {"$set": {"status": "accepted"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Interest not found for this startup")

    return {"message": "Interest accepted successfully"}



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

        sector_value = structured_data.get("sector", "Unknown")

        memo_payload = {
            "sector": sector_value,
            **analyses  # merge all agent analyses
        }

        
        # Prepare input for memo agent (all three analyses combined)

        memo_input = types.Content(
          role="user", 
          parts=[types.Part(text=json.dumps(memo_payload))]
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



async def emit_next_question(user_email,startup_name):
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
        normalized_startup_name = startup_name.strip().lower().replace(" ", "")
        print("&&&&&&&&&&&&&&&&&&&& final_agent_analyses &&&&&&&&&&&&&&&&",agent_analyses)
        
        # startup_name = final_data.get("startup_name", "")
        # Insert ALL data into BigQuery
        insert_success = await insert_into_bigquery(user_email, normalized_startup_name,final_data, agent_analyses)
        

        # # ✅ Insert / update MongoDB document with BigQuery data
        # db.StartupDetails.update_one(
        #     {"emailId": user_email, "startupName": startup_name},
        #     {
        #         "$set": {
        #             "bigqueryData": {
        #                 "financial_data": agent_analyses.get("financial_analysis"),
        #                 "team_data": agent_analyses.get("team_analysis"),
        #                 "market_data": agent_analyses.get("market_analysis"),
        #                 "first_memo": agent_analyses.get("investment_memo")
        #             },
        #             "updatedAt": datetime.utcnow()
        #         }
        #     },
            
        # )
        # normalized_startup_name = normalize_name(startup_name)
        # existing_doc = db.StartupDetails.find_one({"emailId": user_email, "startupName": startup_name})

        # Fetch the existing document (case + space insensitive)
        # existing_doc = db.StartupDetails.find_one({
        #     "emailId": user_email,
        #     "startupName": {"$regex": f"^{normalized_startup_name}$", "$options": "i"}
        # })
        existing_doc = db.StartupDetails.find_one({
            "emailId": user_email,
            "startupName": normalized_startup_name
        }) or {} 
        # update_fields = {
        #     "bigqueryData": {
        #         "financial_data": agent_analyses.get("financial_analysis"),
        #         "team_data": agent_analyses.get("team_analysis"),
        #         "market_data": agent_analyses.get("market_analysis"),
        #         "first_memo": agent_analyses.get("investment_memo")
        #     },
        #     "updatedAt": datetime.utcnow()
        # }
        update_fields = {
            "bigqueryData": {
                "financial_data": json.dumps(agent_analyses.get("financial_analysis")),
                "team_data": json.dumps(agent_analyses.get("team_analysis")),
                "market_data": json.dumps(agent_analyses.get("market_analysis")),
                "first_memo": json.dumps(agent_analyses.get("investment_memo"))
            },
            "updatedAt": datetime.utcnow()
        }

# Add missing required fields if not present
        required_fields = ["registeredName", "incorporationMonth", "incorporationYear", "about", "uid", "createdAt"]
        for field in required_fields:
            if field not in existing_doc:
                update_fields[field] = "" if field != "createdAt" else datetime.utcnow()

        # db.StartupDetails.update_one(
        #     {"emailId": user_email, "startupName": startup_name},
        #     {"$set": update_fields}
        # )

        # Update the MongoDB document
        db.StartupDetails.update_one(
            {
                "emailId": user_email,
                "startupName": normalized_startup_name
            },
            {"$set": update_fields},
            upsert=True
        )

        # Send success message to frontend with all analyses
        await sio.emit("final_json", {
            "status": "success", 
            "message": "Startup details updated successfully",
            "analyses": agent_analyses,
            "investment_memo": agent_analyses.get("investment_memo", {}),
            "bigquery_success": insert_success
        }, room=user_email)



async def validate_and_prepare_bq_data(user_email: str, startup_name: str,structured_data: Dict[str, Any], agent_analyses: Dict[str, Any]) -> Dict[str, Any]:
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
    
    normalized_startup_name = startup_name.strip().lower().replace(" ", "")

    # Validate required fields
    if not user_email:
        raise ValueError("user_email is required")
    if not startup_name:
        raise ValueError("startup_name is required")
    
    # Prepare the record with proper error handling
    record = {
        "founder_email": user_email,
        "startup_name": normalized_startup_name,
        "data": safe_json_dumps(structured_data),
        "created_at": datetime.utcnow().isoformat(),
        "financial_data": safe_json_dumps(agent_analyses.get("financial_analysis")),
        "team_data": safe_json_dumps(agent_analyses.get("team_analysis")),
        "market_data": safe_json_dumps(agent_analyses.get("market_analysis")),
        "first_memo": safe_json_dumps(agent_analyses.get("investment_memo"))
    }
    
    # Log the data being inserted (without sensitive info)
    logger.info(f"Preparing to insert data for {user_email}")
    logger.info(f"Data keys: {list(record.keys())}")
    
    return record

async def insert_into_bigquery(user_email: str, startup_name: str,structured_data: Dict[str, Any], agent_analyses: Dict[str, Any]):
    """Insert all analysis data into BigQuery with enhanced error handling"""
    
    try:
        normalized_startup_name = startup_name.strip().lower().replace(" ", "")

        # Prepare the data
        record = await validate_and_prepare_bq_data(user_email, normalized_startup_name,structured_data, agent_analyses)
        
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
# @app.post("/upload-and-analyze")
# async def upload_and_analyze(files: list[UploadFile], user_email: str = Form(...)):
#     file_paths = []
#     bucket = storage_client.bucket(BUCKET_NAME)
#     for file in files:
#         blob_name = f"{user_email}/{file.filename}"
#         blob = bucket.blob(blob_name)
#         with tempfile.NamedTemporaryFile(delete=False) as tmp:
#             tmp.write(await file.read())
#             tmp_path = tmp.name
#         blob.upload_from_filename(tmp_path)
#         os.remove(tmp_path)
#         file_paths.append(blob_name)

#     req = DocRequest(bucket_name=BUCKET_NAME, file_paths=file_paths)
#     content = types.Content(role="user", parts=[types.Part(text=req.json())])

#     # Run root agent
#     runner_root = adk.Runner(agent=root_agent, app_name=app_name, session_service=session_service)
#     root_output = None
#     async for event in runner_root.run_async(user_id=user_id, session_id=session_id, new_message=content):
#         if event.is_final_response():
#             root_output = event.content

#     # Run question agent
#     runner_q = adk.Runner(agent=question_agent, app_name=app_name, session_service=session_service)
#     question_output = None
#     async for event in runner_q.run_async(user_id=user_id, session_id=session_id, new_message=root_output):
#         if event.is_final_response():
#             question_output = event.content

#     await filler_agent.run(question_output)

#     # If client already connected, emit immediately, else mark pending
#     if sio.manager.rooms.get(user_email):
#         await emit_next_question(user_email)
#     else:
#         pending_first_questions[user_email] = True

#     return JSONResponse({"status": "ok", "message": "Files uploaded and analysis started."})

from typing import List
from fastapi import UploadFile, File, Form
from urllib.parse import quote
@app.post("/upload-and-analyze")
async def upload_and_analyze(
    files: List[UploadFile] = File(...),
    emailId: str = Form(...),
    startupName: str = Form(...)
):
    # normalized_name = normalize_name(startupName)
    # startupName=startupName.lower()
    normalized_startup_name = startupName.strip().lower().replace(" ", "")
    bucket = storage_client.bucket(BUCKET_NAME)
    file_paths = []
    uploaded_files_info = []

    # ✅ Upload files to GCS under: emailId/startupName/<file>
    for file in files:
        blob_name = f"{emailId}/{normalized_startup_name}/{file.filename}"
        blob = bucket.blob(blob_name)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        blob.upload_from_filename(tmp_path)
        os.remove(tmp_path)

        file_paths.append(blob_name)

        # URL-encode the blob name for public URL
        encoded_blob_name = quote(blob_name)

        uploaded_files_info.append({
            "fileName": file.filename,
            "gcsUrl": f"https://storage.googleapis.com/{BUCKET_NAME}/{encoded_blob_name}"
        })

    # existing_doc = db.StartupDetails.find_one({"emailId": emailId, "startupName": startupName})

    # ✅ Fetch existing document using normalized name
    existing_doc = db.StartupDetails.find_one({
        "emailId": emailId,
        "startupName": normalized_startup_name
    })
    
    created_at = existing_doc["createdAt"] if existing_doc else datetime.utcnow()
    registered_name = existing_doc.get("registeredName", startupName) if existing_doc else startupName
    inc_month = existing_doc.get("incorporationMonth", "") if existing_doc else ""
    inc_year = existing_doc.get("incorporationYear", "") if existing_doc else ""
    about_text = existing_doc.get("about", "") if existing_doc else ""
    uid_val = existing_doc.get("uid", "") if existing_doc else ""


    # ✅ Store file metadata in MongoDB
    # db.StartupDetails.update_one(
    #     {"emailId": emailId, "startupName": startupName},
    #     {
    #         "$push": {"uploadedFiles": {"$each": uploaded_files_info}},
    #         "$set": {"updatedAt": datetime.utcnow()}
    #     },
    #     upsert=True  # ✅ THIS IS THE IMPORTANT FIX
        
    # )

    # db.StartupDetails.update_one(
    # {"emailId": emailId, "startupName": startupName},
    # {
    #     "$push": {"uploadedFiles": {"$each": uploaded_files_info}},
    #     "$set": {
    #         "updatedAt": datetime.utcnow(),
    #         "createdAt": created_at,
    #         "registeredName": registered_name,
    #         "incorporationMonth": inc_month,
    #         "incorporationYear": inc_year,
    #         "about": about_text,
    #         "uid": uid_val
    #     }
    # },
#     # upsert=True
# )
    # ✅ Update MongoDB with uploaded files and maintain required fields
    db.StartupDetails.update_one(
        {"emailId": emailId, "startupName": startupName},
        {
            "$push": {"uploadedFiles": {"$each": uploaded_files_info}},
            "$set": {
                "updatedAt": datetime.utcnow(),
                "createdAt": created_at,
                "registeredName": registered_name,
                "incorporationMonth": inc_month,
                "incorporationYear": inc_year,
                "about": about_text,
                "uid": uid_val
            }
        },
        upsert=True
    )


    # -------------------- AI AGENT EXECUTION --------------------

    req = DocRequest(bucket_name=BUCKET_NAME, file_paths=file_paths)
    content = types.Content(role="user", parts=[types.Part(text=req.json())])

    runner_root = adk.Runner(agent=root_agent, app_name=app_name, session_service=session_service)
    root_output = None
    async for event in runner_root.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            root_output = event.content

    runner_q = adk.Runner(agent=question_agent, app_name=app_name, session_service=session_service)
    question_output = None
    async for event in runner_q.run_async(user_id=user_id, session_id=session_id, new_message=root_output):
        if event.is_final_response():
            question_output = event.content

    await filler_agent.run(question_output)

    # ✅ If founder already connected to socket, emit question immediately
    if sio.manager.rooms.get(emailId):
        await emit_next_question(emailId, normalized_startup_name)
    else:
        pending_first_questions[emailId] = {"startup_name": normalized_startup_name}

    return JSONResponse({"status": "ok", "message": "Files uploaded & voice agent is preparing questions."})

# ===== Socket.IO Events =====
@sio.event
async def connect(sid, environ, auth):
    user_email = auth.get("user_email") if auth else None
    print(f"Client connected: {sid}, auth: {auth}")
    if user_email:
        await sio.enter_room(sid, user_email)
        # If a first question is pending, emit now
        if pending_first_questions.get(user_email):
            startup_info = pending_first_questions.pop(user_email)
            startup_name = startup_info.get("startup_name", "Unknown")
            await emit_next_question(user_email, startup_name)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)

@sio.on("answer")
async def receive_answer(sid, data):
    answer = data.get("answer")
    user_email = data.get("user_email")
    key = data.get("key")
    startup_name = data.get("startup_name")  # may be None

    if not answer or not user_email or not key:
        return

    # fallback if startup_name is None
    if not startup_name:
        startup_name = "Unknown"

    normalized = startup_name.strip().lower().replace(" ", "")

    fill_json(filler_agent.structured_json, key, answer)
    filler_agent.questions.pop(key, None)
    await emit_next_question(user_email, normalized)
