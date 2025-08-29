"""
Accuracy Validation Framework for Growth Co-pilot
Tests analyzer outputs against known ground truth data
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import structlog

logger = structlog.get_logger()


class AccuracyValidator:
    """Validates analyzer accuracy against known test cases"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.results = []
        
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load ground truth test cases"""
        return [
            {
                "domain": "stripe.com",
                "ground_truth": {
                    "has_pricing_page": True,
                    "pricing_transparent": True,
                    "has_free_trial": True,
                    "trial_length": 14,
                    "has_annual_billing": True,
                    "form_fields_signup": 4,
                    "mobile_responsive": True,
                    "page_speed_score": 85,  # Approximate
                    "has_social_proof": True,
                    "has_testimonials": True,
                    "competitors": ["square.com", "paypal.com", "adyen.com"],
                    "blocks_ai_crawlers": False
                }
            },
            {
                "domain": "notion.so",
                "ground_truth": {
                    "has_pricing_page": True,
                    "pricing_transparent": True,
                    "has_free_trial": True,
                    "trial_length": None,  # Freemium
                    "has_annual_billing": True,
                    "form_fields_signup": 3,
                    "mobile_responsive": True,
                    "page_speed_score": 75,
                    "has_social_proof": True,
                    "has_testimonials": True,
                    "competitors": ["confluence.atlassian.com", "clickup.com", "monday.com"],
                    "blocks_ai_crawlers": False
                }
            },
            {
                "domain": "hubspot.com",
                "ground_truth": {
                    "has_pricing_page": True,
                    "pricing_transparent": True,
                    "has_free_trial": True,
                    "trial_length": 14,
                    "has_annual_billing": True,
                    "form_fields_signup": 6,
                    "mobile_responsive": True,
                    "page_speed_score": 70,
                    "has_social_proof": True,
                    "has_testimonials": True,
                    "competitors": ["salesforce.com", "pipedrive.com", "zoho.com"],
                    "blocks_ai_crawlers": False
                }
            }
        ]
    
    async def validate_analyzer(self, analyzer_name: str, analyzer_func, test_domain: str) -> Dict[str, Any]:
        """Validate a specific analyzer against ground truth"""
        try:
            # Run analyzer
            result = await analyzer_func(test_domain)
            
            # Get ground truth
            ground_truth = next(
                (tc["ground_truth"] for tc in self.test_cases if tc["domain"] == test_domain),
                None
            )
            
            if not ground_truth:
                return {"error": f"No ground truth for {test_domain}"}
            
            # Calculate accuracy
            accuracy_metrics = self._calculate_accuracy(result, ground_truth, analyzer_name)
            
            return {
                "analyzer": analyzer_name,
                "domain": test_domain,
                "accuracy": accuracy_metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Validation failed for {analyzer_name}", error=str(e))
            return {"error": str(e)}
    
    def _calculate_accuracy(self, result: Dict, ground_truth: Dict, analyzer_name: str) -> Dict[str, Any]:
        """Calculate accuracy metrics"""
        metrics = {
            "correct": 0,
            "incorrect": 0,
            "missing": 0,
            "false_positives": 0,
            "accuracy_score": 0.0,
            "details": []
        }
        
        # Map analyzer outputs to ground truth fields
        if analyzer_name == "pricing":
            checks = [
                ("has_pricing_page", result.get("has_pricing_page")),
                ("pricing_transparent", result.get("transparent_pricing")),
                ("has_annual_billing", result.get("has_annual_plans")),
                ("has_free_trial", result.get("has_trial"))
            ]
        elif analyzer_name == "conversion":
            checks = [
                ("form_fields_signup", len(result.get("form_fields", []))),
                ("has_social_proof", result.get("has_social_proof")),
                ("has_testimonials", result.get("has_testimonials"))
            ]
        elif analyzer_name == "performance":
            score = result.get("score", 0)
            actual_score = ground_truth.get("page_speed_score", 0)
            # Allow 15 point variance for performance scores
            is_accurate = abs(score - actual_score) <= 15
            checks = [("page_speed_accurate", is_accurate)]
        elif analyzer_name == "competitors":
            found_competitors = set(result.get("competitors", []))
            actual_competitors = set(ground_truth.get("competitors", []))
            overlap = found_competitors.intersection(actual_competitors)
            accuracy = len(overlap) / len(actual_competitors) if actual_competitors else 0
            checks = [("competitor_accuracy", accuracy > 0.5)]
        else:
            checks = []
        
        # Calculate metrics
        for field, analyzer_value in checks:
            ground_value = ground_truth.get(field)
            
            if ground_value is None:
                metrics["missing"] += 1
            elif analyzer_value == ground_value:
                metrics["correct"] += 1
                metrics["details"].append(f"✓ {field}: {analyzer_value}")
            else:
                metrics["incorrect"] += 1
                metrics["details"].append(f"✗ {field}: got {analyzer_value}, expected {ground_value}")
        
        # Calculate accuracy score
        total = metrics["correct"] + metrics["incorrect"] + metrics["missing"]
        if total > 0:
            metrics["accuracy_score"] = (metrics["correct"] / total) * 100
        
        return metrics
    
    async def run_full_validation(self, analyzers: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation on all analyzers"""
        results = []
        
        for test_case in self.test_cases:
            domain = test_case["domain"]
            logger.info(f"Validating against {domain}")
            
            for analyzer_name, analyzer_func in analyzers.items():
                result = await self.validate_analyzer(analyzer_name, analyzer_func, domain)
                results.append(result)
        
        # Calculate overall accuracy
        total_accuracy = sum(r["accuracy"]["accuracy_score"] for r in results if "accuracy" in r)
        avg_accuracy = total_accuracy / len(results) if results else 0
        
        return {
            "overall_accuracy": avg_accuracy,
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate accuracy summary"""
        summary = {
            "total_tests": len(results),
            "passed": 0,
            "failed": 0,
            "accuracy_by_analyzer": {},
            "problem_areas": []
        }
        
        # Group by analyzer
        for result in results:
            if "accuracy" in result:
                analyzer = result["analyzer"]
                score = result["accuracy"]["accuracy_score"]
                
                if analyzer not in summary["accuracy_by_analyzer"]:
                    summary["accuracy_by_analyzer"][analyzer] = []
                
                summary["accuracy_by_analyzer"][analyzer].append(score)
                
                if score >= 80:
                    summary["passed"] += 1
                else:
                    summary["failed"] += 1
                    summary["problem_areas"].append(f"{analyzer} on {result['domain']}: {score:.1f}%")
        
        # Calculate averages
        for analyzer, scores in summary["accuracy_by_analyzer"].items():
            summary["accuracy_by_analyzer"][analyzer] = sum(scores) / len(scores)
        
        return summary


class ConfidenceScorer:
    """Add confidence scores to recommendations"""
    
    def score_recommendation(self, recommendation: Dict[str, Any], supporting_data: Dict[str, Any]) -> float:
        """Calculate confidence score for a recommendation"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data sources
        if supporting_data.get("multiple_signals"):
            confidence += 0.2  # Multiple analyzers found same issue
        
        if supporting_data.get("competitor_validated"):
            confidence += 0.15  # Competitors do it differently
        
        if supporting_data.get("industry_benchmark"):
            confidence += 0.15  # Have industry data to support
        
        if supporting_data.get("user_testable"):
            confidence += 0.1  # Can be easily verified by user
        
        # Decrease confidence for assumptions
        if supporting_data.get("estimated"):
            confidence -= 0.2  # Using estimates not real data
        
        if supporting_data.get("partial_data"):
            confidence -= 0.15  # Missing some information
        
        return min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1
    
    def add_confidence_to_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Add confidence scores to all recommendations"""
        
        # Score revenue leaks
        if "revenue_leaks" in results:
            for leak in results["revenue_leaks"]:
                leak["confidence"] = self.score_recommendation(leak, {
                    "multiple_signals": leak.get("verified", False),
                    "competitor_validated": leak.get("competitors_different", False),
                    "user_testable": True
                })
        
        # Score growth opportunities
        if "untapped_channels" in results:
            for channel in results["untapped_channels"]:
                channel["confidence"] = self.score_recommendation(channel, {
                    "industry_benchmark": True,
                    "estimated": True,  # User numbers are estimates
                    "competitor_validated": channel.get("competitors_using", False)
                })
        
        return results


class CrossValidator:
    """Cross-validate findings between analyzers"""
    
    async def validate_findings(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-check findings between different analyzers"""
        validations = {}
        
        # Validate pricing findings
        if all_results.get("revenue_intelligence") and all_results.get("competitors"):
            pricing_issues = all_results["revenue_intelligence"].get("pricing_opportunities", [])
            competitor_features = all_results["competitors"].get("competitor_features", [])
            
            for issue in pricing_issues:
                if "annual_billing" in str(issue):
                    # Check if competitors really have annual billing
                    has_annual = any("annual" in str(f).lower() for f in competitor_features)
                    issue["validated"] = has_annual
                    issue["confidence_boost"] = 0.3 if has_annual else -0.2
        
        # Validate performance findings
        if all_results.get("performance") and all_results.get("revenue_intelligence"):
            perf_score = all_results["performance"].get("score", 100)
            revenue_leaks = all_results["revenue_intelligence"].get("revenue_leaks", [])
            
            # If performance is bad, should have speed-related revenue leaks
            if perf_score < 50:
                has_speed_leak = any("speed" in str(leak).lower() or "load" in str(leak).lower() 
                                    for leak in revenue_leaks)
                validations["performance_validated"] = has_speed_leak
        
        # Validate form findings
        if all_results.get("form_intelligence") and all_results.get("conversion"):
            form_fields = all_results["form_intelligence"].get("average_fields", 0)
            conversion_issues = all_results["conversion"].get("issues", [])
            
            # High form fields should correlate with conversion issues
            if form_fields > 5:
                has_form_issue = any("form" in str(issue).lower() for issue in conversion_issues)
                validations["form_validated"] = has_form_issue
        
        return validations


# Testing functions
async def test_accuracy():
    """Run accuracy tests on known domains"""
    from app.analyzers.revenue_intelligence import RevenueIntelligenceAnalyzer
    from app.analyzers.performance import PerformanceAnalyzer
    from app.analyzers.competitors import CompetitorAnalyzer
    
    validator = AccuracyValidator()
    
    # Create analyzer instances
    analyzers = {
        "revenue": RevenueIntelligenceAnalyzer().analyze,
        "performance": PerformanceAnalyzer().analyze,
        "competitors": CompetitorAnalyzer().analyze
    }
    
    # Run validation
    results = await validator.run_full_validation(analyzers)
    
    print(f"\n📊 ACCURACY REPORT")
    print(f"Overall Accuracy: {results['overall_accuracy']:.1f}%")
    print(f"\nBy Analyzer:")
    for analyzer, score in results['summary']['accuracy_by_analyzer'].items():
        print(f"  {analyzer}: {score:.1f}%")
    
    if results['summary']['problem_areas']:
        print(f"\n⚠️ Problem Areas:")
        for problem in results['summary']['problem_areas']:
            print(f"  - {problem}")
    
    return results


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_accuracy())