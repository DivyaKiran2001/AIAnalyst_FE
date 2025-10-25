import json
import logging
import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Optional,Any

load_dotenv(r"D:\GenAI_Exchange\AIAnalyst_FE\Backend\.env")


# ===== Logging Setup =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("team_risk_tool")

# ===== Web Search Configuration =====
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
GOOGLE_SEARCH_KEY = os.getenv('GOOGLE_SEARCH_KEY')
GOOGLE_SEARCH_Engine_Id = os.getenv('GOOGLE_SEARCH_Engine_Id')

class WebSearchClient:
    """Client for web search operations"""
    
    def __init__(self):
        self.newsapi_key = NEWSAPI_KEY
        self.google_key = GOOGLE_SEARCH_KEY
        self.google_search_engine_id = GOOGLE_SEARCH_Engine_Id
        self._session = None
    
    async def get_session(self):
        """Get or create a session"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def search_person_news(self, person_name: str, company_name: str) -> List[Dict]:
        """Search for news articles about a person"""
        if not self.newsapi_key:
            logger.warning("❌ NEWSAPI_KEY not configured")
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'"{person_name}"',
                'sortBy': 'relevancy',
                'pageSize': 3,
                'apiKey': self.newsapi_key,
                'language': 'en'
            }
            
            logger.info(f"📰 NewsAPI call: {person_name}")
            
            session = await self.get_session()
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    logger.info(f"✅ NewsAPI found {len(articles)} articles for {person_name}")
                    return articles
                else:
                    error_text = await response.text()
                    logger.error(f"❌ NewsAPI error {response.status}: {error_text}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ News search error for {person_name}: {e}")
            return []
    
    async def search_person_web(self, person_name: str, company_name: str) -> List[Dict]:
        """Search for general web information about a person"""
        if not self.google_key or not self.google_search_engine_id:
            logger.warning("❌ Google Search API not configured")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': f'"{person_name}" "{company_name}"',
                'key': self.google_key,
                'cx': self.google_search_engine_id,
                'num': 3
            }
            
            logger.info(f"🔍 Google Search API call: {person_name} at {company_name}")
            
            session = await self.get_session()
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    logger.info(f"✅ Google Search found {len(items)} results for {person_name}")
                    return items
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Google Search API error {response.status}: {error_text}")
                    # Try alternative search query
                    logger.info("🔄 Trying alternative search query...")
                    params['q'] = f'{person_name} {company_name}'
                    async with session.get(url, params=params, timeout=30) as retry_response:
                        if retry_response.status == 200:
                            data = await retry_response.json()
                            items = data.get('items', [])
                            logger.info(f"✅ Google Search (retry) found {len(items)} results")
                            return items
                        else:
                            retry_error = await retry_response.text()
                            logger.error(f"❌ Google Search retry error {retry_response.status}: {retry_error}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Web search error for {person_name}: {e}")
            return []
    
    async def get_person_web_data(self, person_name: str, company_name: str) -> Dict:
        """Get comprehensive web data for a person"""
        logger.info(f"🌐 Starting web search for: {person_name}")
        
        # Run both searches concurrently
        news_task = asyncio.create_task(self.search_person_news(person_name, company_name))
        web_task = asyncio.create_task(self.search_person_web(person_name, company_name))
        
        news_articles, web_results = await asyncio.gather(news_task, web_task, return_exceptions=True)
        
        # Handle exceptions
        if isinstance(news_articles, Exception):
            logger.error(f"❌ News search exception: {news_articles}")
            news_articles = []
        if isinstance(web_results, Exception):
            logger.error(f"❌ Web search exception: {web_results}")
            web_results = []
        
        # Analyze the results
        credibility_indicators = []
        
        # Check for professional indicators
        professional_keywords = ['linkedin', 'founder', 'ceo', 'cto', 'director', 'manager', 'experience', 'previous', 'speaker', 'coach']
        news_titles = ' '.join([article.get('title', '') for article in news_articles]).lower()
        web_snippets = ' '.join([result.get('snippet', '') for result in web_results]).lower()
        
        all_text = news_titles + ' ' + web_snippets
        
        for keyword in professional_keywords:
            if keyword in all_text:
                credibility_indicators.append(keyword)
        
        web_data = {
            'news_mentions': len(news_articles),
            'web_references': len(web_results),
            'credibility_indicators': credibility_indicators,
            'has_public_presence': len(news_articles) > 0 or len(web_results) > 0,
            'professional_score': min(len(credibility_indicators) * 20, 100),  # 0-100 scale
            'sample_news': [article.get('title', '') for article in news_articles[:2]] if news_articles else [],
            'sample_web': [result.get('title', '') for result in web_results[:2]] if web_results else []
        }
        
        logger.info(f"📊 Web data for {person_name}: {web_data['news_mentions']} news, {web_data['web_references']} web results")
        return web_data
    
    async def close(self):
        """Close the HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None

