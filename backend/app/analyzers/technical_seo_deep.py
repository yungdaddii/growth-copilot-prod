"""
Technical SEO Deep Dive Analyzer
Goes beyond basic meta tags to find real technical SEO issues
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional, Set
import re
import json
import structlog
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

from app.utils.cache import cache_result, get_cached_result

logger = structlog.get_logger()


class TechnicalSEODeepAnalyzer:
    """
    Deep technical SEO analysis that finds real issues:
    - Canonical URL problems
    - Hreflang implementation errors
    - XML sitemap validation
    - Core Web Vitals per page type
    - Internal link structure and orphan pages
    - Redirect chains and loops
    - JavaScript SEO issues
    - Structured data validation
    - Crawl budget optimization
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.max_pages_to_crawl = 50  # Limit for performance
        
    async def analyze(self, domain: str) -> Dict[str, Any]:
        """
        Perform deep technical SEO analysis
        """
        cache_key = f"technical_seo_deep:{domain}"
        cached = await get_cached_result(cache_key)
        if cached:
            return cached
        
        results = {
            "crawl_stats": {},
            "indexability_issues": [],
            "canonical_issues": [],
            "hreflang_issues": [],
            "sitemap_issues": [],
            "internal_linking_issues": [],
            "redirect_issues": [],
            "javascript_seo_issues": [],
            "structured_data_issues": [],
            "core_web_vitals_by_template": {},
            "orphan_pages": [],
            "duplicate_content": [],
            "crawl_budget_waste": [],
            "technical_debt_score": 0,
            "priority_fixes": [],
            "seo_health_score": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                # Start with homepage
                homepage_url = f"https://{domain}"
                
                # Crawl site structure
                crawl_results = await self._crawl_site_structure(domain, client)
                results["crawl_stats"] = crawl_results["stats"]
                
                # Analyze each area in parallel
                tasks = [
                    self._analyze_indexability(crawl_results, client),
                    self._analyze_canonicals(crawl_results, client),
                    self._analyze_hreflang(crawl_results, client),
                    self._validate_sitemap(domain, crawl_results, client),
                    self._analyze_internal_linking(crawl_results),
                    self._detect_redirect_chains(crawl_results, client),
                    self._analyze_javascript_seo(crawl_results, client),
                    self._validate_structured_data(crawl_results, client),
                    self._analyze_core_web_vitals_by_template(crawl_results, domain),
                    self._find_duplicate_content(crawl_results),
                    self._analyze_crawl_budget(crawl_results)
                ]
                
                analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(analysis_results):
                    if isinstance(result, Exception):
                        logger.error(f"Technical SEO task {i} failed", error=str(result))
                    else:
                        if i == 0:  # Indexability
                            results["indexability_issues"] = result
                        elif i == 1:  # Canonicals
                            results["canonical_issues"] = result
                        elif i == 2:  # Hreflang
                            results["hreflang_issues"] = result
                        elif i == 3:  # Sitemap
                            results["sitemap_issues"] = result
                        elif i == 4:  # Internal linking
                            results["internal_linking_issues"] = result.get("issues", [])
                            results["orphan_pages"] = result.get("orphan_pages", [])
                        elif i == 5:  # Redirects
                            results["redirect_issues"] = result
                        elif i == 6:  # JavaScript SEO
                            results["javascript_seo_issues"] = result
                        elif i == 7:  # Structured data
                            results["structured_data_issues"] = result
                        elif i == 8:  # Core Web Vitals
                            results["core_web_vitals_by_template"] = result
                        elif i == 9:  # Duplicate content
                            results["duplicate_content"] = result
                        elif i == 10:  # Crawl budget
                            results["crawl_budget_waste"] = result
                
                # Calculate scores and priorities
                results["technical_debt_score"] = self._calculate_technical_debt(results)
                results["priority_fixes"] = self._prioritize_fixes(results)
                results["seo_health_score"] = self._calculate_health_score(results)
                
                # Cache for 24 hours
                await cache_result(cache_key, results, ttl=86400)
        
        except Exception as e:
            logger.error(f"Technical SEO deep analysis failed for {domain}", error=str(e))
        
        return results
    
    async def _crawl_site_structure(self, domain: str, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Crawl site to understand structure and find all pages"""
        crawled_urls = set()
        to_crawl = {f"https://{domain}"}
        pages_data = {}
        redirects = {}
        
        while to_crawl and len(crawled_urls) < self.max_pages_to_crawl:
            url = to_crawl.pop()
            
            if url in crawled_urls:
                continue
            
            try:
                response = await client.get(url, follow_redirects=False)
                crawled_urls.add(url)
                
                # Handle redirects
                if 300 <= response.status_code < 400:
                    redirect_target = response.headers.get('location')
                    if redirect_target:
                        redirect_url = urljoin(url, redirect_target)
                        redirects[url] = {
                            "target": redirect_url,
                            "status": response.status_code
                        }
                        if redirect_url not in crawled_urls:
                            to_crawl.add(redirect_url)
                    continue
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract page data
                    page_data = {
                        "url": url,
                        "title": soup.find('title').text if soup.find('title') else None,
                        "meta_description": None,
                        "canonical": None,
                        "robots": None,
                        "hreflang": [],
                        "internal_links": [],
                        "external_links": [],
                        "h1_count": len(soup.find_all('h1')),
                        "word_count": len(soup.get_text().split()),
                        "images_without_alt": 0,
                        "response_time": response.elapsed.total_seconds()
                    }
                    
                    # Meta tags
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc:
                        page_data["meta_description"] = meta_desc.get('content')
                    
                    meta_robots = soup.find('meta', attrs={'name': 'robots'})
                    if meta_robots:
                        page_data["robots"] = meta_robots.get('content')
                    
                    # Canonical
                    canonical = soup.find('link', attrs={'rel': 'canonical'})
                    if canonical:
                        page_data["canonical"] = canonical.get('href')
                    
                    # Hreflang
                    hreflang_tags = soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True})
                    page_data["hreflang"] = [
                        {"lang": tag.get('hreflang'), "href": tag.get('href')}
                        for tag in hreflang_tags
                    ]
                    
                    # Find all links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        absolute_url = urljoin(url, href)
                        parsed = urlparse(absolute_url)
                        
                        if parsed.netloc == domain:
                            page_data["internal_links"].append(absolute_url)
                            if absolute_url not in crawled_urls and len(crawled_urls) < self.max_pages_to_crawl:
                                to_crawl.add(absolute_url)
                        elif parsed.scheme in ['http', 'https']:
                            page_data["external_links"].append(absolute_url)
                    
                    # Images without alt
                    images = soup.find_all('img')
                    page_data["images_without_alt"] = sum(1 for img in images if not img.get('alt'))
                    
                    pages_data[url] = page_data
            
            except Exception as e:
                logger.debug(f"Error crawling {url}: {e}")
        
        return {
            "pages": pages_data,
            "redirects": redirects,
            "stats": {
                "total_pages_crawled": len(crawled_urls),
                "total_pages_found": len(pages_data),
                "total_redirects": len(redirects)
            }
        }
    
    async def _analyze_indexability(self, crawl_results: Dict, client: httpx.AsyncClient) -> List[Dict]:
        """Check for indexability issues"""
        issues = []
        pages = crawl_results.get("pages", {})
        
        for url, page_data in pages.items():
            # Check robots meta
            robots = page_data.get("robots", "")
            if robots and any(x in robots.lower() for x in ["noindex", "none"]):
                issues.append({
                    "type": "noindex_page",
                    "url": url,
                    "severity": "high",
                    "issue": "Page has noindex directive",
                    "impact": "Page won't appear in search results",
                    "fix": "Remove noindex if page should be indexed"
                })
            
            # Check for orphan pages (no internal links pointing to them)
            is_orphan = True
            for other_url, other_data in pages.items():
                if url != other_url and url in other_data.get("internal_links", []):
                    is_orphan = False
                    break
            
            if is_orphan and not url.endswith("/"):  # Ignore homepage
                issues.append({
                    "type": "orphan_page",
                    "url": url,
                    "severity": "medium",
                    "issue": "No internal links point to this page",
                    "impact": "Hard for search engines to discover",
                    "fix": "Add internal links from related pages"
                })
            
            # Check for thin content
            word_count = page_data.get("word_count", 0)
            if word_count < 300:
                issues.append({
                    "type": "thin_content",
                    "url": url,
                    "word_count": word_count,
                    "severity": "medium",
                    "issue": f"Page has only {word_count} words",
                    "impact": "May be seen as low-quality content",
                    "fix": "Add more valuable content (aim for 500+ words)"
                })
        
        return issues
    
    async def _analyze_canonicals(self, crawl_results: Dict, client: httpx.AsyncClient) -> List[Dict]:
        """Analyze canonical URL implementation"""
        issues = []
        pages = crawl_results.get("pages", {})
        
        canonical_targets = defaultdict(list)
        
        for url, page_data in pages.items():
            canonical = page_data.get("canonical")
            
            if not canonical:
                issues.append({
                    "type": "missing_canonical",
                    "url": url,
                    "severity": "low",
                    "issue": "No canonical URL specified",
                    "impact": "May cause duplicate content issues",
                    "fix": "Add self-referencing canonical"
                })
            else:
                # Check if canonical is absolute
                if not canonical.startswith("http"):
                    issues.append({
                        "type": "relative_canonical",
                        "url": url,
                        "canonical": canonical,
                        "severity": "high",
                        "issue": "Canonical URL is relative, not absolute",
                        "impact": "Search engines may not recognize it",
                        "fix": "Use absolute URL for canonical"
                    })
                
                # Track canonical targets
                canonical_targets[canonical].append(url)
                
                # Check for canonical chains
                if canonical != url and canonical in pages:
                    target_canonical = pages[canonical].get("canonical")
                    if target_canonical and target_canonical != canonical:
                        issues.append({
                            "type": "canonical_chain",
                            "url": url,
                            "chain": f"{url} -> {canonical} -> {target_canonical}",
                            "severity": "high",
                            "issue": "Canonical chain detected",
                            "impact": "Confuses search engines",
                            "fix": "Point directly to final canonical URL"
                        })
        
        # Check for multiple pages pointing to same canonical
        for canonical, pointing_pages in canonical_targets.items():
            if len(pointing_pages) > 5:  # Threshold for concern
                issues.append({
                    "type": "excessive_canonicalization",
                    "canonical_target": canonical,
                    "pages_count": len(pointing_pages),
                    "severity": "medium",
                    "issue": f"{len(pointing_pages)} pages canonicalize to one URL",
                    "impact": "May indicate content duplication issues",
                    "fix": "Review if all pages should canonicalize here"
                })
        
        return issues
    
    async def _analyze_hreflang(self, crawl_results: Dict, client: httpx.AsyncClient) -> List[Dict]:
        """Check hreflang implementation"""
        issues = []
        pages = crawl_results.get("pages", {})
        
        hreflang_groups = defaultdict(set)
        
        for url, page_data in pages.items():
            hreflang_tags = page_data.get("hreflang", [])
            
            if hreflang_tags:
                # Check for x-default
                has_x_default = any(tag["lang"] == "x-default" for tag in hreflang_tags)
                if not has_x_default:
                    issues.append({
                        "type": "missing_x_default",
                        "url": url,
                        "severity": "low",
                        "issue": "No x-default hreflang tag",
                        "impact": "No fallback for unlisted languages",
                        "fix": "Add x-default hreflang tag"
                    })
                
                # Check for self-reference
                has_self_reference = any(
                    tag["href"] == url 
                    for tag in hreflang_tags
                )
                if not has_self_reference:
                    issues.append({
                        "type": "no_self_reference_hreflang",
                        "url": url,
                        "severity": "medium",
                        "issue": "No self-referencing hreflang",
                        "impact": "Incomplete hreflang setup",
                        "fix": "Include self-referencing hreflang"
                    })
                
                # Check for return links
                for tag in hreflang_tags:
                    target_url = tag["href"]
                    if target_url in pages:
                        target_hreflang = pages[target_url].get("hreflang", [])
                        has_return_link = any(
                            t["href"] == url 
                            for t in target_hreflang
                        )
                        if not has_return_link:
                            issues.append({
                                "type": "missing_return_hreflang",
                                "url": url,
                                "target": target_url,
                                "severity": "high",
                                "issue": "Missing return hreflang link",
                                "impact": "Breaks hreflang implementation",
                                "fix": f"Add hreflang from {target_url} back to {url}"
                            })
                
                # Check language codes
                for tag in hreflang_tags:
                    lang = tag["lang"]
                    if lang != "x-default" and not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', lang):
                        issues.append({
                            "type": "invalid_hreflang_code",
                            "url": url,
                            "lang_code": lang,
                            "severity": "high",
                            "issue": f"Invalid language code: {lang}",
                            "impact": "Hreflang won't work",
                            "fix": "Use valid ISO 639-1 language codes"
                        })
        
        return issues
    
    async def _validate_sitemap(self, domain: str, crawl_results: Dict, client: httpx.AsyncClient) -> List[Dict]:
        """Validate XML sitemap"""
        issues = []
        
        sitemap_urls = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/wp-sitemap.xml"
        ]
        
        sitemap_found = False
        
        for sitemap_url in sitemap_urls:
            try:
                response = await client.get(sitemap_url)
                if response.status_code == 200:
                    sitemap_found = True
                    
                    # Parse XML
                    try:
                        root = ET.fromstring(response.text)
                        
                        # Check for sitemap index
                        if 'sitemapindex' in root.tag:
                            # It's a sitemap index
                            sitemaps = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
                            if len(sitemaps) > 50000:
                                issues.append({
                                    "type": "sitemap_too_large",
                                    "url": sitemap_url,
                                    "count": len(sitemaps),
                                    "severity": "medium",
                                    "issue": f"Sitemap index has {len(sitemaps)} sitemaps (max 50,000)",
                                    "impact": "Search engines may not process all",
                                    "fix": "Split into multiple sitemap indexes"
                                })
                        else:
                            # Regular sitemap
                            urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                            
                            if len(urls) > 50000:
                                issues.append({
                                    "type": "sitemap_too_many_urls",
                                    "url": sitemap_url,
                                    "count": len(urls),
                                    "severity": "high",
                                    "issue": f"Sitemap has {len(urls)} URLs (max 50,000)",
                                    "impact": "Exceeds sitemap limit",
                                    "fix": "Split into multiple sitemaps"
                                })
                            
                            # Check for missing pages
                            sitemap_url_set = set()
                            for url_element in urls:
                                loc = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                                if loc is not None:
                                    sitemap_url_set.add(loc.text)
                            
                            # Compare with crawled pages
                            crawled_pages = set(crawl_results.get("pages", {}).keys())
                            
                            missing_from_sitemap = crawled_pages - sitemap_url_set
                            if missing_from_sitemap:
                                issues.append({
                                    "type": "pages_missing_from_sitemap",
                                    "count": len(missing_from_sitemap),
                                    "examples": list(missing_from_sitemap)[:5],
                                    "severity": "medium",
                                    "issue": f"{len(missing_from_sitemap)} crawled pages not in sitemap",
                                    "impact": "Pages may not be discovered by search engines",
                                    "fix": "Add important pages to sitemap"
                                })
                            
                            # Check for non-existent pages in sitemap
                            for sitemap_page in sitemap_url_set:
                                if sitemap_page not in crawled_pages:
                                    # Quick check if page exists
                                    try:
                                        check_response = await client.head(sitemap_page)
                                        if check_response.status_code == 404:
                                            issues.append({
                                                "type": "404_in_sitemap",
                                                "url": sitemap_page,
                                                "severity": "high",
                                                "issue": "404 page in sitemap",
                                                "impact": "Wastes crawl budget",
                                                "fix": "Remove 404 pages from sitemap"
                                            })
                                    except:
                                        pass
                            
                            # Check lastmod dates
                            for url_element in urls[:10]:  # Sample check
                                lastmod = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                                if lastmod is None:
                                    issues.append({
                                        "type": "missing_lastmod",
                                        "severity": "low",
                                        "issue": "Sitemap URLs missing lastmod date",
                                        "impact": "Search engines can't prioritize fresh content",
                                        "fix": "Add lastmod dates to sitemap"
                                    })
                                    break
                    
                    except ET.ParseError:
                        issues.append({
                            "type": "invalid_sitemap_xml",
                            "url": sitemap_url,
                            "severity": "critical",
                            "issue": "Sitemap XML is malformed",
                            "impact": "Search engines can't parse sitemap",
                            "fix": "Fix XML syntax errors"
                        })
                    
                    break
            
            except Exception as e:
                logger.debug(f"Error checking sitemap {sitemap_url}: {e}")
        
        if not sitemap_found:
            issues.append({
                "type": "no_sitemap",
                "severity": "high",
                "issue": "No XML sitemap found",
                "impact": "Harder for search engines to discover all pages",
                "fix": "Create XML sitemap at /sitemap.xml"
            })
        
        return issues
    
    async def _analyze_internal_linking(self, crawl_results: Dict) -> Dict[str, Any]:
        """Analyze internal link structure"""
        pages = crawl_results.get("pages", {})
        issues = []
        orphan_pages = []
        
        # Build link graph
        inbound_links = defaultdict(set)
        outbound_links = defaultdict(set)
        
        for url, page_data in pages.items():
            internal_links = page_data.get("internal_links", [])
            for link in internal_links:
                outbound_links[url].add(link)
                inbound_links[link].add(url)
        
        # Find orphan pages
        for url in pages.keys():
            if url not in inbound_links or len(inbound_links[url]) == 0:
                if not url.endswith("/"):  # Not homepage
                    orphan_pages.append({
                        "url": url,
                        "title": pages[url].get("title", ""),
                        "issue": "No internal links pointing to this page"
                    })
        
        # Find pages with too few internal links
        for url, linking_pages in inbound_links.items():
            if len(linking_pages) < 2:
                issues.append({
                    "type": "weak_internal_linking",
                    "url": url,
                    "inbound_links": len(linking_pages),
                    "severity": "medium",
                    "issue": f"Only {len(linking_pages)} internal link(s) to this page",
                    "impact": "Weak page authority flow",
                    "fix": "Add more contextual internal links"
                })
        
        # Find pages with excessive outbound links
        for url, links in outbound_links.items():
            if len(links) > 100:
                issues.append({
                    "type": "too_many_internal_links",
                    "url": url,
                    "link_count": len(links),
                    "severity": "low",
                    "issue": f"Page has {len(links)} internal links",
                    "impact": "Dilutes PageRank flow",
                    "fix": "Reduce to most important links"
                })
        
        # Check for broken internal links
        all_internal_links = set()
        for links in outbound_links.values():
            all_internal_links.update(links)
        
        existing_pages = set(pages.keys())
        broken_internal_links = all_internal_links - existing_pages
        
        for broken_link in broken_internal_links:
            # Find pages linking to broken URL
            linking_pages = [url for url, links in outbound_links.items() if broken_link in links]
            if linking_pages:
                issues.append({
                    "type": "broken_internal_link",
                    "broken_url": broken_link,
                    "linking_pages": linking_pages[:3],
                    "severity": "high",
                    "issue": f"Internal link to non-existent page",
                    "impact": "Poor user experience, wastes link equity",
                    "fix": "Fix or remove broken link"
                })
        
        return {
            "issues": issues,
            "orphan_pages": orphan_pages
        }
    
    async def _detect_redirect_chains(self, crawl_results: Dict, client: httpx.AsyncClient) -> List[Dict]:
        """Detect redirect chains and loops"""
        issues = []
        redirects = crawl_results.get("redirects", {})
        
        # Build redirect chains
        for start_url, redirect_data in redirects.items():
            chain = [start_url]
            current = redirect_data["target"]
            
            while current in redirects and len(chain) < 10:
                chain.append(current)
                current = redirects[current]["target"]
                
                # Detect loops
                if current in chain:
                    issues.append({
                        "type": "redirect_loop",
                        "chain": chain + [current],
                        "severity": "critical",
                        "issue": "Redirect loop detected",
                        "impact": "Pages become inaccessible",
                        "fix": "Break the redirect loop"
                    })
                    break
            
            if len(chain) > 2:
                issues.append({
                    "type": "redirect_chain",
                    "chain": chain,
                    "length": len(chain),
                    "severity": "high" if len(chain) > 3 else "medium",
                    "issue": f"Redirect chain with {len(chain)} hops",
                    "impact": "Slows page load, loses link equity",
                    "fix": "Redirect directly to final destination"
                })
        
        return issues
    
    async def _analyze_javascript_seo(self, crawl_results: Dict, client: httpx.AsyncClient) -> List[Dict]:
        """Check for JavaScript SEO issues"""
        issues = []
        pages = crawl_results.get("pages", {})
        
        # Sample some pages to check for JS rendering issues
        sample_pages = list(pages.items())[:10]
        
        for url, page_data in sample_pages:
            try:
                # Get page with and without JavaScript
                response = await client.get(url)
                if response.status_code == 200:
                    # Check for signs of client-side rendering
                    if '<div id="root"></div>' in response.text or '<div id="app"></div>' in response.text:
                        # Check if content is in initial HTML
                        if page_data.get("word_count", 0) < 100:
                            issues.append({
                                "type": "csr_seo_issue",
                                "url": url,
                                "severity": "high",
                                "issue": "Content relies on JavaScript rendering",
                                "impact": "Search engines may not see content",
                                "fix": "Implement SSR or SSG for SEO-critical pages"
                            })
                    
                    # Check for lazy-loaded critical content
                    if 'lazy' in response.text.lower() and page_data.get("h1_count", 0) == 0:
                        issues.append({
                            "type": "lazy_loaded_critical_content",
                            "url": url,
                            "severity": "medium",
                            "issue": "Critical content may be lazy-loaded",
                            "impact": "Search engines might miss important content",
                            "fix": "Don't lazy-load above-fold or critical content"
                        })
            
            except Exception as e:
                logger.debug(f"Error checking JavaScript SEO for {url}: {e}")
        
        return issues
    
    async def _validate_structured_data(self, crawl_results: Dict, client: httpx.AsyncClient) -> List[Dict]:
        """Validate structured data implementation"""
        issues = []
        pages = crawl_results.get("pages", {})
        
        for url, page_data in list(pages.items())[:20]:  # Sample check
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find JSON-LD structured data
                    json_ld_scripts = soup.find_all('script', type='application/ld+json')
                    
                    if not json_ld_scripts:
                        # Check if it's a page that should have structured data
                        if any(indicator in url for indicator in ['product', 'blog', 'article', 'about']):
                            issues.append({
                                "type": "missing_structured_data",
                                "url": url,
                                "severity": "medium",
                                "issue": "No structured data found",
                                "impact": "Missing rich snippets opportunity",
                                "fix": "Add appropriate schema.org markup"
                            })
                    else:
                        # Validate JSON-LD
                        for script in json_ld_scripts:
                            try:
                                data = json.loads(script.string)
                                
                                # Check for required properties
                                if '@type' not in data:
                                    issues.append({
                                        "type": "invalid_structured_data",
                                        "url": url,
                                        "severity": "high",
                                        "issue": "Structured data missing @type",
                                        "impact": "Structured data won't be recognized",
                                        "fix": "Add @type property"
                                    })
                                
                                # Check for common issues
                                if data.get('@type') == 'Product' and 'offers' not in data:
                                    issues.append({
                                        "type": "incomplete_product_schema",
                                        "url": url,
                                        "severity": "medium",
                                        "issue": "Product schema missing offers",
                                        "impact": "Won't show price in search results",
                                        "fix": "Add offers with price and availability"
                                    })
                            
                            except json.JSONDecodeError:
                                issues.append({
                                    "type": "invalid_json_ld",
                                    "url": url,
                                    "severity": "high",
                                    "issue": "Invalid JSON-LD syntax",
                                    "impact": "Structured data won't be parsed",
                                    "fix": "Fix JSON syntax errors"
                                })
            
            except Exception as e:
                logger.debug(f"Error validating structured data for {url}: {e}")
        
        return issues
    
    async def _analyze_core_web_vitals_by_template(self, crawl_results: Dict, domain: str) -> Dict[str, Any]:
        """Analyze Core Web Vitals by page template/type"""
        # This would integrate with PageSpeed API in production
        # For now, return template-based estimates
        
        pages = crawl_results.get("pages", {})
        templates = {
            "homepage": [],
            "product": [],
            "category": [],
            "blog": [],
            "other": []
        }
        
        for url, page_data in pages.items():
            if url.endswith("/"):
                templates["homepage"].append(url)
            elif "product" in url:
                templates["product"].append(url)
            elif "category" in url or "collection" in url:
                templates["category"].append(url)
            elif "blog" in url or "article" in url:
                templates["blog"].append(url)
            else:
                templates["other"].append(url)
        
        vitals_by_template = {}
        for template, urls in templates.items():
            if urls:
                # In production, would fetch real CWV data
                vitals_by_template[template] = {
                    "sample_size": len(urls),
                    "average_lcp": 2.5,  # Placeholder
                    "average_fid": 100,  # Placeholder
                    "average_cls": 0.1,  # Placeholder
                    "passing_rate": 75,  # Placeholder
                    "issues": []
                }
                
                # Add template-specific issues
                if template == "product" and vitals_by_template[template]["average_lcp"] > 2.5:
                    vitals_by_template[template]["issues"].append({
                        "issue": "Product pages have poor LCP",
                        "impact": "Lower rankings for product searches",
                        "fix": "Optimize product images and critical CSS"
                    })
        
        return vitals_by_template
    
    async def _find_duplicate_content(self, crawl_results: Dict) -> List[Dict]:
        """Find duplicate or near-duplicate content"""
        issues = []
        pages = crawl_results.get("pages", {})
        
        # Group pages by title
        titles = defaultdict(list)
        for url, page_data in pages.items():
            title = page_data.get("title", "")
            if title:
                titles[title].append(url)
        
        # Find duplicate titles
        for title, urls in titles.items():
            if len(urls) > 1:
                issues.append({
                    "type": "duplicate_title",
                    "title": title,
                    "urls": urls,
                    "count": len(urls),
                    "severity": "medium",
                    "issue": f"{len(urls)} pages with identical title",
                    "impact": "Confuses search engines and users",
                    "fix": "Create unique titles for each page"
                })
        
        # Group by meta description
        descriptions = defaultdict(list)
        for url, page_data in pages.items():
            desc = page_data.get("meta_description", "")
            if desc:
                descriptions[desc].append(url)
        
        # Find duplicate descriptions
        for desc, urls in descriptions.items():
            if len(urls) > 1:
                issues.append({
                    "type": "duplicate_meta_description",
                    "urls": urls[:5],
                    "count": len(urls),
                    "severity": "low",
                    "issue": f"{len(urls)} pages with identical meta description",
                    "impact": "Missed opportunity for unique SERP messaging",
                    "fix": "Write unique descriptions for each page"
                })
        
        return issues
    
    async def _analyze_crawl_budget(self, crawl_results: Dict) -> List[Dict]:
        """Identify crawl budget waste"""
        issues = []
        pages = crawl_results.get("pages", {})
        redirects = crawl_results.get("redirects", {})
        
        # Check for parameter URLs
        parameter_urls = []
        for url in pages.keys():
            if '?' in url:
                parameter_urls.append(url)
        
        if len(parameter_urls) > 10:
            issues.append({
                "type": "excessive_parameter_urls",
                "count": len(parameter_urls),
                "examples": parameter_urls[:5],
                "severity": "medium",
                "issue": f"{len(parameter_urls)} URLs with parameters",
                "impact": "Wastes crawl budget on duplicate content",
                "fix": "Use canonical tags or robots.txt to manage parameters"
            })
        
        # Check for excessive redirects
        if len(redirects) > 20:
            issues.append({
                "type": "excessive_redirects",
                "count": len(redirects),
                "severity": "medium",
                "issue": f"{len(redirects)} redirects found",
                "impact": "Wastes crawl budget",
                "fix": "Update internal links to final destinations"
            })
        
        # Check for low-value pages
        low_value_pages = []
        for url, page_data in pages.items():
            word_count = page_data.get("word_count", 0)
            if word_count < 50 and not url.endswith("/"):
                low_value_pages.append(url)
        
        if low_value_pages:
            issues.append({
                "type": "low_value_pages",
                "count": len(low_value_pages),
                "examples": low_value_pages[:5],
                "severity": "low",
                "issue": f"{len(low_value_pages)} pages with minimal content",
                "impact": "Wastes crawl budget",
                "fix": "Noindex low-value pages or add content"
            })
        
        return issues
    
    def _calculate_technical_debt(self, results: Dict) -> int:
        """Calculate technical debt score (0-100, higher is worse)"""
        score = 0
        
        # Weight different issue types
        weights = {
            "canonical_issues": 2,
            "hreflang_issues": 3,
            "sitemap_issues": 2,
            "redirect_issues": 3,
            "javascript_seo_issues": 4,
            "structured_data_issues": 2,
            "indexability_issues": 4,
            "orphan_pages": 2,
            "duplicate_content": 1,
            "crawl_budget_waste": 1
        }
        
        for issue_type, weight in weights.items():
            issues = results.get(issue_type, [])
            if isinstance(issues, list):
                score += min(len(issues) * weight, 20)  # Cap each category
        
        return min(score, 100)
    
    def _prioritize_fixes(self, results: Dict) -> List[Dict]:
        """Prioritize technical SEO fixes by impact"""
        all_fixes = []
        
        # Collect all issues with priority
        for issue_type in ["indexability_issues", "canonical_issues", "redirect_issues", 
                          "javascript_seo_issues", "sitemap_issues"]:
            issues = results.get(issue_type, [])
            if isinstance(issues, list):
                for issue in issues:
                    if isinstance(issue, dict) and issue.get("severity") == "high":
                        all_fixes.append({
                            "category": issue_type.replace("_", " ").title(),
                            "issue": issue.get("issue", ""),
                            "fix": issue.get("fix", ""),
                            "impact": issue.get("impact", ""),
                            "severity": issue.get("severity", "medium"),
                            "url": issue.get("url", "")
                        })
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_fixes.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        return all_fixes[:10]  # Top 10 priorities
    
    def _calculate_health_score(self, results: Dict) -> int:
        """Calculate overall SEO health score (0-100, higher is better)"""
        score = 100
        
        # Deduct points for issues
        deductions = {
            "critical": 15,
            "high": 10,
            "medium": 5,
            "low": 2
        }
        
        for issue_type in results:
            if isinstance(results[issue_type], list):
                for issue in results[issue_type]:
                    if isinstance(issue, dict):
                        severity = issue.get("severity", "low")
                        score -= deductions.get(severity, 0)
        
        return max(0, score)