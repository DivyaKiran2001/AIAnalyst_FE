import re
from google.cloud import bigquery
from Backend.tools.web_search_tool import WebSearchTool
from datetime import datetime


def financial_analysis(structured_data: dict) -> dict:
    """
    Tool to calculate financial metrics and perform benchmarking.
    """

    def extract_number(value) -> float:
        """Extract numeric value from string or number"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = re.sub(r'[^\d.]', '', value)
            return float(cleaned) if cleaned else None
        return None

    def calculate_metrics(financials: dict, traction: dict) -> dict:
        """Calculate ALL key financial metrics using available data"""
        print("Calculate key financial metrics")
        metrics = {}

        # Extract all available data
        revenue = extract_number(financials.get("revenue"))
        current_mrr = extract_number(traction.get("current_mrr"))
        ask_amount = extract_number(financials.get("ask_amount"))
        equity_offered = extract_number(financials.get("equity_offered"))
        burn_rate = extract_number(financials.get("burn_rate"))
        monthly_expenses = extract_number(financials.get("monthly_expenses"))
        cash_balance = extract_number(financials.get("cash_balance"))
        marketing_spend = extract_number(financials.get("marketing_spend"))
        
        # Traction data for CAC/LTV calculations
        new_customers = extract_number(traction.get("new_customers_this_month"))
        avg_subscription_price = extract_number(traction.get("average_subscription_price"))
        customer_lifespan = extract_number(traction.get("customer_lifespan_months"))
        active_customers = extract_number(traction.get("active_customers"))

        # 1. REVENUE METRICS
        # Annual Revenue
        if current_mrr:
            metrics["annual_revenue"] = current_mrr * 12
        elif revenue:
            metrics["annual_revenue"] = revenue

        # 2. VALUATION METRICS
        # Implied Valuation
        if ask_amount and equity_offered and equity_offered > 0:
            metrics["implied_valuation"] = ask_amount / (equity_offered / 100)

        # Valuation Multiple
        if metrics.get("implied_valuation") and metrics.get("annual_revenue"):
            metrics["revenue_multiple"] = metrics["implied_valuation"] / metrics["annual_revenue"]

        # 3. BURN & RUNWAY METRICS (IMPROVED)
        # Monthly Net Burn (more accurate than just burn_rate)
        if monthly_expenses and current_mrr:
            metrics["monthly_net_burn"] = monthly_expenses - current_mrr
        elif burn_rate:
            metrics["monthly_net_burn"] = burn_rate
        elif monthly_expenses:
            metrics["monthly_net_burn"] = monthly_expenses  # Assume no revenue

        # Runway calculation (using actual cash balance)
        if cash_balance and metrics.get("monthly_net_burn") and metrics["monthly_net_burn"] > 0:
            metrics["runway_months"] = cash_balance / metrics["monthly_net_burn"]
        elif burn_rate and burn_rate > 0:
            # Fallback: assume cash balance based on ask amount
            assumed_cash = ask_amount * 2 if ask_amount else 100000
            metrics["runway_months"] = assumed_cash / burn_rate

        # 4. CUSTOMER ECONOMICS METRICS (NEW)
        # Customer Acquisition Cost (CAC)
        if marketing_spend and new_customers and new_customers > 0:
            metrics["cac"] = marketing_spend / new_customers

        # Lifetime Value (LTV)
        if avg_subscription_price and customer_lifespan:
            metrics["ltv"] = avg_subscription_price * customer_lifespan

        # LTV to CAC Ratio (Golden Metric)
        if metrics.get("ltv") and metrics.get("cac") and metrics["cac"] > 0:
            metrics["ltv_cac_ratio"] = metrics["ltv"] / metrics["cac"]

        # 5. EFFICIENCY METRICS (NEW)
        # Marketing Efficiency
        if marketing_spend and current_mrr:
            metrics["marketing_efficiency"] = current_mrr / marketing_spend if marketing_spend > 0 else None

        # Customer Growth Rate
        if active_customers and new_customers:
            metrics["customer_growth_rate"] = (new_customers / active_customers) * 100 if active_customers > 0 else None

        # 6. UNIT ECONOMICS (NEW)
        # Average Revenue Per User (ARPU)
        if current_mrr and active_customers and active_customers > 0:
            metrics["arpu"] = current_mrr / active_customers

        print(f"Calculated metrics: {metrics}")
        return metrics

    # def get_industry_benchmarks(data: dict) -> dict:
    #     """Get industry benchmarks (simulated)"""
    #     return {
    #         "avg_revenue_multiple": 6.0,
    #         "avg_ltv_cac_ratio": 3.5,
    #         "acceptable_burn_rate": 50000,
    #         "typical_runway": 18,
    #         "seed_stage_valuation_range": {"min": 500000, "max": 5000000},
    #     }

    def insert_benchmarks_into_bigquery(sector: str, stage: str, benchmarks: dict) -> bool:
        """Insert new benchmarks into BigQuery table"""
        print("Insert new benchmarks into BigQuery table")
        try:
            client = bigquery.Client()
            
            table_id = "intense-subject-470817-v2.startup_benchmarks.industry_benchmarks"
            
            rows_to_insert = [{
                "sector": sector,
                "stage": stage,
                "avg_revenue_multiple": benchmarks.get("avg_revenue_multiple", 6.0),
                "avg_ltv_cac_ratio": benchmarks.get("avg_ltv_cac_ratio", 3.5),
                "acceptable_burn_rate": benchmarks.get("acceptable_burn_rate", 50000),
                "typical_runway": benchmarks.get("typical_runway", 18),
                "min_valuation": benchmarks.get("seed_stage_valuation_range", {}).get("min", 500000),
                "max_valuation": benchmarks.get("seed_stage_valuation_range", {}).get("max", 5000000),
                "data_source": benchmarks.get("data_source", "web_search"),
                "last_updated": datetime.utcnow().isoformat()
            }]
            
            errors = client.insert_rows_json(table_id, rows_to_insert)
            
            if errors:
                print(f"Errors inserting into BigQuery: {errors}")
                return False
            else:
                print(f"Successfully inserted benchmarks for {sector} - {stage}")
                return True
                
        except Exception as e:
            print(f"Failed to insert into BigQuery: {e}")
            return False

    def get_industry_benchmarks_from_bigquery(sector: str, stage: str) -> dict:
        """Get industry benchmarks from BigQuery table (sector+stage or sector-only average)"""
        print("Get industry benchmarks from BigQuery table")
        try:
            client = bigquery.Client()

            # ✅ Step 1: Check if (sector, stage) exists
            check_query = f"""
            SELECT COUNT(*) as record_count
            FROM `intense-subject-470817-v2.startup_benchmarks.vw_industry_benchmarks`
            WHERE sector = '{sector}' AND stage = '{stage}'
            """
            check_job = client.query(check_query)
            check_result = list(check_job)

            if check_result and check_result[0].record_count > 0:
                # Case 1: Exact sector + stage match
                query = f"""
                SELECT 
                    avg_revenue_multiple,
                    avg_ltv_cac_ratio,
                    acceptable_burn_rate,
                    typical_runway,
                    seed_stage_valuation_range
                FROM `intense-subject-470817-v2.startup_benchmarks.vw_industry_benchmarks`
                WHERE sector = '{sector}' AND stage = '{stage}'
                LIMIT 1
                """
                query_job = client.query(query)
                results = list(query_job)

                if not results:
                    return None

                row = results[0]

                # Extract valuation range from STRUCT
                valuation_range = {"min": 500000, "max": 5000000}
                if (hasattr(row, 'seed_stage_valuation_range') and 
                    row.seed_stage_valuation_range and
                    hasattr(row.seed_stage_valuation_range, 'min') and
                    hasattr(row.seed_stage_valuation_range, 'max')):
                    min_val = row.seed_stage_valuation_range.min
                    max_val = row.seed_stage_valuation_range.max
                    if min_val is not None and max_val is not None:
                        valuation_range = {"min": float(min_val), "max": float(max_val)}

                return {
                    "avg_revenue_multiple": float(row.avg_revenue_multiple),
                    "avg_ltv_cac_ratio": float(row.avg_ltv_cac_ratio),
                    "acceptable_burn_rate": float(row.acceptable_burn_rate),
                    "typical_runway": float(row.typical_runway),
                    "seed_stage_valuation_range": valuation_range,
                    "data_source": "bigquery_exact_match"
                }
            else:
                return None
            # else:
                # Case 2: No exact stage match → fallback to sector averages
                # Query the underlying table to get valuation ranges
                # query = f"""
                # SELECT 
                #     AVG(avg_revenue_multiple) as avg_revenue_multiple,
                #     AVG(avg_ltv_cac_ratio) as avg_ltv_cac_ratio,
                #     AVG(acceptable_burn_rate) as acceptable_burn_rate,
                #     AVG(typical_runway) as typical_runway,
                #     AVG(min_valuation) as avg_min_valuation,
                #     AVG(max_valuation) as avg_max_valuation
                # FROM `ai-analyst-poc-474306.startup_benchmarks.industry_benchmarks`
                # WHERE sector = '{sector}'
                # """
                # query_job = client.query(query)
                # results = list(query_job)

                # if not results:
                #     return None

                # row = results[0]

                # # Calculate average valuation range
                # valuation_range = {
                #     "min": float(row.avg_min_valuation) if row.avg_min_valuation else 500000,
                #     "max": float(row.avg_max_valuation) if row.avg_max_valuation else 5000000
                # }

                # return {
                #     "avg_revenue_multiple": float(row.avg_revenue_multiple) if row.avg_revenue_multiple else 6.0,
                #     "avg_ltv_cac_ratio": float(row.avg_ltv_cac_ratio) if row.avg_ltv_cac_ratio else 3.5,
                #     "acceptable_burn_rate": float(row.acceptable_burn_rate) if row.acceptable_burn_rate else 50000,
                #     "typical_runway": float(row.typical_runway) if row.typical_runway else 18,
                #     "seed_stage_valuation_range": valuation_range,
                #     "data_source": "bigquery_sector_average"
                # }

        except Exception as e:
            print(f"BigQuery query failed: {e}")
            return None


    # def get_industry_benchmarks_simulated() -> dict:
    #     """Fallback simulated benchmarks"""
    #     return {
    #         "avg_revenue_multiple": 6.0,
    #         "avg_ltv_cac_ratio": 3.5,
    #         "acceptable_burn_rate": 50000,
    #         "typical_runway": 18,
    #         "seed_stage_valuation_range": {"min": 500000, "max": 5000000},
    #         "data_source": "simulated"
    #     }

    def get_industry_benchmarks(data: dict) -> dict:
        """Get industry benchmarks with web search fallback and auto-insertion"""
        # Extract sector and stage from data if available
        sector = data.get("sector")
        stage = data.get("stage", "seed")
        
        # Try BigQuery first with exact match
        benchmarks = get_industry_benchmarks_from_bigquery(sector, stage)
        print(f"benchmark.....................................{benchmarks}")
        if benchmarks is not None:
            benchmarks["query_context"] = {
                "sector_used": sector if sector else "not_provided",
                "stage_used": stage
            }
            return benchmarks
        
        # If still no data, use web search
        web_search_tool = WebSearchTool()
        web_benchmarks = web_search_tool.search_benchmarks(sector, stage)
         
        # Insert the web search results into BigQuery for future use
        #***********************************uncomment later*****************************
        # if sector and stage:
        #     insert_success = insert_benchmarks_into_bigquery(sector, stage, web_benchmarks)
        #     if insert_success:
        #         web_benchmarks["data_source"] = "web_search_inserted"
        #     else:
        #         web_benchmarks["data_source"] = "web_search_failed_insert"
        
        web_benchmarks["query_context"] = {
            "sector_used": sector if sector else "not_provided",
            "stage_used": stage,
            "benchmark_source": web_benchmarks.get("data_source", "web_search"),
            "confidence": web_benchmarks.get("confidence", "medium")
        }
        
        return web_benchmarks

    def generate_comprehensive_analysis(metrics: dict, benchmarks: dict) -> dict:
        """Generate comprehensive analysis using all metrics and benchmarks"""
        analysis = {
            "score_breakdown": {},
            "risk_factors": [],
            "strengths": [],
            "weaknesses": [],
            "final_score": 0,
            "verdict": "",
            "detailed_recommendation": ""
        }
        
        # Score individual metrics
        analysis["score_breakdown"] = _score_individual_metrics(metrics, benchmarks)
        
        # Identify strengths and weaknesses
        analysis.update(_identify_strengths_weaknesses(metrics, benchmarks))
        
        # Calculate final score
        analysis["final_score"] = _calculate_final_score(analysis["score_breakdown"])
        
        # Determine verdict
        analysis["verdict"] = _determine_verdict(analysis["final_score"], metrics, benchmarks)
        
        # Generate detailed recommendation
        analysis["detailed_recommendation"] = _generate_detailed_recommendation(metrics, benchmarks, analysis)
        
        return analysis

    def _score_individual_metrics(metrics: dict, benchmarks: dict) -> dict:
        """Score each metric on a 0-10 scale"""
        scores = {}
        
        # LTV:CAC RATIO (Most important)
        ltv_cac = metrics.get("ltv_cac_ratio")
        benchmark_ratio = benchmarks.get("avg_ltv_cac_ratio", 3.5)
        if ltv_cac:
            if ltv_cac >= 5.0:
                scores["ltv_cac_ratio"] = 10
            elif ltv_cac >= benchmark_ratio:
                scores["ltv_cac_ratio"] = 8
            elif ltv_cac >= 2.5:
                scores["ltv_cac_ratio"] = 6
            elif ltv_cac >= 1.5:
                scores["ltv_cac_ratio"] = 4
            else:
                scores["ltv_cac_ratio"] = 2
        else:
            scores["ltv_cac_ratio"] = 0
        

        # NEW: VALUATION RANGE SCORING
        implied_valuation = metrics.get("implied_valuation")
        valuation_range = benchmarks.get("seed_stage_valuation_range")
        
        if implied_valuation and valuation_range:
            min_val = valuation_range.get("min", 500000)
            max_val = valuation_range.get("max", 5000000)
            range_mid = (min_val + max_val) / 2
            
            # Score based on how close to the ideal range
            if min_val <= implied_valuation <= max_val:
                scores["valuation_range"] = 10
            elif implied_valuation <= min_val * 1.2:  # Up to 20% below min
                scores["valuation_range"] = 8
            elif implied_valuation <= max_val * 1.2:  # Up to 20% above max  
                scores["valuation_range"] = 6
            elif implied_valuation <= max_val * 1.5:  # Up to 50% above max
                scores["valuation_range"] = 4
            else:
                scores["valuation_range"] = 2
        else:
            scores["valuation_range"] = 0


        # RUNWAY
        runway = metrics.get("runway_months")
        benchmark_runway = benchmarks.get("typical_runway", 18)
        if runway:
            if runway >= 24:
                scores["runway"] = 10
            elif runway >= benchmark_runway:
                scores["runway"] = 8
            elif runway >= 12:
                scores["runway"] = 6
            elif runway >= 6:
                scores["runway"] = 4
            else:
                scores["runway"] = 2
        else:
            scores["runway"] = 0
        
        # REVENUE MULTIPLE
        multiple = metrics.get("revenue_multiple")
        benchmark_multiple = benchmarks.get("avg_revenue_multiple", 6.0)
        if multiple:
            # Lower multiple is better for investors
            if multiple <= benchmark_multiple * 0.8:
                scores["revenue_multiple"] = 10
            elif multiple <= benchmark_multiple:
                scores["revenue_multiple"] = 8
            elif multiple <= benchmark_multiple * 1.2:
                scores["revenue_multiple"] = 6
            elif multiple <= benchmark_multiple * 1.5:
                scores["revenue_multiple"] = 4
            else:
                scores["revenue_multiple"] = 2
        else:
            scores["revenue_multiple"] = 0
        
        # MONTHLY NET BURN
        burn_rate = abs(metrics.get("monthly_net_burn", 0))
        acceptable_burn = benchmarks.get("acceptable_burn_rate", 50000)
        if burn_rate:
            if burn_rate <= acceptable_burn * 0.5:
                scores["burn_efficiency"] = 10
            elif burn_rate <= acceptable_burn:
                scores["burn_efficiency"] = 8
            elif burn_rate <= acceptable_burn * 1.5:
                scores["burn_efficiency"] = 6
            elif burn_rate <= acceptable_burn * 2:
                scores["burn_efficiency"] = 4
            else:
                scores["burn_efficiency"] = 2
        else:
            scores["burn_efficiency"] = 0
        
        # CUSTOMER GROWTH
        growth_rate = metrics.get("customer_growth_rate")
        if growth_rate:
            if growth_rate >= 20:
                scores["growth_traction"] = 10
            elif growth_rate >= 10:
                scores["growth_traction"] = 8
            elif growth_rate >= 5:
                scores["growth_traction"] = 6
            elif growth_rate >= 2:
                scores["growth_traction"] = 4
            else:
                scores["growth_traction"] = 2
        else:
            scores["growth_traction"] = 0
        
        # MARKETING EFFICIENCY
        marketing_eff = metrics.get("marketing_efficiency")
        if marketing_eff:
            if marketing_eff >= 5.0:
                scores["marketing_efficiency"] = 10
            elif marketing_eff >= 3.0:
                scores["marketing_efficiency"] = 8
            elif marketing_eff >= 1.5:
                scores["marketing_efficiency"] = 6
            elif marketing_eff >= 1.0:
                scores["marketing_efficiency"] = 4
            else:
                scores["marketing_efficiency"] = 2
        else:
            scores["marketing_efficiency"] = 0
        
        return scores

    def _identify_strengths_weaknesses(metrics: dict, benchmarks: dict) -> dict:
        """Identify key strengths and weaknesses"""
        strengths = []
        weaknesses = []
        risk_factors = []
        
        # LTV:CAC Analysis
        ltv_cac = metrics.get("ltv_cac_ratio")
        benchmark_ratio = benchmarks.get("avg_ltv_cac_ratio", 3.5)
        if ltv_cac:
            if ltv_cac >= 5.0:
                strengths.append(f"Exceptional unit economics (LTV:CAC ratio of {ltv_cac:.1f})")
            elif ltv_cac >= benchmark_ratio:
                strengths.append(f"Strong unit economics (LTV:CAC ratio of {ltv_cac:.1f})")
            elif ltv_cac < 3.0:
                weaknesses.append(f"Weak unit economics (LTV:CAC ratio of {ltv_cac:.1f})")
                risk_factors.append("Low LTV:CAC ratio indicates poor customer acquisition efficiency")
        
        #VALUATION RANGE ANALYSIS
        implied_valuation = metrics.get("implied_valuation")
        valuation_range = benchmarks.get("seed_stage_valuation_range")
        
        if implied_valuation and valuation_range:
            min_val = valuation_range.get("min", 500000)
            max_val = valuation_range.get("max", 5000000)
            
            if implied_valuation < min_val:
                strengths.append(f"Conservative valuation (${implied_valuation:,.0f}) below typical seed range")
            elif implied_valuation <= max_val:
                strengths.append(f"Valuation (${implied_valuation:,.0f}) within typical seed stage range")
            else:
                weaknesses.append(f"Premium valuation (${implied_valuation:,.0f}) above typical seed range (${min_val:,.0f}-${max_val:,.0f})")
                risk_factors.append("Valuation may be inflated for seed stage")
        # Runway Analysis
        runway = metrics.get("runway_months")
        if runway:
            if runway >= 24:
                strengths.append(f"Comfortable cash runway of {runway:.1f} months")
            elif runway >= 18:
                strengths.append(f"Adequate runway of {runway:.1f} months")
            elif runway < 12:
                weaknesses.append(f"Short runway of {runway:.1f} months - urgent funding needed")
                risk_factors.append(f"Limited runway ({runway:.1f} months) creates execution risk")
            elif runway < 6:
                weaknesses.append(f"Critical runway situation: only {runway:.1f} months remaining")
                risk_factors.append("Critical cash runway situation")
        
        # Valuation Analysis
        multiple = metrics.get("revenue_multiple")
        benchmark_multiple = benchmarks.get("avg_revenue_multiple", 6.0)
        if multiple:
            if multiple <= benchmark_multiple:
                strengths.append(f"Reasonable valuation ({multiple:.1f}x revenue)")
            elif multiple <= benchmark_multiple * 1.3:
                strengths.append(f"Slightly premium valuation ({multiple:.1f}x revenue)")
            else:
                weaknesses.append(f"High valuation multiple ({multiple:.1f}x vs industry {benchmark_multiple:.1f}x)")
                risk_factors.append("Premium valuation requires exceptional growth justification")
        
        # Burn Rate Analysis
        burn_rate = abs(metrics.get("monthly_net_burn", 0))
        acceptable_burn = benchmarks.get("acceptable_burn_rate", 50000)
        if burn_rate > acceptable_burn * 1.5:
            weaknesses.append(f"High burn rate of ${burn_rate:,.0f}/month")
            risk_factors.append("High burn rate may indicate inefficient operations")
        
        # Growth Analysis
        growth_rate = metrics.get("customer_growth_rate")
        if growth_rate and growth_rate < 2:
            weaknesses.append(f"Slow customer growth ({growth_rate:.1f}% monthly)")
            risk_factors.append("Low growth rate may indicate product-market fit issues")
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "risk_factors": risk_factors
        }

    def _calculate_final_score(score_breakdown: dict) -> float:
        """Calculate weighted final score (0-10)"""
        weights = {
            "ltv_cac_ratio": 0.25,
            "runway": 0.20,
            "revenue_multiple": 0.10,  # Reduced from 0.15
            "valuation_range": 0.10,   # NEW: Add valuation range weight
            "burn_efficiency": 0.15,
            "growth_traction": 0.10,
            "marketing_efficiency": 0.10
        }
        
        total_score = 0
        total_weight = 0
        
        for metric, weight in weights.items():
            score = score_breakdown.get(metric, 0)
            total_score += score * weight
            total_weight += weight
        
        return round(total_score / total_weight, 2) if total_weight > 0 else 0

    def _determine_verdict(final_score: float, metrics: dict, benchmarks: dict) -> str:
        """Determine investment verdict based on score and critical metrics"""
        
        # Critical failure conditions
        runway = metrics.get("runway_months")
        ltv_cac = metrics.get("ltv_cac_ratio")
        
        if runway and runway < 3:
            return "FAIL - Critical Runway"
        if ltv_cac and ltv_cac < 1.0:
            return "FAIL - Poor Unit Economics"
        
        # NEW: Valuation range critical check
        implied_valuation = metrics.get("implied_valuation")
        valuation_range = benchmarks.get("seed_stage_valuation_range")
        if implied_valuation and valuation_range:
            max_val = valuation_range.get("max", 5000000)
            if implied_valuation > max_val * 1.5:  # 50% above max
                return "FAIL - Excessively Overvalued"

        # Score-based verdict
        if final_score >= 8.5:
            return "STRONG PASS"
        elif final_score >= 7.0:
            return "PASS"
        elif final_score >= 5.5:
            return "WEAK PASS"
        elif final_score >= 4.0:
            return "HOLD - Requires Significant Improvement"
        else:
            return "FAIL"

    def _generate_detailed_recommendation(metrics: dict, benchmarks: dict, analysis: dict) -> str:
        """Generate detailed investment recommendation"""
        recommendation_parts = []
        
        # Valuation Recommendation
        multiple = metrics.get("revenue_multiple")
        benchmark_multiple = benchmarks.get("avg_revenue_multiple", 6.0)
        if multiple:
            if multiple > benchmark_multiple * 1.5:
                recommendation_parts.append(f"Consider negotiating valuation down from {multiple:.1f}x to industry average of {benchmark_multiple:.1f}x")
            elif multiple > benchmark_multiple:
                recommendation_parts.append(f"Valuation is reasonable but at premium - ensure growth justifies multiple")
            else:
                recommendation_parts.append(f"Valuation appears attractive at {multiple:.1f}x revenue")
        
        # Runway Recommendation
        runway = metrics.get("runway_months")
        if runway:
            if runway < 12:
                recommendation_parts.append("Prioritize immediate funding round due to short runway")
            elif runway < 18:
                recommendation_parts.append("Initiate fundraising within next 3-6 months")
            else:
                recommendation_parts.append("Comfortable runway allows for strategic fundraising timing")
        
        # Unit Economics Recommendation
        ltv_cac = metrics.get("ltv_cac_ratio")
        if ltv_cac:
            if ltv_cac < 3.0:
                recommendation_parts.append("Focus on improving unit economics before scaling - reduce CAC or increase LTV")
            elif ltv_cac >= 5.0:
                recommendation_parts.append("Excellent unit economics - consider accelerating customer acquisition")
        
        # Growth Recommendation
        growth_rate = metrics.get("customer_growth_rate")
        if growth_rate and growth_rate < 5:
            recommendation_parts.append("Address growth bottlenecks before additional funding")
        
        # Final strategic recommendation
        verdict = analysis["verdict"]
        if "STRONG PASS" in verdict:
            recommendation_parts.append("RECOMMENDATION: Strong investment case - proceed with due diligence")
        elif "PASS" in verdict:
            recommendation_parts.append("RECOMMENDATION: Solid investment opportunity - proceed with standard due diligence")
        elif "WEAK PASS" in verdict:
            recommendation_parts.append("RECOMMENDATION: Marginal opportunity - conduct enhanced due diligence on key risk areas")
        elif "HOLD" in verdict:
            recommendation_parts.append("RECOMMENDATION: Monitor company progress and reconsider after improvements")
        else:
            recommendation_parts.append("RECOMMENDATION: Not suitable for investment at this time")
        
        return ". ".join(recommendation_parts)

    try:
        financials = structured_data.get("financials", {})
        traction = structured_data.get("traction", {})

        metrics = calculate_metrics(financials, traction)
        benchmarks = get_industry_benchmarks(structured_data)
         # Generate comprehensive analysis
        comprehensive_analysis = generate_comprehensive_analysis(metrics, benchmarks)

        return {
            "calculated_metrics": metrics,
            "industry_benchmarks": benchmarks,
            "investment_analysis": comprehensive_analysis
        }

    except Exception as e:
        return {"error": f"Financial analysis failed: {str(e)}"}