# ===== Initialize Web Search Client =====
web_client = WebSearchClient()

# ===== Enhanced Team Evaluation Tool =====
async def evaluate_team_tool(structured_json: Dict[str, Any]) -> str:
    """
    Enhanced tool with web search capabilities
    Takes structured JSON as input and extracts company_name and team_members
    """
    try:
        # Extract company_name from structured_json
        company_name = structured_json.get("startup_name", "")
        
        # Extract team data from structured_json
        team_data = structured_json.get("team", {})
        
        # Format team members into the required array structure
        team_members = []
        
        # Add CEO if present
        ceo_name = team_data.get("ceo")
        if ceo_name:
            team_members.append({"name": ceo_name, "role": "CEO"})
        
        # Add CTO if present
        cto_name = team_data.get("cto")
        if cto_name:
            team_members.append({"name": cto_name, "role": "CTO"})
        
        # Add other key members if present
        other_members = team_data.get("other_key_members", [])
        for member in other_members:
            if isinstance(member, str):
                # Parse member string (format: "Name - Role" or just "Name")
                if " - " in member:
                    name, role = member.split(" - ", 1)
                    team_members.append({"name": name.strip(), "role": role.strip()})
                else:
                    team_members.append({"name": member.strip(), "role": "Team Member"})
        
        logger.info(f"Evaluating team for {company_name} with {len(team_members)} members")
        
        if not team_members:
            return json.dumps({"error": "No team members found in the provided data"})
        
        logger.info("🔍 Starting web search analysis...")
        # Perform the analysis with web data
        analysis = await analyze_team_composition(company_name, team_members)

        logger.info("✅ Analysis completed with web data")
        return json.dumps(analysis)
        
    except Exception as e:
        logger.error(f"Team evaluation error: {e}")
        return json.dumps({"error": f"Team evaluation failed: {str(e)}"})

async def analyze_team_composition(company_name: str, team_members: List[Dict]) -> Dict:
    """
    Analyze team composition with web data
    """
    logger.info(f"Analyzing {len(team_members)} team members for {company_name}")
    
    # Get web data for all team members
    web_data = await gather_web_data(company_name, team_members)
    
    analysis = {
        "team_size_adequacy": analyze_team_size(team_members),
        "role_completeness": analyze_role_coverage(team_members),
        "web_presence": web_data,
        "founder_credibility": analyze_founder_credibility(team_members, web_data),
        "skill_gaps": identify_skill_gaps(team_members),
        "execution_risks": identify_execution_risks(team_members)
    }
    
    # Calculate overall scores
    analysis["scores"] = calculate_team_scores(analysis)
    analysis["recommendations"] = generate_recommendations(analysis)
    
    return {
        "team_assessment": {
            "company_name": company_name,
            "team_size": len(team_members),
            "overall_score": analysis["scores"]["overall_score"],
            "risk_level": analysis["execution_risks"]["risk_level"],
            "strengths": extract_strengths(analysis),
            "concerns": extract_concerns(analysis),
            "recommendations": analysis["recommendations"],
            "web_data_available": any(member_data['has_public_presence'] for member_data in web_data.values()),
            "detailed_analysis": analysis
        }
    }

async def gather_web_data(company_name: str, team_members: List[Dict]) -> Dict:
    """Gather web data for all team members"""
    web_data = {}
    
    for member in team_members:
        member_name = member.get('name', '')
        if member_name:
            logger.info(f"Searching web data for: {member_name}")
            member_web_data = await web_client.get_person_web_data(member_name, company_name)
            web_data[member_name] = member_web_data
        else:
            web_data[member_name] = {
                'news_mentions': 0,
                'web_references': 0,
                'credibility_indicators': [],
                'has_public_presence': False,
                'professional_score': 0,
                'sample_news': [],
                'sample_web': []
            }
    
    return web_data

