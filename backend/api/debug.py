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
    
    def detect_environment_mode(self) -> ServiceMode:
        """Detect current environment mode - all vendors use mock implementations."""
        # All vendors currently use mock implementations regardless of credentials
        return ServiceMode.MOCK
    
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
            
            vendor_info = {
                "name": vendor_config.get("name", vendor_name),
                "type": vendor_config.get("type", "unknown"),
                "enabled": vendor_config.get("enabled", False),
                "has_credentials": has_key,
                "mode": "mock",  # All vendors use mock implementations
                "features": vendor_config.get("features", [])
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
        environment_mode = self.detect_environment_mode()
        vendor_status = self.get_vendor_status()
        
        # Demo readiness calculation
        demo_ready = self._calculate_demo_readiness(
            services_status, vendor_status, overall_health
        )
        
        return {
            "project": self.config.get("project", {}),
            "timestamp": time.time(),
            "overall_health": overall_health,
            "environment_mode": environment_mode,
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
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()

# Global debug service instance
debug_service = DebugService()