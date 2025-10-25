from typing import List, Dict, Optional,Any
import json
import logging
import re
import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(r"D:\GenAI_Exchange\AIAnalyst_FE\Backend\.env")


# ===== Logging Setup =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("market_analyst_agent")

# ===== Configuration =====
GOOGLE_SEARCH_KEY = os.getenv('GOOGLE_SEARCH_KEY')
GOOGLE_SEARCH_Engine_Id = os.getenv('GOOGLE_SEARCH_Engine_Id')

# ===== Helper Functions (DEFINE THESE FIRST) =====
def extract_market_size_numbers(text: str) -> Dict:
    """Extract numerical values from market size claims"""
    patterns = {
        'billion': r'[\$]?([\d\.]+)\s*[Bb]illion',
        'million': r'[\$]?([\d\.]+)\s*[Mm]illion',
        'trillion': r'[\$]?([\d\.]+)\s*[Tt]rillion',
        'year': r'by\s*(\d{4})|in\s*(\d{4})'
    }
    
    extracted = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            clean_matches = []
            for match in matches:
                if isinstance(match, tuple):
                    clean_matches.extend([m for m in match if m])
                else:
                    clean_matches.append(match)
            extracted[key] = clean_matches[0] if clean_matches else None
    
    return extracted

def calculate_relevance(snippet: str, target_market: str) -> float:
    """Calculate relevance score between snippet and target market"""
    snippet_lower = snippet.lower()
    market_terms = target_market.lower().split()
    
    relevance = 0.0
    for term in market_terms:
        if term in snippet_lower:
            relevance += 0.2
    
    key_terms = ['market', 'size', 'growth', 'industry', 'report']
    for term in key_terms:
        if term in snippet_lower:
            relevance += 0.1
    
    return min(relevance, 1.0)

def calculate_validation_confidence(google_results: Dict, world_bank_data: Dict) -> int:
    """Calculate overall validation confidence score (0-100)"""
    confidence = 0
    
    if 'relevant_sources' in google_results:
        confidence += min(len(google_results['relevant_sources']) * 20, 60)
    
    if 'latest_data' in world_bank_data and world_bank_data['latest_data']:
        confidence += 20
    
    if 'error' in google_results or 'error' in world_bank_data:
        confidence = max(confidence - 20, 0)
    
    return min(confidence, 100)

def process_world_bank_response(data: Dict, target_market: str, relevant_indicator: str) -> Dict:
    """Process World Bank API response"""
    if not data or len(data) < 2:
        return {"info": "No data available from World Bank"}
    
    indicators = data[1]
    latest_data = []
    
    for item in indicators[:3]:
        if item.get('value'):
            latest_data.append({
                'year': item.get('date'),
                'value': item.get('value'),
                'indicator': item.get('indicator', {}).get('value', '')
            })
    
    # Determine trend
    trend = "stable/declining"
    if len(latest_data) > 1:
        try:
            if float(latest_data[0]['value']) > float(latest_data[-1]['value']):
                trend = "growing"
        except (ValueError, TypeError):
            pass
    
    return {
        "indicator": relevant_indicator,
        "latest_data": latest_data,
        "trend": trend
    }

def extract_competitors_from_search(search_results: List, target_market: str) -> Dict:
    """Extract competitor information from search results"""
    competitors = {"direct": [], "indirect": [], "key_players": []}
    
    for item in search_results:
        snippet = item.get('snippet', '').lower()
        title = item.get('title', '').lower()
        
        # Simple heuristic for competitor identification
        if any(term in snippet for term in ['competitor', 'competitive', 'vs', 'alternative']):
            competitors["direct"].append({
                'name': item.get('title'),
                'source': item.get('link'),
                'type': 'direct'
            })
        elif any(term in title for term in [target_market.lower(), 'market', 'industry']):
            competitors["key_players"].append({
                'name': item.get('title'),
                'source': item.get('link'),
                'type': 'key_player'
            })
        else:
            competitors["indirect"].append({
                'name': item.get('title'),
                'source': item.get('link'),
                'type': 'indirect'
            })
    
    return competitors

def process_trends_data(items: List) -> Dict:
    """Process trends data from search results"""
    trends = []
    
    for item in items:
        snippet = item.get('snippet', '')
        # Extract growth-related information
        if any(term in snippet.lower() for term in ['growth', 'increasing', 'rising', 'forecast']):
            trends.append({
                'source': item.get('title'),
                'trend_indication': snippet[:200],
                'confidence': 'high' if 'report' in item.get('title', '').lower() else 'medium'
            })
    
    return {
        "trends_found": len(trends),
        "trend_direction": "positive" if len(trends) > 2 else "neutral",
        "sources": trends
    }