def analyze_founder_credibility(team_members: List[Dict], web_data: Dict) -> Dict:
    """Analyze founder credibility based on web presence"""
    credibility_scores = []
    
    for member in team_members:
        member_name = member.get('name', '')
        member_web_data = web_data.get(member_name, {})
        
        credibility_score = member_web_data.get('professional_score', 0)
        
        # Adjust score based on role relevance
        role = member.get('role', '').lower()
        if any(keyword in role for keyword in ['founder', 'ceo', 'cto', 'director']):
            role_multiplier = 1.2
        else:
            role_multiplier = 1.0
            
        adjusted_score = min(credibility_score * role_multiplier, 100)
        
        credibility_scores.append({
            'name': member_name,
            'role': member.get('role', ''),
            'web_presence_score': adjusted_score,
            'news_mentions': member_web_data.get('news_mentions', 0),
            'web_references': member_web_data.get('web_references', 0),
            'credibility_indicators': member_web_data.get('credibility_indicators', []),
            'has_public_presence': member_web_data.get('has_public_presence', False)
        })
    
    avg_credibility = sum(score['web_presence_score'] for score in credibility_scores) / len(credibility_scores) if credibility_scores else 0
    
    return {
        'individual_scores': credibility_scores,
        'team_credibility_score': avg_credibility,
        'credibility_rating': 'HIGH' if avg_credibility >= 70 else 'MEDIUM' if avg_credibility >= 40 else 'LOW'
    }

def analyze_team_size(team_members: List[Dict]) -> Dict:
    """Analyze if team size is adequate for startup stage"""
    size = len(team_members)
    
    if size >= 3:
        rating = "EXCELLENT"
        rationale = "Ideal founding team size with role specialization"
    elif size == 2:
        rating = "GOOD" 
        rationale = "Standard founding team, should cover key roles"
    else:
        rating = "RISKY"
        rationale = "Single founder carries higher execution risk"
    
    return {
        "team_size": size,
        "rating": rating,
        "rationale": rationale
    }

def analyze_role_coverage(team_members: List[Dict]) -> Dict:
    """Analyze coverage of key startup roles"""
    roles = [member.get('role', '').lower() for member in team_members]
    
    key_roles = {
        "technical_lead": any(keyword in ' '.join(roles) for keyword in ['cto', 'technical', 'engineer', 'developer']),
        "business_lead": any(keyword in ' '.join(roles) for keyword in ['ceo', 'business', 'commercial', 'sales', 'marketing']),
        "product_lead": any(keyword in ' '.join(roles) for keyword in ['product', 'design', 'ux', 'ui']),
        "operations_lead": any(keyword in ' '.join(roles) for keyword in ['operations', 'coo', 'delivery'])
    }
    
    coverage_percentage = (sum(key_roles.values()) / len(key_roles)) * 100
    
    missing_roles = [role for role, covered in key_roles.items() if not covered]
    
    return {
        "key_roles_present": key_roles,
        "coverage_percentage": coverage_percentage,
        "missing_roles": missing_roles,
        "rating": "STRONG" if coverage_percentage >= 75 else "MODERATE" if coverage_percentage >= 50 else "WEAK"
    }

def identify_skill_gaps(team_members: List[Dict]) -> List[str]:
    """Identify potential skill gaps in the team"""
    gaps = []
    roles = [member.get('role', '').lower() for member in team_members]
    all_roles_text = ' '.join(roles)
    
    # Check for common startup skill gaps
    if not any(keyword in all_roles_text for keyword in ['technical', 'engineer', 'cto', 'developer']):
        gaps.append("TECHNICAL_LEADERSHIP: No clear technical expertise")
    
    if not any(keyword in all_roles_text for keyword in ['business', 'ceo', 'sales', 'marketing', 'commercial']):
        gaps.append("BUSINESS_LEADERSHIP: No clear business/commercial expertise")
    
    if len(team_members) < 2:
        gaps.append("TEAM_SIZE: Single founder may lack bandwidth for all functions")
    
    return gaps

def identify_execution_risks(team_members: List[Dict]) -> Dict:
    """Identify execution risks based on team composition"""
    risks = []
    risk_level = "LOW"
    
    # Single founder risk
    if len(team_members) == 1:
        risks.append("HIGH_RISK: Single founder - high execution burden")
        risk_level = "HIGH"
    
    # Role gap risks
    roles_text = ' '.join([member.get('role', '').lower() for member in team_members])
    technical_present = any(keyword in roles_text for keyword in ['technical', 'engineer', 'cto', 'developer'])
    business_present = any(keyword in roles_text for keyword in ['business', 'ceo', 'sales', 'marketing'])
    
    if not technical_present and not business_present:
        risks.append("HIGH_RISK: Missing both technical and business leadership")
        risk_level = "HIGH"
    elif not technical_present:
        risks.append("MEDIUM_RISK: Missing technical leadership")
        risk_level = max(risk_level, "MEDIUM")
    elif not business_present:
        risks.append("MEDIUM_RISK: Missing business leadership") 
        risk_level = max(risk_level, "MEDIUM")
    
    return {
        "risk_level": risk_level,
        "identified_risks": risks,
        "risk_score": {"HIGH": 75, "MEDIUM": 50, "LOW": 25}.get(risk_level, 25)
    }

