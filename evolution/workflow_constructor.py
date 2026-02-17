from __future__ import annotations

from dataclasses import dataclass
from typing import List
from urllib.parse import urlparse


@dataclass
class Source:
    title: str
    url: str
    content: str


class InternetWorkflowEngine:
    authority_domains = {
        "owasp.org": 1.0,
        "portswigger.net": 0.95,
        "hackerone.com": 0.9,
        "github.com": 0.85,
        "mitre.org": 1.0,
        "nist.gov": 1.0,
    }

    async def search_internet(self, queries: List[str]) -> List[Source]:
        return [Source(title=q, url="https://owasp.org", content=f"Methodology for {q}") for q in queries]

    def calculate_authority(self, source: Source) -> float:
        domain = urlparse(source.url).netloc
        return self.authority_domains.get(domain, 0.5)

    async def construct_pentest_workflow(self, target_type: str, tech_stack: List[str]):
        queries = [
            f"{target_type} penetration testing methodology",
            f"OWASP {target_type} testing guide",
            f"{' '.join(tech_stack)} security assessment",
        ]
        sources = await self.search_internet(queries)
        ordered = sorted(sources, key=self.calculate_authority, reverse=True)
        return {
            "target_type": target_type,
            "tech_stack": tech_stack,
            "phases": ["recon", "mapping", "validation", "reporting"],
            "sources": [s.title for s in ordered],
        }