def assess_competitive_intensity(competitors: Dict) -> str:
    """Assess competitive intensity based on competitor analysis"""
    total_competitors = len(competitors.get('direct', [])) + len(competitors.get('indirect', []))
    
    if total_competitors > 10:
        return "High competition"
    elif total_competitors > 5:
        return "Moderate competition"
    else:
        return "Low competition"

async def analyze_market_concentration(competitors: Dict) -> str:
    """Analyze market concentration level"""
    direct_competitors = len(competitors.get('direct', []))
    
    if direct_competitors == 0:
        return "Fragmented (no clear leaders)"
    elif direct_competitors < 5:
        return "Oligopolistic (few dominant players)"
    else:
        return "Competitive (many players)"

async def identify_growth_drivers(target_market: str) -> List:
    """Identify key growth drivers for the market"""
    common_drivers = {
        'technology': ['Digital adoption', 'Mobile penetration', 'IoT expansion'],
        'retail': ['E-commerce growth', 'Consumer spending', 'Urbanization'],
        'finance': ['Digital payments', 'Financial inclusion', 'Regulatory changes']
    }
    
    for sector, drivers in common_drivers.items():
        if sector in target_market.lower():
            return drivers
    
    return ['Market expansion', 'Consumer demand', 'Technological advancement']

def assess_market_maturity(target_market: str) -> str:
    """Assess market maturity level"""
    emerging_terms = ['tech', 'digital', 'ai', 'blockchain', 'edtech', 'fintech']
    mature_terms = ['retail', 'manufacturing', 'real estate', 'agriculture']
    
    if any(term in target_market.lower() for term in emerging_terms):
        return "Emerging"
    elif any(term in target_market.lower() for term in mature_terms):
        return "Mature"
    else:
        return "Growth"

async def fetch_industry_benchmarks(target_market: str) -> Dict:
    """Fetch industry-specific benchmarks"""
    return {
        "revenue": {
            "early_stage": "$1-5M ARR",
            "growth_stage": "$5-20M ARR",
            "mature": "$20M+ ARR"
        },
        "growth": {
            "early_stage": "100-200% YoY",
            "growth_stage": "50-100% YoY",
            "mature": "20-50% YoY"
        },
        "profitability": {
            "gross_margin": "60-80%",
            "net_margin": "10-20%",
            "cac_ratio": "1:3"
        }
    }

async def analyze_standard_kpis(target_market: str) -> List:
    """Analyze standard KPIs for the industry"""
    kpi_templates = {
        'ecommerce': ['CAC', 'LTV', 'Conversion Rate', 'AOV', 'Churn Rate'],
        'saas': ['MRR', 'ARR', 'Churn Rate', 'LTV:CAC', 'Net Retention'],
        'marketplace': ['GMV', 'Take Rate', 'Buyer/Seller Ratio', 'Network Effects']
    }
    
    for sector, kpis in kpi_templates.items():
        if sector in target_market.lower():
            return kpis
    
    return ['Revenue Growth', 'Customer Acquisition', 'Profit Margins', 'Market Share']

async def identify_market_risks(target_market: str) -> List:
    """Identify potential market risks"""
    common_risks = {
        'technology': ['Rapid obsolescence', 'Regulatory changes', 'Cybersecurity threats'],
        'retail': ['Economic downturns', 'Supply chain disruptions', 'Changing consumer preferences'],
        'finance': ['Regulatory compliance', 'Market volatility', 'Credit risks']
    }
    
    for sector, risks in common_risks.items():
        if sector in target_market.lower():
            return risks
    
    return ['Market competition', 'Economic factors', 'Regulatory environment']

async def identify_market_opportunities(target_market: str) -> List:
    """Identify market opportunities"""
    return [
        "Digital transformation initiatives",
        "Growing consumer demand",
        "Emerging market segments",
        "Technology enablement"
    ]

async def analyze_regulatory_factors(target_market: str) -> Dict:
    """Analyze regulatory factors affecting the market"""
    return {
        "regulatory_environment": "Moderate",
        "compliance_requirements": ["Data privacy", "Consumer protection"],
        "licensing_needs": ["Business registration", "Industry-specific licenses"]
    }

