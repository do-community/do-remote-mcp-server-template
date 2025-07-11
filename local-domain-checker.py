#!/usr/bin/env python3
"""
MCP Server for checking domain name availability using FastMCP 2.0
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
import whois
import dns.resolver
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("domain-checker")

# Create the FastMCP server
mcp = FastMCP(
    name="Domain Checker",
    instructions="When you are asked about domain availability or to check if a domain is available for registration, call the appropriate function."
)

class DomainChecker:
    """Domain availability checker with multiple verification methods"""
    
    def __init__(self):
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 10
    
    async def check_domain_availability(self, domain: str) -> Dict[str, Any]:
        """Check if a domain is available using multiple methods"""
        results = {
            "domain": domain,
            "available": None,
            "whois_available": None,
            "dns_resolvable": None,
            "error": None,
            "details": {}
        }
        
        try:
            # Method 1: WHOIS lookup
            whois_result = await self._check_whois(domain)
            results["whois_available"] = whois_result["available"]
            results["details"]["whois"] = whois_result
            
            # Method 2: DNS resolution check
            dns_result = await self._check_dns_resolution(domain)
            results["dns_resolvable"] = dns_result["resolvable"]
            results["details"]["dns"] = dns_result
            
            # Determine overall availability
            if results["whois_available"] is True and results["dns_resolvable"] is False:
                results["available"] = True
            elif results["whois_available"] is False:
                results["available"] = False
            else:
                results["available"] = None
                
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"Error checking domain {domain}: {e}")
        
        return results
    
    async def _check_whois(self, domain: str) -> Dict[str, Any]:
        """Check domain availability using WHOIS"""
        try:
            loop = asyncio.get_event_loop()
            whois_data = await loop.run_in_executor(None, whois.whois, domain)
            
            if whois_data is None:
                return {"available": True, "reason": "No WHOIS data found"}
            
            if hasattr(whois_data, 'status') and whois_data.status:
                return {
                    "available": False, 
                    "reason": "Domain has active status",
                    "status": whois_data.status,
                    "registrar": getattr(whois_data, 'registrar', None),
                    "creation_date": str(getattr(whois_data, 'creation_date', None))
                }
            
            if hasattr(whois_data, 'registrar') and whois_data.registrar:
                return {
                    "available": False,
                    "reason": "Domain has registrar",
                    "registrar": whois_data.registrar
                }
            
            return {
                "available": None,
                "reason": "WHOIS data exists but unclear status",
                "raw_data": str(whois_data)[:500]
            }
            
        except whois.parser.PywhoisError as e:
            return {"available": True, "reason": f"WHOIS parser error: {str(e)}"}
        except Exception as e:
            return {"available": None, "reason": f"WHOIS lookup failed: {str(e)}"}
    
    async def _check_dns_resolution(self, domain: str) -> Dict[str, Any]:
        """Check if domain resolves via DNS"""
        try:
            loop = asyncio.get_event_loop()
            
            def resolve_dns():
                try:
                    answers = self.dns_resolver.resolve(domain, 'A')
                    return [str(answer) for answer in answers]
                except dns.resolver.NXDOMAIN:
                    return None
                except Exception as e:
                    raise e
            
            a_records = await loop.run_in_executor(None, resolve_dns)
            
            if a_records:
                return {
                    "resolvable": True,
                    "a_records": a_records,
                    "reason": "Domain resolves to IP addresses"
                }
            else:
                return {
                    "resolvable": False,
                    "reason": "Domain does not resolve (NXDOMAIN)"
                }
                
        except Exception as e:
            return {
                "resolvable": None,
                "reason": f"DNS lookup failed: {str(e)}"
            }

# Initialize domain checker
domain_checker = DomainChecker()

@mcp.tool()
async def check_domain(domain: str) -> str:
    """Check if a single domain name is available for registration"""
    result = await domain_checker.check_domain_availability(domain)
    
    # Format the response nicely
    if result["available"] is True:
        status = "✅ LIKELY AVAILABLE"
    elif result["available"] is False:
        status = "❌ NOT AVAILABLE"
    else:
        status = "❓ UNCLEAR"
    
    response = f"""Domain: {domain}
Status: {status}

WHOIS Check: {'Available' if result['whois_available'] else 'Registered' if result['whois_available'] is False else 'Unclear'}
DNS Resolution: {'Not resolving' if result['dns_resolvable'] is False else 'Resolving' if result['dns_resolvable'] else 'Error'}

Details:
{json.dumps(result['details'], indent=2)}
"""
    
    if result["error"]:
        response += f"\nError: {result['error']}"
    
    return response

@mcp.tool()
async def check_multiple_domains(domains: List[str]) -> str:
    """Check availability for multiple domain names at once"""
    if not domains:
        return "Error: Domain list is required"
    
    # Check domains concurrently
    tasks = [domain_checker.check_domain_availability(domain) for domain in domains]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions in the results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "domain": domains[i],
                "available": None,
                "error": str(result)
            })
        else:
            processed_results.append(result)
    
    # Format results as a table
    response = "Domain Availability Check Results:\n\n"
    for result in processed_results:
        if result["available"] is True:
            status = "✅ LIKELY AVAILABLE"
        elif result["available"] is False:
            status = "❌ NOT AVAILABLE"
        else:
            status = "❓ UNCLEAR"
        
        response += f"{result['domain']:<30} {status}\n"
    
    response += f"\nDetailed results:\n{json.dumps(processed_results, indent=2)}"
    
    return response

@mcp.resource("domain://check/{domain}")
async def domain_info_resource(domain: str) -> str:
    """Get domain availability information as a resource"""
    result = await domain_checker.check_domain_availability(domain)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    mcp.run()