def calculate_team_scores(analysis: Dict) -> Dict:
    """Calculate overall team scores including web credibility"""
    size_score = {"EXCELLENT": 90, "GOOD": 70, "RISKY": 30}[analysis["team_size_adequacy"]["rating"]]
    role_score = analysis["role_completeness"]["coverage_percentage"]
    credibility_score = analysis["founder_credibility"]["team_credibility_score"]
    risk_score = 100 - analysis["execution_risks"]["risk_score"]
    
    # Weighted average with credibility included
    overall_score = (size_score * 0.2 + role_score * 0.3 + credibility_score * 0.3 + risk_score * 0.2)
    
    return {
        "team_size_score": size_score,
        "role_coverage_score": role_score,
        "credibility_score": credibility_score,
        "risk_score": risk_score,
        "overall_score": round(overall_score, 1)
    }

def extract_strengths(analysis: Dict) -> List[str]:
    """Extract strengths from analysis including web data"""
    strengths = []
    
    if analysis["team_size_adequacy"]["rating"] in ["EXCELLENT", "GOOD"]:
        strengths.append(f"Strong team size: {analysis['team_size_adequacy']['rationale']}")
    
    if analysis["role_completeness"]["rating"] == "STRONG":
        strengths.append("Comprehensive role coverage across key functions")
    
    if analysis["founder_credibility"]["credibility_rating"] == "HIGH":
        strengths.append("Strong web presence and credibility indicators found")
    elif analysis["founder_credibility"]["credibility_rating"] == "MEDIUM":
        strengths.append("Moderate web presence with some credibility indicators")
    
    if analysis["execution_risks"]["risk_level"] == "LOW":
        strengths.append("Low execution risk based on team composition")
    
    # Add specific web-based strengths
    web_data = analysis.get("web_presence", {})
    for member_name, member_data in web_data.items():
        if member_data.get('has_public_presence', False):
            strengths.append(f"{member_name}: Public presence validated through web search")
    
    return strengths

def extract_concerns(analysis: Dict) -> List[str]:
    """Extract concerns from analysis"""
    concerns = []
    
    concerns.extend(analysis["skill_gaps"])
    concerns.extend(analysis["execution_risks"]["identified_risks"])
    
    # Add web-based concerns
    if analysis["founder_credibility"]["credibility_rating"] == "LOW":
        concerns.append("LIMITED_WEB_PRESENCE: Limited public information found about team members")
    
    web_data = analysis.get("web_presence", {})
    members_without_presence = [name for name, data in web_data.items() if not data.get('has_public_presence', False)]
    if members_without_presence:
        concerns.append(f"NO_WEB_PRESENCE: No public information found for: {', '.join(members_without_presence)}")
    
    return concerns

def generate_recommendations(analysis: Dict) -> List[str]:
    """Generate actionable recommendations based on analysis"""
    recommendations = []
    
    # Team size recommendations
    if analysis["team_size_adequacy"]["team_size"] == 1:
        recommendations.append("Consider bringing on a co-founder to share execution burden")
    
    # Role gap recommendations
    missing_roles = analysis["role_completeness"]["missing_roles"]
    for role in missing_roles:
        role_name = role.replace('_', ' ').title()
        recommendations.append(f"Consider adding {role_name} expertise through hiring or advisory board")
    
    # Web presence recommendations
    if analysis["founder_credibility"]["credibility_rating"] in ["LOW", "MEDIUM"]:
        recommendations.append("Build online presence through LinkedIn, industry publications, and speaking engagements")
        recommendations.append("Consider creating professional profiles on relevant platforms")
    
    # Risk mitigation recommendations
    if analysis["execution_risks"]["risk_level"] in ["HIGH", "MEDIUM"]:
        recommendations.append("Develop clear role definitions and accountability matrix")
        recommendations.append("Consider interim executives or advisors for missing expertise")
    
    return recommendations