def assess_economic_sensitivity(target_market: str) -> str:
    """Assess how sensitive the market is to economic conditions"""
    sensitive_sectors = ['luxury', 'real estate', 'automotive', 'travel']
    resilient_sectors = ['healthcare', 'education', 'essential retail', 'utilities']
    
    if any(sector in target_market.lower() for sector in sensitive_sectors):
        return "High sensitivity to economic cycles"
    elif any(sector in target_market.lower() for sector in resilient_sectors):
        return "Resilient to economic cycles"
    else:
        return "Moderate sensitivity to economic cycles"

def estimate_adoption_curve(target_market: str) -> str:
    """Estimate technology adoption curve"""
    tech_heavy = ['ai', 'blockchain', 'iot', 'ar/vr', 'metaverse']
    if any(tech in target_market.lower() for tech in tech_heavy):
        return "Early Adopters"
    else:
        return "Early Majority"

def analyze_seasonality(target_market: str) -> Dict:
    """Analyze market seasonality patterns"""
    seasonal_patterns = {
        'retail': "High seasonality (Q4 peak)",
        'travel': "Seasonal variations",
        'education': "Academic year cycles",
        'default': "Moderate seasonality"
    }
    
    for pattern, description in seasonal_patterns.items():
        if pattern in target_market.lower():
            return {"pattern": description}
    
    return {"pattern": "Moderate seasonality"}

def get_current_timestamp() -> str:
    """Get current timestamp for report"""
    return datetime.now().isoformat()

def assess_market_potential(validation: Dict, trends: Dict) -> str:
    """Assess overall market potential"""
    confidence = validation.get("confidence_score", 0)
    trend_direction = trends.get("trend_direction", "neutral")
    
    if confidence >= 70 and trend_direction == "positive":
        return "High Potential"
    elif confidence >= 50:
        return "Moderate Potential"
    else:
        return "Needs Further Validation"

def generate_market_recommendations(results: Dict) -> List[str]:
    """Generate actionable recommendations based on analysis"""
    recommendations = []
    
    validation = results.get("market_validation", {})
    competition = results.get("competitive_analysis", {})
    risks = results.get("risk_assessment", {})
    
    if validation.get("confidence_score", 0) < 60:
        recommendations.append("Conduct deeper market size validation with primary research")
    
    if competition.get("competitive_intensity") == "High competition":
        recommendations.append("Focus on clear differentiation and unique value proposition")
    elif competition.get("competitive_intensity") == "Low competition":
        recommendations.append("Validate market demand and customer willingness to pay")
    
    if risks.get("market_risks"):
        recommendations.append("Develop risk mitigation strategies for identified market risks")
    
    recommendations.extend([
        "Validate assumptions with customer interviews",
        "Monitor key market indicators regularly",
        "Benchmark performance against industry standards"
    ])
    
    return recommendations

# ===== Session Management =====
class SessionManager:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self.session
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

# ===== Core Analysis Functions =====
async def google_market_validation(target_market: str, extracted_size: Dict, session: aiohttp.ClientSession) -> Dict:
    """Use Google Search to validate market claims"""
    if not GOOGLE_SEARCH_KEY or not GOOGLE_SEARCH_Engine_Id:
        return {"error": "Google API not configured"}
    
    try:
        queries = [
            f'"{target_market}" market size 2024',
            f'global {target_market} industry statistics',
            f'{target_market} TAM SAM SOM analysis',
            f'{target_market} market growth report'
        ]
        
        all_results = []
        for query in queries[:2]:  # Limit to save API calls
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_SEARCH_KEY,
                'cx': GOOGLE_SEARCH_Engine_Id,
                'q': query,
                'num': 3
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('items', []):
                        all_results.append({
                            'title': item.get('title'),
                            'link': item.get('link'),
                            'snippet': item.get('snippet'),
                            'relevance_score': calculate_relevance(item.get('snippet', ''), target_market)
                        })
        
        return {
            "sources_checked": len(all_results),
            "relevant_sources": [r for r in all_results if r['relevance_score'] > 0.3],
            "validation_queries": queries[:2]
        }
        
    except Exception as e:
        return {"error": str(e)}

