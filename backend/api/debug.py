"""
Debug endpoint for system health checks and monitoring.
Provides comprehensive status information for hackathon demos.
"""

import os
import yaml
import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"

class ServiceMode(str, Enum):
    MOCK = "mock"
    LIVE = "live"
    HYBRID = "hybrid"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    response_time: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict] = None

@dataclass
class ServiceStatus:
    name: str
    type: str
    status: HealthStatus
    url: str
    response_time: Optional[float] = None
    features: List[Dict] = None
    error: Optional[str] = None

class DebugService:
    def __init__(self):
        self.config = self._load_config()
        self.session: Optional[aiohttp.ClientSession] = None
    
    def _load_config(self) -> Dict:
        """Load debug configuration from YAML file."""
        # Try multiple possible paths
        possible_paths = [
            Path("/app/config/debug.yaml"),  # Docker volume mount
            Path(__file__).parent.parent.parent / "config" / "debug.yaml",
            Path("./config/debug.yaml"),
            Path("/config/debug.yaml")
        ]
        
        for config_path in possible_paths:
            try:
                if config_path.exists():
                    with open(config_path, 'r') as file:
                        logger.info(f"Loaded debug config from: {config_path}")
                        return yaml.safe_load(file)
            except Exception as e:
                logger.debug(f"Failed to load config from {config_path}: {e}")
                continue
        
        logger.warning("No debug config found, using defaults")
        return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration if YAML file is not available."""
        return {
            "project": {
                "name": "Hack Stack Demo",
                "description": "Modern hackathon demo stack",
                "version": "1.0.0"
            },
            "services": {},
            "vendors": {},
            "environment": {"detection": {"indicators": []}}
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _check_http_endpoint(self, url: str, endpoint: str = "/", 
                                 expected_status: int = 200, 
                                 timeout: float = 5.0) -> HealthCheck:
        """Check HTTP endpoint health."""
        full_url = f"{url.rstrip('/')}{endpoint}"
        start_time = time.time()
        
        try:
            session = await self._get_session()
            async with session.get(full_url) as response:
                response_time = time.time() - start_time
                
                if response.status == expected_status:
                    return HealthCheck(
                        name=full_url,
                        status=HealthStatus.HEALTHY,
                        response_time=response_time
                    )
                else:
                    return HealthCheck(
                        name=full_url,
                        status=HealthStatus.UNHEALTHY,
                        response_time=response_time,
                        error=f"HTTP {response.status}"
                    )
        except asyncio.TimeoutError:
            return HealthCheck(
                name=full_url,
                status=HealthStatus.UNHEALTHY,
                error="Timeout"
            )
        except Exception as e:
            return HealthCheck(
                name=full_url,
                status=HealthStatus.UNHEALTHY,
                error=str(e)
            )
    
    async def check_service_health(self, service_name: str, service_config: Dict) -> ServiceStatus:
        """Check health of a specific service."""
        # Handle self-service (backend) to avoid circular requests
        if service_config.get("self_service", False):
            return ServiceStatus(
                name=service_config["name"],
                type=service_config["type"],
                status=HealthStatus.HEALTHY,  # If we're running, we're healthy
                url=service_config["url"],
                response_time=0.001,  # Instant self-check
                features=service_config.get("features", []),
                error=None
            )
        
        health_config = service_config.get("health_check", {})
        endpoint = health_config.get("endpoint", "/")
        expected_status = health_config.get("expected_status", 200)
        timeout = health_config.get("timeout", 5)
        
        check = await self._check_http_endpoint(
            service_config["url"], 
            endpoint, 
            expected_status, 
            timeout
        )
        
        return ServiceStatus(
            name=service_config["name"],
            type=service_config["type"],
            status=check.status,
            url=service_config["url"],
            response_time=check.response_time,
            features=service_config.get("features", []),
            error=check.error
        )
    
    def detect_environment_mode(self) -> Dict[str, Any]:
        """Calculate dynamic integration metrics instead of simple mode."""
        vendors = self.config.get("vendors", {})
        
        total_vendors = len(vendors)
        fully_integrated = 0
        partially_integrated = 0
        mock_only = 0
        credentials_ready = 0
        total_credentials = 0
        available_credentials = 0
        
        for vendor_name, vendor_config in vendors.items():
            status = self._detect_actual_integration_status(vendor_name, vendor_config, False)
            
            if status == "fully_integrated":
                fully_integrated += 1
            elif status in ["partial_live", "partial_mock_missing_keys", "partial_mock_dependencies", "credentials_ready_untested"]:
                partially_integrated += 1
            else:
                mock_only += 1
            
            # Count credentials
            env_var = vendor_config.get("env_var")
            if env_var:
                total_credentials += 1
                if os.getenv(env_var):
                    available_credentials += 1
            
            # Special handling for Weaviate (needs both URL and key)
            if vendor_name == "weaviate":
                total_credentials += 1  # Add URL requirement (API key already counted above)
                if os.getenv("WEAVIATE_URL"):
                    available_credentials += 1
        
        # Calculate percentages
        integration_percentage = ((fully_integrated + (partially_integrated * 0.5)) / total_vendors * 100) if total_vendors > 0 else 0
        credential_percentage = (available_credentials / total_credentials * 100) if total_credentials > 0 else 0
        
        # Collect specific missing items
        missing_details = self._get_missing_integration_details(vendors)
        
        return {
            "integration_score": round(integration_percentage, 1),
            "credential_score": round(credential_percentage, 1),
            "vendor_breakdown": {
                "total": total_vendors,
                "fully_integrated": fully_integrated,
                "partially_integrated": partially_integrated,
                "mock_only": mock_only
            },
            "credential_breakdown": {
                "total_required": total_credentials,
                "available": available_credentials,
                "missing": total_credentials - available_credentials
            },
            "missing_details": missing_details,
            "overall_status": self._calculate_overall_status(integration_percentage, credential_percentage)
        }
    
    def _calculate_overall_status(self, integration_percentage: float, credential_percentage: float) -> str:
        """Calculate overall integration status based on metrics."""
        avg_score = (integration_percentage + credential_percentage) / 2
        
        if avg_score >= 90:
            return "production_ready"
        elif avg_score >= 70:
            return "development_ready"
        elif avg_score >= 40:
            return "partial_integration"
        elif avg_score >= 20:
            return "basic_setup"
        else:
            return "demo_mode"
    
    def _get_missing_integration_details(self, vendors: Dict) -> Dict[str, Any]:
        """Get specific details about what's missing for each vendor."""
        missing_credentials = []
        partially_integrated = []
        mock_only_vendors = []
        
        for vendor_name, vendor_config in vendors.items():
            env_var = vendor_config.get("env_var")
            status = self._detect_actual_integration_status(vendor_name, vendor_config, False)
            
            vendor_display_name = vendor_config.get("name", vendor_name)
            
            # Collect missing credentials
            if env_var and not os.getenv(env_var):
                missing_credentials.append({
                    "vendor": vendor_display_name,
                    "env_var": env_var,
                    "description": f"{vendor_display_name} API key"
                })
            
            # Special handling for Weaviate URL
            if vendor_name == "weaviate" and not os.getenv("WEAVIATE_URL"):
                missing_credentials.append({
                    "vendor": vendor_display_name,
                    "env_var": "WEAVIATE_URL",
                    "description": f"{vendor_display_name} instance URL"
                })
            
            # Categorize vendors by integration status
            if status in ["partial_live", "partial_mock_missing_keys", "partial_mock_dependencies", "credentials_ready_untested"]:
                reason = self._get_partial_integration_reason(vendor_name, status)
                partially_integrated.append({
                    "vendor": vendor_display_name,
                    "status": status,
                    "reason": reason
                })
            elif status in ["mock_only", "mock_missing_all"]:
                mock_only_vendors.append({
                    "vendor": vendor_display_name,
                    "reason": "No live integration implemented" if status == "mock_only" else "Missing all credentials"
                })
        
        return {
            "missing_credentials": missing_credentials,
            "partially_integrated": partially_integrated,
            "mock_only_vendors": mock_only_vendors
        }
    
    def _get_partial_integration_reason(self, vendor_name: str, status: str) -> str:
        """Get human-readable reason for partial integration."""
        if status == "partial_mock_missing_keys":
            if vendor_name == "llamaindex":
                return "Missing LLAMA_CLOUD_API_KEY (has OpenAI)"
            else:
                return "Missing API keys"
        elif status == "partial_mock_dependencies":
            return "Has API keys but missing dependencies"
        elif status == "credentials_ready_untested":
            return "Has credentials but live connection untested"
        elif status == "partial_live":
            return "Some components working, others failing"
        else:
            return "Unknown partial integration issue"
    
    def get_vendor_status(self) -> Dict[str, Dict]:
        """Get status of all configured vendors with security information."""
        from .services import get_config
        
        vendors = self.config.get("vendors", {})
        vendor_status = {}
        app_config = get_config()
        
        for vendor_name, vendor_config in vendors.items():
            env_var = vendor_config.get("env_var")
            has_key = bool(os.getenv(env_var)) if env_var else False
            
            # Get security information from app config
            vendor_creds = app_config.vendor_credentials.get(vendor_name)
            
            # Detect actual integration status
            actual_integration_status = self._detect_actual_integration_status(vendor_name, vendor_config, has_key)
            
            vendor_info = {
                "name": vendor_config.get("name", vendor_name),
                "type": vendor_config.get("type", "unknown"),
                "enabled": vendor_config.get("enabled", False),
                "has_credentials": has_key,
                "mode": "mock",  # All vendors use mock implementations
                "features": vendor_config.get("features", []),
                "sponsor": vendor_config.get("sponsor", False),
                "sponsor_info": vendor_config.get("sponsor_info", {}),
                "integration_status": actual_integration_status,
                "configured_status": vendor_config.get("integration_status"),  # What's in config vs reality
                "status_details": self._get_integration_details(vendor_name, has_key)
            }
            
            # Add security information if available
            if vendor_creds:
                vendor_info.update({
                    "credential_source": vendor_creds.source,
                    "is_secure": vendor_creds.is_secure,
                    "security_warning": vendor_creds.warning
                })
            
            vendor_status[vendor_name] = vendor_info
        
        return vendor_status
    
    def _detect_actual_integration_status(self, vendor_name: str, vendor_config: Dict, has_credentials: bool) -> str:
        """Detect the actual integration status based on real capabilities."""
        
        if vendor_name == "llamaindex":
            # Check if LlamaParse/PDF service is actually working in live mode
            try:
                from services.pdf_processing_service import get_pdf_service
                pdf_service = get_pdf_service()
                service_status = pdf_service.get_service_status()
                
                # Check if we're in mock mode and why
                if service_status.get("mode") == "mock":
                    missing_keys = []
                    api_keys = service_status.get("api_keys_detected", {})
                    
                    if not api_keys.get("llama_cloud", False):
                        missing_keys.append("LLAMA_CLOUD_API_KEY")
                    if not api_keys.get("openai", False):
                        missing_keys.append("OPENAI_API_KEY")
                    
                    if missing_keys:
                        return "partial_mock_missing_keys"
                    else:
                        return "partial_mock_dependencies"
                else:
                    # Live mode - check if components are actually working
                    components = service_status.get("components", {})
                    if all(components.values()):
                        return "fully_integrated"
                    else:
                        return "partial_live"
                        
            except Exception as e:
                logger.debug(f"Error checking LlamaIndex status: {e}")
                return "integration_unknown"
        
        elif vendor_name == "weaviate":
            # Check Weaviate integration status
            try:
                weaviate_url = os.getenv("WEAVIATE_URL")
                weaviate_key = os.getenv("WEAVIATE_API_KEY")
                
                if not weaviate_url and not weaviate_key:
                    return "mock_missing_all"
                elif not weaviate_url:
                    return "partial_mock_missing_url"
                elif not weaviate_key:
                    return "partial_mock_missing_key"
                else:
                    # Both URL and key available - check if Weaviate is actually reachable
                    return "credentials_ready_untested"  # Could add actual connectivity test here
                    
            except Exception as e:
                logger.debug(f"Error checking Weaviate status: {e}")
                return "integration_unknown"
        
        # For other vendors, basic detection
        if has_credentials:
            return "credentials_only"
        else:
            return "mock_only"
    
    def _get_integration_details(self, vendor_name: str, has_credentials: bool) -> Dict[str, Any]:
        """Get detailed integration status information."""
        
        if vendor_name == "llamaindex":
            try:
                from services.pdf_processing_service import get_pdf_service
                pdf_service = get_pdf_service()
                service_status = pdf_service.get_service_status()
                
                return {
                    "mode": service_status.get("mode"),
                    "api_keys_detected": service_status.get("api_keys_detected", {}),
                    "dependencies_available": service_status.get("dependencies_available", {}),
                    "components_ready": service_status.get("components", {}),
                    "mock_businesses_available": service_status.get("configuration", {}).get("mock_businesses_available", 0)
                }
            except Exception as e:
                return {"error": str(e)}
        
        elif vendor_name == "weaviate":
            try:
                weaviate_url = os.getenv("WEAVIATE_URL")
                weaviate_key = os.getenv("WEAVIATE_API_KEY")
                
                return {
                    "mode": "mock",  # Currently always mock since no live Weaviate integration
                    "credentials_detected": {
                        "weaviate_url": bool(weaviate_url),
                        "weaviate_api_key": bool(weaviate_key)
                    },
                    "configuration": {
                        "weaviate_url": weaviate_url[:50] + "..." if weaviate_url and len(weaviate_url) > 50 else weaviate_url,
                        "has_api_key": bool(weaviate_key)
                    },
                    "integration_notes": "Vector database integration available but not yet implemented in live mode"
                }
            except Exception as e:
                return {"error": str(e)}
        
        return {
            "has_credentials": has_credentials,
            "mode": "mock"
        }
    
    async def run_all_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive health checks for all services."""
        services = self.config.get("services", {})
        
        # Run health checks for all services concurrently
        service_checks = []
        for service_name, service_config in services.items():
            service_checks.append(
                self.check_service_health(service_name, service_config)
            )
        
        if service_checks:
            service_results = await asyncio.gather(*service_checks, return_exceptions=True)
        else:
            service_results = []
        
        # Process results
        services_status = {}
        healthy_services = 0
        
        for i, result in enumerate(service_results):
            service_name = list(services.keys())[i]
            if isinstance(result, Exception):
                services_status[service_name] = ServiceStatus(
                    name=service_name,
                    type="unknown",
                    status=HealthStatus.UNHEALTHY,
                    url="unknown",
                    error=str(result)
                )
            else:
                services_status[service_name] = result
                if result.status == HealthStatus.HEALTHY:
                    healthy_services += 1
        
        # Calculate overall system health
        total_services = len(services)
        overall_health = HealthStatus.HEALTHY if healthy_services == total_services else \
                        HealthStatus.DEGRADED if healthy_services > 0 else \
                        HealthStatus.UNHEALTHY
        
        # Environment and vendor information
        integration_metrics = self.detect_environment_mode()
        vendor_status = self.get_vendor_status()
        
        # Demo readiness calculation
        demo_ready = self._calculate_demo_readiness(
            services_status, vendor_status, overall_health
        )
        
        return {
            "project": self.config.get("project", {}),
            "timestamp": time.time(),
            "overall_health": overall_health,
            "integration_metrics": integration_metrics,
            "demo_ready": demo_ready,
            "services": {
                name: {
                    "name": status.name,
                    "type": status.type,
                    "status": status.status,
                    "url": status.url,
                    "response_time": status.response_time,
                    "features": status.features,
                    "error": status.error
                }
                for name, status in services_status.items()
            },
            "vendors": vendor_status,
            "summary": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "total_vendors": len(vendor_status),
                "live_vendors": sum(1 for v in vendor_status.values() if v["mode"] == "live"),
                "mock_vendors": sum(1 for v in vendor_status.values() if v["mode"] == "mock")
            }
        }
    
    def _calculate_demo_readiness(self, services_status: Dict, 
                                vendor_status: Dict, overall_health: HealthStatus) -> Dict:
        """Calculate demo readiness score based on configured criteria."""
        criteria = self.config.get("demo_readiness", {}).get("criteria", [])
        if not criteria:
            return {"score": 100, "ready": True, "message": "No criteria configured"}
        
        score = 0
        max_score = sum(c.get("weight", 10) for c in criteria)
        checks = []
        
        for criterion in criteria:
            check_name = criterion["check"]
            weight = criterion.get("weight", 10)
            passed = False
            
            if check_name == "services_healthy":
                passed = overall_health in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            elif check_name == "api_responsive":
                backend_healthy = any(
                    s.type == "api" and s.status == HealthStatus.HEALTHY
                    for s in services_status.values()
                )
                passed = backend_healthy
            elif check_name == "frontend_healthy":
                frontend_healthy = any(
                    s.type == "web" and s.status == HealthStatus.HEALTHY
                    for s in services_status.values()
                )
                passed = frontend_healthy
            elif check_name == "vendor_available":
                passed = len(vendor_status) > 0
            elif check_name in ["llamaindex_available", "llamaindex_pdf_processing"]:
                # Check if LlamaIndex PDF processing is available
                try:
                    from services.pdf_processing_service import get_pdf_service
                    pdf_service = get_pdf_service()
                    status = pdf_service.get_service_status()
                    passed = status.get("dependencies_available", {}).get("llamaparse", False)
                except Exception:
                    passed = False
            
            if passed:
                score += weight
            
            checks.append({
                "name": criterion["name"],
                "passed": passed,
                "weight": weight
            })
        
        percentage = int((score / max_score) * 100) if max_score > 0 else 0
        ready = percentage >= 75  # 75% threshold for demo readiness
        
        return {
            "score": percentage,
            "ready": ready,
            "message": "Demo ready!" if ready else "Issues detected",
            "checks": checks
        }
    
    def auto_discover_endpoints(self, app: FastAPI) -> Dict[str, Any]:
        """Auto-discover all FastAPI endpoints from the application."""
        discovered_endpoints = []
        
        for route in app.routes:
            if isinstance(route, APIRoute):
                # Extract endpoint information
                endpoint_info = {
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name,
                    "summary": getattr(route, 'summary', None),
                    "description": route.description or "",
                    "tags": getattr(route, 'tags', []),
                    "auto_discovered": True
                }
                
                # Try to extract docstring from endpoint function
                if route.endpoint and hasattr(route.endpoint, '__doc__'):
                    doc = route.endpoint.__doc__
                    if doc:
                        endpoint_info["docstring"] = doc.strip()
                
                discovered_endpoints.append(endpoint_info)
        
        return {
            "total_discovered": len(discovered_endpoints),
            "endpoints": discovered_endpoints,
            "discovery_timestamp": time.time()
        }
    
    def organize_endpoints_by_sections(self, discovered_endpoints: List[Dict], yaml_config: Dict) -> Dict[str, Any]:
        """Organize endpoints into sections with YAML config override."""
        
        # Get configured sections from YAML
        sections_config = yaml_config.get("api_endpoints", {}).get("sections", {})
        primary_section = yaml_config.get("api_endpoints", {}).get("primary_section", "business_data")
        
        # Initialize sections
        organized_sections = {}
        endpoint_assignments = {}  # Track which endpoints are assigned
        
        # Process configured sections first
        for section_key, section_config in sections_config.items():
            if section_key == "untracked":
                continue  # Handle untracked separately
                
            section_info = {
                "name": section_config.get("name", section_key),
                "description": section_config.get("description", ""),
                "expanded": section_config.get("expanded", False),
                "is_primary": section_key == primary_section,
                "endpoints": []
            }
            
            # Match configured endpoints to discovered endpoints
            configured_endpoints = section_config.get("endpoints", [])
            for config_endpoint in configured_endpoints:
                config_path = config_endpoint.get("path", "")
                config_method = config_endpoint.get("method", "GET")
                
                # Find matching discovered endpoint
                matched = False
                for discovered in discovered_endpoints:
                    # Direct path match
                    if (discovered["path"] == config_path and 
                        config_method in discovered["methods"]):
                        
                        # Merge config with discovered data
                        endpoint_info = {
                            **discovered,
                            "priority": config_endpoint.get("priority", "medium"),
                            "request_body": config_endpoint.get("request_body"),
                            "configured": True
                        }
                        
                        section_info["endpoints"].append(endpoint_info)
                        endpoint_assignments[f"{config_path}:{config_method}"] = section_key
                        matched = True
                        break
                    
                    # Template path match (for configured concrete paths vs discovered templates)
                    display_path = config_endpoint.get("display_path")
                    if (display_path and discovered["path"] == display_path and 
                        config_method in discovered["methods"]):
                        
                        # Use configured concrete path but discovered metadata
                        endpoint_info = {
                            **discovered,
                            "path": config_path,  # Use concrete path for testing
                            "display_path": display_path,  # Keep template for display
                            "priority": config_endpoint.get("priority", "medium"),
                            "request_body": config_endpoint.get("request_body"),
                            "configured": True
                        }
                        
                        section_info["endpoints"].append(endpoint_info)
                        endpoint_assignments[f"{display_path}:{config_method}"] = section_key
                        matched = True
                        break
                
                # If no match found, create endpoint from config only
                if not matched:
                    endpoint_info = {
                        "path": config_path,
                        "display_path": config_endpoint.get("display_path"),
                        "methods": [config_method],
                        "name": config_endpoint.get("name", ""),
                        "description": config_endpoint.get("description", ""),
                        "priority": config_endpoint.get("priority", "medium"),
                        "request_body": config_endpoint.get("request_body"),
                        "configured": True,
                        "auto_discovered": False
                    }
                    section_info["endpoints"].append(endpoint_info)
            
            organized_sections[section_key] = section_info
        
        # Create untracked section for remaining endpoints
        untracked_endpoints = []
        for discovered in discovered_endpoints:
            # Check if this endpoint was assigned to any section
            assigned = False
            for method in discovered["methods"]:
                endpoint_key = f"{discovered['path']}:{method}"
                if endpoint_key in endpoint_assignments:
                    assigned = True
                    break
            
            if not assigned:
                untracked_endpoints.append({
                    **discovered,
                    "priority": "medium",
                    "configured": False
                })
        
        # Add untracked section if there are untracked endpoints
        if untracked_endpoints:
            organized_sections["untracked"] = {
                "name": "🔍 Untracked APIs",
                "description": "Recently discovered endpoints",
                "expanded": False,
                "is_primary": False,
                "endpoints": untracked_endpoints,
                "auto_populated": True
            }
        
        return {
            "sections": organized_sections,
            "primary_section": primary_section,
            "total_endpoints": len(discovered_endpoints),
            "configured_endpoints": sum(len(section["endpoints"]) for section in organized_sections.values() if not section.get("auto_populated", False)),
            "untracked_endpoints": len(untracked_endpoints),
            "organization_timestamp": time.time()
        }
    
    def get_api_endpoints_status(self, app: FastAPI) -> Dict[str, Any]:
        """Get comprehensive API endpoints status with auto-discovery and YAML config."""
        
        # Auto-discover endpoints
        discovery_result = self.auto_discover_endpoints(app)
        
        # Organize endpoints by sections with YAML config
        organized_result = self.organize_endpoints_by_sections(
            discovery_result["endpoints"], 
            self.config
        )
        
        # Calculate section statistics
        section_stats = {}
        for section_key, section_info in organized_result["sections"].items():
            section_stats[section_key] = {
                "total_endpoints": len(section_info["endpoints"]),
                "configured_endpoints": sum(1 for ep in section_info["endpoints"] if ep.get("configured", False)),
                "high_priority": sum(1 for ep in section_info["endpoints"] if ep.get("priority") == "high"),
                "is_primary": section_info.get("is_primary", False),
                "expanded": section_info.get("expanded", False)
            }
        
        return {
            "discovery": discovery_result,
            "organization": organized_result,
            "section_stats": section_stats,
            "summary": {
                "total_sections": len(organized_result["sections"]),
                "primary_section": organized_result["primary_section"],
                "endpoints_configured": organized_result["configured_endpoints"],
                "endpoints_untracked": organized_result["untracked_endpoints"],
                "auto_discovery_enabled": True
            }
        }

    async def cleanup(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()

# Global debug service instance
debug_service = DebugService()