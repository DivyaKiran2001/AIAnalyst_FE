import os
import requests
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel

class WebSearchTool:
    """Tool to search for industry benchmarks online using real APIs"""
    
    def __init__(self):
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.google_search_key = os.getenv("GOOGLE_SEARCH_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_Engine_Id")

        # self.llm = ChatGoogleGenerativeAI(
        #     model="gemini-2.0-flash", temperature=0.2
        # )
        self.model = GenerativeModel("gemini-2.0-flash")
    
    # def search_benchmarks(self, sector: str, stage: str) -> dict:
    #     """
    #     Search for industry benchmarks using real APIs with fallback strategy
    #     """
    #     print("we are in websearch tool")
    #     benchmarks = {}
        
    #     # Try SerpAPI first (more comprehensive)
    #     if self.serpapi_key:
    #         serpapi_results = self._search_with_serpapi(sector, stage)
    #         print("serpapi_results#######################**********",serpapi_results)
    #         if serpapi_results and self._validate_benchmarks(serpapi_results, stage):
    #             benchmarks.update(serpapi_results)
    #             benchmarks["data_source"] = "serpapi"
        
    #     # If SerpAPI fails or no key, try Google Custom Search
    #     if not benchmarks and self.google_search_key and self.google_search_engine_id:
    #         google_results = self._search_with_google(sector, stage)
    #         print("google_results#######################**********",google_results)
    #         if google_results and self._validate_benchmarks(google_results, stage):
    #             benchmarks.update(google_results)
    #             benchmarks["data_source"] = "google_search"
        
    #     # If both APIs fail, use curated industry data
    #     # if not benchmarks:
    #     #     benchmarks = self._get_curated_benchmarks(sector, stage)
    #     #     benchmarks["data_source"] = "curated_fallback"
    #     print("web_serach_benchmarks",benchmarks)
    #     return benchmarks


    def search_benchmarks(self, sector: str, stage: str) -> dict:
        """Search for industry benchmarks with fallback strategy"""
        print("🔍 Starting web search for benchmarks")
        benchmarks = {}
        
        # Try SerpAPI first
        if self.serpapi_key:
            serpapi_results = self._search_with_serpapi(sector, stage)
            print("serpapi_results#######################**********",serpapi_results)
            if serpapi_results:
                adjusted = self._adjust_benchmarks_to_range(serpapi_results, stage)
                if self._validate_benchmarks(adjusted, stage):
                    adjusted["data_source"] = "serpapi"
                    return adjusted
        
        # If SerpAPI fails, try Google Custom Search
        if self.google_search_key and self.google_search_engine_id:
            google_results = self._search_with_google(sector, stage)
            print("google_results#######################**********",google_results)
            if google_results:
                adjusted = self._adjust_benchmarks_to_range(google_results, stage)
                if self._validate_benchmarks(adjusted, stage):
                    adjusted["data_source"] = "google_search"
                    return adjusted

        print("⚠️ No valid benchmarks found from web search")
        return {}
        

    def _search_with_serpapi(self, sector: str, stage: str) -> Optional[Dict[str, Any]]:
        """
        Search using SerpAPI (https://serpapi.com/)
        Combines results from all queries and passes once to the LLM for extraction.
        """
        print("we are in serp api search...........")

        try:
            # 🧠 Refined, context-rich queries
            queries = [
                f"{sector} startup {stage} stage average revenue multiple 2024 site:crunchbase.com OR site:cbinsights.com OR site:techcrunch.com",
                f"{sector} startup {stage} stage valuation benchmarks 2024 site:tracxn.com OR site:dealroom.co OR site:angel.co",
                f"{sector} {stage} startup average LTV CAC ratio metrics site:saastr.com OR site:forentrepreneurs.com",
                f"{sector} {stage} stage startup typical runway and monthly burn rate benchmarks site:medium.com OR site:startupschool.org",
                f"{sector} {stage} stage valuation range pre-money post-money 2024 site:techcrunch.com OR site:dealroom.co",
                f"{sector} startup {stage} KPIs benchmarks 2024 site:crunchbase.com OR site:cbinsights.com",
            ]

            combined_texts = []

            # 🔁 Gather combined snippets from all queries first
            for query in queries:
                params = {
                    "q": query,
                    "api_key": self.serpapi_key,
                    "engine": "google",
                    "num": 10,
                    "hl": "en",
                    "gl": "us",
                    "safe": "active"
                }

                response = requests.get("https://serpapi.com/search", params=params, timeout=15)

                if response.status_code != 200:
                    print(f"⚠️ SerpAPI request failed with status {response.status_code} for query: {query}")
                    continue

                data = response.json()
                organic_results = data.get("organic_results", [])
                if not organic_results:
                    continue

                # 🧩 Combine top titles/snippets
                snippet_text = " ".join(
                    f"{item.get('title', '')}. {item.get('snippet', '')}"
                    for item in organic_results[:5]
                )

                if snippet_text.strip():
                    combined_texts.append(snippet_text)

            # 🧠 Merge all text into one single context string
            if not combined_texts:
                print("⚠️ No useful text found from SerpAPI queries.")
                return None

            final_combined_text = " ".join(combined_texts)
            print("******************* FINAL COMBINED TEXT *********************")
            print(final_combined_text)  

            # ✅ Call LLM once with all combined text
            extracted = self._extract_numbers_from_text(final_combined_text, sector, stage)

            if extracted:
                print("✅ Extracted metrics from combined SerpAPI results →", extracted)
                return extracted
            else:
                print("⚠️ No metrics extracted from combined text.")
                return None

        except Exception as e:
            print(f"❌ SerpAPI search failed: {e}")
            return None

    
    def _search_with_google(self, sector: str, stage: str) -> Optional[Dict[str, Any]]:
        """
        Search using Google Custom Search API — gathers all text first,
        then calls _extract_numbers_from_text once for cleaner context extraction.
        """
        print("we are in google searching ..........")
        try:
            queries = [
                f"{sector} startup {stage} stage average revenue multiple 2024 site:crunchbase.com OR site:cbinsights.com OR site:techcrunch.com",
                f"{sector} {stage} funding and valuation benchmarks 2024 site:dealroom.co OR site:tracxn.com",
                f"{sector} startup {stage} average LTV CAC ratio benchmarks site:saastr.com OR site:forentrepreneurs.com",
                f"{sector} startup {stage} stage typical runway and burn rate benchmarks site:medium.com OR site:startupschool.org",
                f"{sector} {stage} stage startup pre-money and post-money valuation range site:dealroom.co OR site:techcrunch.com",
                f"{sector} startup {stage} KPIs metrics 2024 site:crunchbase.com OR site:cbinsights.com",
                f"{sector} startup {stage} industry performance benchmarks 2024",
            ]

            all_text_chunks = []

            for query in queries:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.google_search_key,
                    "cx": self.google_search_engine_id,
                    "q": query,
                    "num": 10,
                    "lr": "lang_en"
                }

                response = requests.get(url, params=params, timeout=15)

                if response.status_code != 200:
                    print(f"⚠️ Google Search API failed with status {response.status_code} for query: {query}")
                    continue

                data = response.json()
                if "items" not in data:
                    continue

                # Collect snippets/titles across all queries
                for item in data["items"][:5]:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    all_text_chunks.append(f"{title}. {snippet}")

            # 🧩 Combine everything into one large text block
            combined_text = " ".join(all_text_chunks)
            print("******************* Combined Google text *********************")
            print(combined_text)  # print only first 2000 chars for readability

            # ✅ Now extract all metrics in one go
            if combined_text:
                extracted = self._extract_numbers_from_text(combined_text, sector, stage)
                if extracted:
                    print(f"✅ Final extracted metrics from Google search → {extracted}")
                    return extracted

            return None

        except Exception as e:
            print(f"❌ Google Search API error: {e}")
            return None



    def _extract_numbers_from_text(self, text: str, sector: str, stage: str) -> Dict[str, Any]:
        """
        Use LLM to extract startup benchmark metrics from combined search text.
        Improves accuracy with chunking + examples + normalization hints.
        """

        print("&&&&&&&&&& IN extract_numbers_from_text &&&&&&&&&&")
        
        # 🔹 1. Split text into manageable chunks (LLMs perform better with focused context)
        chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
        print(f"📚 Total chunks to process: {len(chunks)}")

        results = []

        # 🔹 2. Few-shot prompt template
        base_prompt = f"""
            You are a financial data extraction expert. 
            Extract **key startup financial benchmarks** from the given text.

            Always normalize currency:
            - Convert $5M → 5000000
            - Convert $10B → 10000000000

            Only use numbers that clearly relate to benchmarks.

            **Examples:**
            Text: "Seed stage startups typically have a $3M to $10M valuation and 12-18 months runway."
            JSON:
            {{
            "avg_revenue_multiple": null,
            "avg_ltv_cac_ratio": null,
            "typical_runway": 15,
            "acceptable_burn_rate": null,
            "seed_stage_valuation_range": {{
                "min": 3000000,
                "max": 10000000
            }}
            }}

            Text: "SaaS startups at Series A often see 8x ARR multiples and $200k monthly burn."
            JSON:
            {{
            "avg_revenue_multiple": 8.0,
            "avg_ltv_cac_ratio": null,
            "typical_runway": null,
            "acceptable_burn_rate": 200000,
            "seed_stage_valuation_range": {{
                "min": null,
                "max": null
            }}
            }}

            Now analyze the text below.

            Sector: {sector}
            Stage: {stage}

            Text:
            {{chunk}}

            Respond ONLY in this JSON format:
            {{
            "avg_revenue_multiple": <float or null>,
            "avg_ltv_cac_ratio": <float or null>,
            "typical_runway": <int or null>,
            "acceptable_burn_rate": <float or null>,
            "seed_stage_valuation_range": {{
                "min": <float or null>,
                "max": <float or null>
            }}
            }}
            """

        # 🔹 3. Process each chunk and aggregate results
        for idx, chunk in enumerate(chunks, 1):
            print(f"🔍 Processing chunk {idx}/{len(chunks)} (length={len(chunk)})")

            prompt = base_prompt.replace("{chunk}", chunk)

            try:
                response = self.model.generate_content(prompt)
                response_text = response.candidates[0].content.parts[0].text.strip()
                response_text = re.sub(r"```json|```", "", response_text).strip()

                print(f"⚙️ Raw output (chunk {idx}):", response_text)

                data = json.loads(response_text)
                results.append(data)
            except Exception as e:
                print(f"⚠️ LLM failed on chunk {idx}: {e}")

        # 🔹 4. Combine results from all chunks
        def avg(values):
            vals = [v for v in values if v is not None]
            return sum(vals) / len(vals) if vals else None

        combined = {
            "avg_revenue_multiple": avg([r.get("avg_revenue_multiple") for r in results]),
            "avg_ltv_cac_ratio": avg([r.get("avg_ltv_cac_ratio") for r in results]),
            "typical_runway": avg([r.get("typical_runway") for r in results]),
            "acceptable_burn_rate": avg([r.get("acceptable_burn_rate") for r in results]),
            "seed_stage_valuation_range": {
                "min": min(
                    [r["seed_stage_valuation_range"]["min"] for r in results if r["seed_stage_valuation_range"]["min"] is not None],
                    default=None
                ),
                "max": max(
                    [r["seed_stage_valuation_range"]["max"] for r in results if r["seed_stage_valuation_range"]["max"] is not None],
                    default=None
                )
            }
        }

        print("✅ Combined Extracted Benchmarks:", combined)
        return combined



    def _adjust_benchmarks_to_range(self, benchmarks: Dict[str, Any], stage: str) -> Dict[str, Any]:
        """Adjust benchmarks to realistic bounds and fill missing None values"""
        realistic_ranges = {
            "avg_revenue_multiple": {"seed": (3,12),"series_a":(6,20),"series_b":(8,25),"series_c":(10,30),"default":(4,15)},
            "avg_ltv_cac_ratio": {"seed": (2,6),"series_a":(2.5,5.5),"series_b":(3,5),"series_c":(3.5,4.5),"default":(2,5)},
            "typical_runway": {"seed": (12,24),"series_a":(18,36),"series_b":(24,48),"series_c":(30,60),"default":(12,36)},
            "acceptable_burn_rate": {"seed": (10000,100000),"series_a":(50000,300000),"series_b":(100000,500000),"series_c":(250000,1000000),"default":(20000,200000)}
        }

        adjusted = benchmarks.copy()

        # Fill or clamp each metric
        for metric, value in benchmarks.items():
            if metric in realistic_ranges:
                min_val, max_val = realistic_ranges[metric].get(stage.lower(), realistic_ranges[metric]["default"])
                # Fill missing value with midpoint
                if value is None:
                    adjusted[metric] = (min_val + max_val) / 2
                    print(f"⚠️ {metric} was None, filling with midpoint {(min_val + max_val)/2}")
                # Clamp out-of-range values
                elif value < min_val:
                    print(f"⚠️ {metric}={value} below min {min_val}, adjusting")
                    adjusted[metric] = min_val
                elif value > max_val:
                    print(f"⚠️ {metric}={value} above max {max_val}, adjusting")
                    adjusted[metric] = max_val

        # Fill missing valuation range
        if "seed_stage_valuation_range" in benchmarks:
            val_range = benchmarks["seed_stage_valuation_range"]
            valuation_defaults = {"pre_seed":(250000,2000000),"seed":(500000,5000000),"series_a":(3000000,15000000),
                                "series_b":(15000000,50000000),"series_c":(50000000,100000000),"series_d+":(100000000,500000000),
                                "default":(500000,10000000)}
            min_real, max_real = valuation_defaults.get(stage.lower(), valuation_defaults["default"])

            # Fill missing min/max
            if val_range.get("min") is None: val_range["min"] = min_real
            if val_range.get("max") is None: val_range["max"] = max_real

            # Ensure min < max
            if val_range["min"] >= val_range["max"]:
                val_range["max"] = val_range["min"] * 2

            adjusted["seed_stage_valuation_range"] = val_range

        return adjusted

    

    def _validate_benchmarks(self, benchmarks: Dict[str, Any], stage: str) -> bool:
        """Strict validation of benchmarks with cross-metric consistency checks"""

        realistic_ranges = {
            "avg_revenue_multiple": {
                "seed": (3.0, 12.0),
                "series_a": (6.0, 20.0),
                "series_b": (8.0, 25.0),
                "series_c": (10.0, 30.0),
                "default": (4.0, 15.0)
            },
            "avg_ltv_cac_ratio": {
                "seed": (2.0, 6.0),
                "series_a": (2.5, 5.5),
                "series_b": (3.0, 5.0),
                "series_c": (3.5, 4.5),
                "default": (2.0, 5.0)
            },
            "typical_runway": {
                "seed": (12, 24),
                "series_a": (18, 36),
                "series_b": (24, 48),
                "series_c": (30, 60),
                "default": (12, 36)
            },
            "acceptable_burn_rate": {
                "seed": (10000, 100000),
                "series_a": (50000, 300000),
                "series_b": (100000, 500000),
                "series_c": (250000, 1000000),
                "default": (20000, 200000)
            }
        }

        # Required metrics
        required_metrics = ["avg_revenue_multiple", "avg_ltv_cac_ratio"]
        for metric in required_metrics:
            if metric not in benchmarks:
                print(f"❌ Missing required metric: {metric}")
                return False

        valid_metrics = 0
        total_metrics = 0

        for metric, value in benchmarks.items():
            if metric in realistic_ranges:
                total_metrics += 1

                # Skip None values safely
                if value is None:
                    print(f"⚠️ Skipping {metric}: value is None")
                    continue

                min_val, max_val = realistic_ranges[metric].get(stage.lower(), realistic_ranges[metric]["default"])

                # Safe comparison
                if min_val <= value <= max_val:
                    valid_metrics += 1
                    print(f"✅ {metric}: {value} (within {min_val}-{max_val})")
                else:
                    print(f"❌ {metric}: {value} (outside {min_val}-{max_val})")

        # ✅ Validate valuation range if present
        if "seed_stage_valuation_range" in benchmarks:
            val_range = benchmarks["seed_stage_valuation_range"] or {}
            min_val = val_range.get("min")
            max_val = val_range.get("max")

            valuation_ranges = {
                "pre_seed": (250000, 2000000),
                "seed": (500000, 5000000),
                "series_a": (3000000, 15000000),
                "series_b": (15000000, 50000000),
                "series_c": (50000000, 100000000),
                "series_d+": (100000000, 500000000),
                "default": (500000, 10000000)
            }

            min_real, max_real = valuation_ranges.get(stage.lower(), valuation_ranges["default"])

            if (
                isinstance(min_val, (int, float))
                and isinstance(max_val, (int, float))
                and min_val < max_val
                and min_real <= min_val <= max_real
                and min_real <= max_val <= max_real
            ):
                valid_metrics += 1
                print(f"✅ Valuation ${min_val:,.0f}–${max_val:,.0f} within ${min_real:,}-${max_real:,}")
            else:
                print(f"⚠️ Skipping valuation check — invalid or incomplete values: {val_range}")

        # Cross-metric consistency (safe for None)
        consistency_checks = self._check_benchmark_consistency(benchmarks)
        valid_consistency = sum(check for check in consistency_checks.values() if isinstance(check, bool))
        total_consistency = len(consistency_checks)

        metric_success_rate = valid_metrics / total_metrics if total_metrics > 0 else 0
        consistency_success_rate = valid_consistency / total_consistency if total_consistency > 0 else 1

        print(f"Metric validation: {valid_metrics}/{total_metrics} ({metric_success_rate:.1%})")
        print(f"Consistency validation: {valid_consistency}/{total_consistency} ({consistency_success_rate:.1%})")

        if metric_success_rate >= 0.7 and consistency_success_rate >= 0.7:
            print("✅ Benchmarks validation PASSED")
            return True
        else:
            print("❌ Benchmarks validation FAILED")
            return False



    def _check_benchmark_consistency(self, benchmarks: Dict[str, Any]) -> Dict[str, bool]:
        """Check internal consistency between different benchmark metrics safely"""
        checks = {}

        multiple = benchmarks.get("avg_revenue_multiple")
        ltv_cac = benchmarks.get("avg_ltv_cac_ratio")
        burn = benchmarks.get("acceptable_burn_rate")
        runway = benchmarks.get("typical_runway")
        val_range = benchmarks.get("seed_stage_valuation_range", {})

        # Check 1: Revenue multiple vs LTV/CAC
        if multiple is not None and ltv_cac is not None:
            expected_min_multiple = ltv_cac * 1.5
            checks["multiple_vs_ltv_cac"] = multiple >= expected_min_multiple
            print(f"Consistency: multiple {multiple} vs expected ≥{expected_min_multiple:.1f}")

        # Check 2: Burn rate vs runway
        if burn is not None and runway is not None and runway > 0:
            reasonable_burn = burn <= (2000000 / runway)
            checks["burn_vs_runway"] = reasonable_burn
            print(f"Consistency: burn ${burn:,.0f} vs runway {runway} → {reasonable_burn}")

        # Check 3: Valuation sanity
        min_val = val_range.get("min")
        max_val = val_range.get("max")
        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
            checks["valuation_range_sane"] = (0 < min_val < max_val and max_val/min_val <= 10)
            print(f"Consistency: valuation ${min_val:,.0f}-${max_val:,.0f} sane? {checks['valuation_range_sane']}")

        return checks