async def world_bank_validation(target_market: str, session: aiohttp.ClientSession) -> Dict:
    """Use World Bank data for macroeconomic validation"""
    try:
        # Map common markets to World Bank indicators
        indicator_mapping = {
            'retail': 'NE.CON.PRVT.CD',
            'technology': 'IT.NET.USER.ZS',
            'ecommerce': 'IT.NET.USER.ZS',
            'automotive': 'IS.VEH.NVEH.P3',
            'finance': 'FS.AST.PRVT.GD.ZS',
            'healthcare': 'SH.XPD.CHEX.GD.ZS'
        }
        
        relevant_indicator = None
        for keyword, indicator in indicator_mapping.items():
            if keyword in target_market.lower():
                relevant_indicator = indicator
                break
        
        if not relevant_indicator:
            return {"info": "No specific World Bank indicator found for this market"}
        
        url = f"https://api.worldbank.org/v2/country/IND/indicator/{relevant_indicator}"
        params = {'format': 'json', 'date': '2020:2024', 'per_page': 5}
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return process_world_bank_response(data, target_market, relevant_indicator)
            else:
                return {"error": f"World Bank API returned status {response.status}"}
                    
    except Exception as e:
        return {"error": str(e)}

async def validate_market_size(claimed_size: str, target_market: str, session: aiohttp.ClientSession) -> Dict:
    """Validate market size claims using multiple data sources"""
    extracted_size = extract_market_size_numbers(claimed_size)
    
    # Run validation from multiple sources
    google_results = await google_market_validation(target_market, extracted_size, session)
    world_bank_data = await world_bank_validation(target_market, session)
    
    return {
        "claimed_size": claimed_size,
        "extracted_values": extracted_size,
        "google_validation": google_results,
        "world_bank_data": world_bank_data,
        "confidence_score": calculate_validation_confidence(google_results, world_bank_data)
    }

async def find_competitors(target_market: str, session: aiohttp.ClientSession) -> Dict:
    """Find direct and indirect competitors using Google Search"""
    if not GOOGLE_SEARCH_KEY or not GOOGLE_SEARCH_Engine_Id:
        return {"direct": [], "indirect": [], "key_players": []}
    
    try:
        queries = [
            f'"{target_market}" competitors',
            f'"{target_market}" similar companies',
            f'"{target_market}" market players'
        ]
        
        competitors = {"direct": [], "indirect": [], "key_players": []}
        
        for query in queries[:1]:  # Use first query only to save API calls
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_SEARCH_KEY,
                'cx': GOOGLE_SEARCH_Engine_Id,
                'q': query,
                'num': 5
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    competitors = extract_competitors_from_search(data.get('items', []), target_market)
                    break
                    
        return competitors
                    
    except Exception as e:
        logger.error(f"Competitor search error: {e}")
    
    return {"direct": [], "indirect": [], "key_players": []}

async def analyze_competitive_landscape(target_market: str, session: aiohttp.ClientSession) -> Dict:
    """Analyze competitors and market positioning"""
    competitors = await find_competitors(target_market, session)
    market_concentration = await analyze_market_concentration(competitors)
    
    return {
        "direct_competitors": competitors.get("direct", []),
        "indirect_competitors": competitors.get("indirect", []),
        "market_concentration": market_concentration,
        "key_players": competitors.get("key_players", []),
        "competitive_intensity": assess_competitive_intensity(competitors)
    }

async def google_trends_analysis(target_market: str, session: aiohttp.ClientSession) -> Dict:
    """Analyze market trends using Google Search"""
    if not GOOGLE_SEARCH_KEY or not GOOGLE_SEARCH_Engine_Id:
        return {"error": "Google API not configured"}
    
    try:
        query = f'"{target_market}" market trends 2024 growth forecast'
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_SEARCH_KEY,
            'cx': GOOGLE_SEARCH_Engine_Id,
            'q': query,
            'num': 3
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return process_trends_data(data.get('items', []))
            else:
                return {"error": "Failed to fetch trends data"}
                    
    except Exception as e:
        return {"error": str(e)}

async def analyze_growth_patterns(target_market: str) -> Dict:
    """Analyze market growth patterns"""
    return {
        "estimated_cagr": "8-12%",
        "growth_drivers": await identify_growth_drivers(target_market),
        "market_maturity": assess_market_maturity(target_market)
    }

async def analyze_market_trends(target_market: str, session: aiohttp.ClientSession) -> Dict:
    """Analyze current market trends and growth patterns"""
    trends_data = await google_trends_analysis(target_market, session)
    growth_patterns = await analyze_growth_patterns(target_market)
    
    return {
        "market_trends": trends_data,
        "growth_patterns": growth_patterns,
        "adoption_curve": estimate_adoption_curve(target_market),
        "seasonality": analyze_seasonality(target_market)
    }

async def get_industry_benchmarks(target_market: str) -> Dict:
    """Get industry-specific benchmarks and KPIs"""
    benchmarks = await fetch_industry_benchmarks(target_market)
    kpi_analysis = await analyze_standard_kpis(target_market)
    
    return {
        "revenue_benchmarks": benchmarks.get("revenue", {}),
        "growth_benchmarks": benchmarks.get("growth", {}),
        "kpi_standards": kpi_analysis,
        "profitability_metrics": benchmarks.get("profitability", {})
    }

