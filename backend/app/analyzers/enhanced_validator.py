"""
Enhanced validation and accuracy improvements for analyzers
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
import hashlib
import json
from datetime import datetime
import structlog

logger = structlog.get_logger()


class EnhancedValidator:
    """Multiple validation methods for higher accuracy"""
    
    def __init__(self):
        self.validation_methods = {
            "dns": self._validate_via_dns,
            "ssl": self._validate_via_ssl,
            "headers": self._validate_via_headers,
            "robots": self._validate_via_robots,
            "sitemap": self._validate_via_sitemap,
            "api": self._validate_via_api
        }
    
    async def _validate_via_dns(self, domain: str) -> Dict[str, Any]:
        """Use DNS records to validate infrastructure"""
        import dns.resolver
        
        findings = {}
        try:
            # Check MX records (email provider)
            mx = dns.resolver.resolve(domain, 'MX')
            findings["has_email"] = len(mx) > 0
            
            # Check for common services
            for record in mx:
                if 'google' in str(record).lower():
                    findings["uses_google_workspace"] = True
                elif 'outlook' in str(record).lower():
                    findings["uses_microsoft"] = True
            
            # Check TXT records for services
            txt = dns.resolver.resolve(domain, 'TXT')
            for record in txt:
                record_str = str(record).lower()
                if 'v=spf1' in record_str:
                    findings["has_spf"] = True
                if 'google-site-verification' in record_str:
                    findings["has_google_verification"] = True
                if 'facebook-domain-verification' in record_str:
                    findings["has_facebook_pixel"] = True
                    
        except Exception as e:
            logger.debug(f"DNS validation failed: {e}")
            
        return findings
    
    async def _validate_via_ssl(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate for company info"""
        import ssl
        import socket
        
        findings = {}
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Extract organization info
                    subject = dict(x[0] for x in cert['subject'])
                    findings["organization"] = subject.get('organizationName', '')
                    findings["ssl_valid"] = True
                    
                    # Check certificate issuer (quality indicator)
                    issuer = dict(x[0] for x in cert['issuer'])
                    if 'Let\'s Encrypt' in issuer.get('organizationName', ''):
                        findings["ssl_type"] = "basic"
                    else:
                        findings["ssl_type"] = "extended"
                        
        except Exception as e:
            logger.debug(f"SSL validation failed: {e}")
            findings["ssl_valid"] = False
            
        return findings
    
    async def _validate_via_headers(self, domain: str) -> Dict[str, Any]:
        """Analyze HTTP headers for technology stack"""
        findings = {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", follow_redirects=True)
                headers = response.headers
                
                # Detect technologies
                if 'x-powered-by' in headers:
                    findings["powered_by"] = headers['x-powered-by']
                
                if 'server' in headers:
                    server = headers['server'].lower()
                    if 'cloudflare' in server:
                        findings["uses_cloudflare"] = True
                    elif 'nginx' in server:
                        findings["uses_nginx"] = True
                    elif 'apache' in server:
                        findings["uses_apache"] = True
                
                # Security headers (quality indicator)
                security_headers = [
                    'strict-transport-security',
                    'x-frame-options',
                    'x-content-type-options',
                    'content-security-policy'
                ]
                findings["security_score"] = sum(1 for h in security_headers if h in headers) * 25
                
                # Check for A/B testing tools
                if any(h for h in headers if 'optimizely' in h.lower()):
                    findings["has_ab_testing"] = True
                    
        except Exception as e:
            logger.debug(f"Header validation failed: {e}")
            
        return findings
    
    async def _validate_via_robots(self, domain: str) -> Dict[str, Any]:
        """Validate robots.txt for crawler permissions"""
        findings = {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}/robots.txt")
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check AI crawler permissions
                    findings["allows_gptbot"] = "gptbot" not in content or "disallow" not in content
                    findings["allows_claude"] = "claude" not in content or "disallow" not in content
                    findings["allows_googlebot"] = "googlebot" not in content or "disallow" not in content
                    
                    # Check for sitemap
                    findings["has_sitemap"] = "sitemap:" in content
                    
                    # Check crawl delay (site confidence)
                    if "crawl-delay" in content:
                        findings["has_crawl_delay"] = True
                        
        except Exception as e:
            logger.debug(f"Robots validation failed: {e}")
            
        return findings
    
    async def _validate_via_sitemap(self, domain: str) -> Dict[str, Any]:
        """Parse sitemap for page structure"""
        findings = {"pages": [], "page_count": 0}
        
        try:
            async with httpx.AsyncClient() as client:
                # Try common sitemap locations
                for sitemap_url in [
                    f"https://{domain}/sitemap.xml",
                    f"https://{domain}/sitemap_index.xml",
                    f"https://{domain}/sitemap"
                ]:
                    response = await client.get(sitemap_url)
                    if response.status_code == 200:
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(response.text)
                        
                        # Count URLs
                        urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                        findings["page_count"] = len(urls)
                        
                        # Extract key pages
                        for url in urls[:50]:  # Limit to first 50
                            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                            if loc is not None:
                                page_url = loc.text
                                if any(key in page_url.lower() for key in ['pricing', 'plans', 'demo', 'trial', 'signup']):
                                    findings["pages"].append(page_url)
                        break
                        
        except Exception as e:
            logger.debug(f"Sitemap validation failed: {e}")
            
        return findings
    
    async def _validate_via_api(self, domain: str) -> Dict[str, Any]:
        """Check for public API endpoints"""
        findings = {}
        
        try:
            async with httpx.AsyncClient() as client:
                # Check common API endpoints
                api_paths = [
                    "/api",
                    "/api/v1",
                    "/api/health",
                    "/api/status",
                    "/.well-known"
                ]
                
                for path in api_paths:
                    response = await client.get(f"https://{domain}{path}", timeout=5)
                    if response.status_code in [200, 401, 403]:  # API exists
                        findings["has_public_api"] = True
                        findings["api_path"] = path
                        break
                        
        except Exception as e:
            logger.debug(f"API validation failed: {e}")
            
        return findings
    
    async def validate_all(self, domain: str) -> Dict[str, Any]:
        """Run all validation methods"""
        results = {}
        
        tasks = []
        for method_name, method_func in self.validation_methods.items():
            tasks.append(method_func(domain))
        
        validation_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (method_name, _) in enumerate(self.validation_methods.items()):
            if not isinstance(validation_results[i], Exception):
                results[method_name] = validation_results[i]
            else:
                logger.debug(f"{method_name} validation failed: {validation_results[i]}")
                
        return results


class DataQualityChecker:
    """Ensure data quality and consistency"""
    
    def __init__(self):
        self.quality_rules = {
            "pricing": self._check_pricing_quality,
            "performance": self._check_performance_quality,
            "competitors": self._check_competitor_quality
        }
    
    def _check_pricing_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pricing data quality"""
        quality = {"score": 100, "issues": []}
        
        # Check for conflicting data
        if data.get("has_pricing_page") and data.get("pricing_hidden"):
            quality["score"] -= 30
            quality["issues"].append("Conflicting pricing visibility data")
        
        # Check for reasonable values
        if data.get("starting_price"):
            price = data["starting_price"]
            if price < 0 or price > 100000:
                quality["score"] -= 20
                quality["issues"].append(f"Unrealistic price: ${price}")
        
        # Check completeness
        required_fields = ["has_pricing_page", "has_free_trial", "has_annual_billing"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            quality["score"] -= len(missing) * 10
            quality["issues"].append(f"Missing fields: {missing}")
        
        return quality
    
    def _check_performance_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance data quality"""
        quality = {"score": 100, "issues": []}
        
        # Check score validity
        if "score" in data:
            score = data["score"]
            if score < 0 or score > 100:
                quality["score"] -= 50
                quality["issues"].append(f"Invalid performance score: {score}")
        
        # Check metric consistency
        if data.get("load_time", 0) < 1 and data.get("score", 100) < 50:
            quality["score"] -= 30
            quality["issues"].append("Inconsistent: Fast load but low score")
            
        return quality
    
    def _check_competitor_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate competitor data quality"""
        quality = {"score": 100, "issues": []}
        
        competitors = data.get("competitors", [])
        
        # Check for duplicates
        domains = [c.get("domain") for c in competitors]
        if len(domains) != len(set(domains)):
            quality["score"] -= 30
            quality["issues"].append("Duplicate competitors found")
        
        # Check for self-reference
        if data.get("analyzed_domain") in domains:
            quality["score"] -= 50
            quality["issues"].append("Self-referenced as competitor")
        
        # Check data completeness
        for comp in competitors:
            if not comp.get("domain") or not comp.get("features"):
                quality["score"] -= 10
                quality["issues"].append(f"Incomplete competitor data: {comp.get('domain', 'unknown')}")
        
        return quality
    
    def check_all_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Check quality of all analyzer results"""
        quality_report = {
            "overall_score": 100,
            "details": {},
            "recommendations": []
        }
        
        for analyzer_name, check_func in self.quality_rules.items():
            if analyzer_name in results:
                quality = check_func(results[analyzer_name])
                quality_report["details"][analyzer_name] = quality
                
                # Adjust overall score
                quality_report["overall_score"] = min(
                    quality_report["overall_score"],
                    quality["score"]
                )
                
                # Add recommendations
                if quality["issues"]:
                    quality_report["recommendations"].append(
                        f"Fix {analyzer_name}: {', '.join(quality['issues'])}"
                    )
        
        return quality_report


# Real-world testing
async def test_real_accuracy():
    """Test against real websites"""
    test_domains = [
        "stripe.com",      # Known good - lots of public data
        "notion.so",       # Freemium model
        "hubspot.com",     # Complex pricing
        "linear.app",      # Modern SaaS
        "vercel.com"       # Developer-focused
    ]
    
    validator = EnhancedValidator()
    quality_checker = DataQualityChecker()
    
    for domain in test_domains:
        print(f"\n🔍 Testing {domain}")
        
        # Run enhanced validation
        validation_data = await validator.validate_all(domain)
        
        print(f"  DNS: {validation_data.get('dns', {})}")
        print(f"  SSL: {validation_data.get('ssl', {})}")
        print(f"  Headers: {validation_data.get('headers', {})}")
        print(f"  Robots: {validation_data.get('robots', {})}")
        print(f"  Sitemap pages: {validation_data.get('sitemap', {}).get('page_count', 0)}")
        
        # This would integrate with actual analyzer results
        # quality = quality_checker.check_all_quality(analyzer_results)
        # print(f"  Quality Score: {quality['overall_score']}")


if __name__ == "__main__":
    asyncio.run(test_real_accuracy())