async def assess_market_risks(target_market: str) -> Dict:
    """Assess market risks and opportunities"""
    risks = await identify_market_risks(target_market)
    opportunities = await identify_market_opportunities(target_market)
    
    return {
        "market_risks": risks,
        "growth_opportunities": opportunities,
        "regulatory_factors": await analyze_regulatory_factors(target_market),
        "economic_sensitivity": assess_economic_sensitivity(target_market)
    }

async def generate_market_report(claimed_size: str, target_market: str, results: Dict) -> Dict:
    """Generate final comprehensive market analysis report"""
    
    validation = results.get("market_validation", {})
    competition = results.get("competitive_analysis", {})
    trends = results.get("market_trends", {})
    benchmarks = results.get("industry_benchmarks", {})
    risks = results.get("risk_assessment", {})
    
    return {
        "executive_summary": {
            "market_claim": claimed_size,
            "validation_confidence": validation.get("confidence_score", 0),
            "competitive_intensity": competition.get("competitive_intensity", "Unknown"),
            "market_potential": assess_market_potential(validation, trends),
            "key_risks": risks.get("market_risks", [])[:3]
        },
        "market_validation": validation,
        "competitive_analysis": competition,
        "market_trends": trends,
        "industry_benchmarks": benchmarks,
        "risk_assessment": risks,
        "recommendations": generate_market_recommendations(results),
        "timestamp": get_current_timestamp()
    }

# ===== Main Analysis Function =====
async def perform_market_analysis(market_size_claim: str, target_market: str) -> Dict:
    """
    Perform comprehensive market analysis using free APIs
    """
    logger.info(f"Starting market analysis for: {target_market}")
    
    # Use session manager for all HTTP requests
    async with SessionManager() as session:
        # Run all analysis components
        results = {}
        
        try:
            results["market_validation"] = await validate_market_size(market_size_claim, target_market, session)
            logger.info("✅ market_validation completed")
        except Exception as e:
            logger.error(f"❌ market_validation failed: {e}")
            results["market_validation"] = {}
        
        try:
            results["competitive_analysis"] = await analyze_competitive_landscape(target_market, session)
            logger.info("✅ competitive_analysis completed")
        except Exception as e:
            logger.error(f"❌ competitive_analysis failed: {e}")
            results["competitive_analysis"] = {}
        
        try:
            results["market_trends"] = await analyze_market_trends(target_market, session)
            logger.info("✅ market_trends completed")
        except Exception as e:
            logger.error(f"❌ market_trends failed: {e}")
            results["market_trends"] = {}
        
        try:
            results["industry_benchmarks"] = await get_industry_benchmarks(target_market)
            logger.info("✅ industry_benchmarks completed")
        except Exception as e:
            logger.error(f"❌ industry_benchmarks failed: {e}")
            results["industry_benchmarks"] = {}
        
        try:
            results["risk_assessment"] = await assess_market_risks(target_market)
            logger.info("✅ risk_assessment completed")
        except Exception as e:
            logger.error(f"❌ risk_assessment failed: {e}")
            results["risk_assessment"] = {}
    
    # Generate final report
    return await generate_market_report(market_size_claim, target_market, results)

# ===== Market Analysis Tool =====
async def analyze_market_tool(structured_json: Dict[str, Any]) -> str:
    """
    Market Analysis Tool - Validates market claims and analyzes competitive landscape
    Takes structured JSON as input and extracts market_size_claim and target_market
    """
    try:
        # Extract market data from structured_json
        market_data = structured_json.get("market", {})
        
        # Extract market_size_claim and target_market
        market_size_claim = market_data.get("market_size_claim", "")
        target_market = market_data.get("target_market", "")
        
        logger.info(f"Analyzing market: {market_size_claim} for {target_market}")
        
        # Perform comprehensive market analysis
        analysis = await perform_market_analysis(market_size_claim, target_market)
        
        # Add context to the analysis result
        if isinstance(analysis, dict):
            analysis["analysis_context"] = {
                "startup_name": structured_json.get("startup_name", ""),
                "sector": structured_json.get("sector", ""),
                "stage": structured_json.get("stage", "")
            }
        
        return json.dumps(analysis)
        
    except Exception as e:
        logger.error(f"Market analysis error: {e}")
        return json.dumps({"error": f"Market analysis failed: {str(e)}"})