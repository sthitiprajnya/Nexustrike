from __future__ import annotations

import math
import random
from typing import Dict


class NeverPerfectEvaluator:
    def __init__(self, theoretical_max: float = 0.97, inject_challenge_probability: float = 0.03):
        self.theoretical_max = theoretical_max
        self.inject_challenge_probability = inject_challenge_probability

    @staticmethod
    def asymptotic_transform(value: float, max_achievable: float) -> float:
        k = 0.05
        return max_achievable * (1 - math.exp(-k * value))

    def get_metric_max(self, metric: str) -> float:
        return {
            "coverage": 0.97,
            "accuracy": 0.96,
            "depth": 0.95,
            "exploitation": 0.94,
            "innovation": 0.93,
            "efficiency": 0.92,
        }.get(metric, 0.9)

    def identify_improvement_areas(self, scores: Dict[str, float]):
        return [k for k, v in scores.items() if v < 0.8]

    def calculate_engagement_score(self, engagement_data: Dict) -> Dict:
        raw_scores = engagement_data.get(
            "raw_scores",
            {"coverage": 80, "accuracy": 80, "depth": 80, "exploitation": 80, "innovation": 80, "efficiency": 80},
        )
        asymptotic_scores = {
            metric: self.asymptotic_transform(raw, self.get_metric_max(metric))
            for metric, raw in raw_scores.items()
        }
        weights = {
            "coverage": 0.20,
            "accuracy": 0.25,
            "depth": 0.15,
            "exploitation": 0.20,
            "innovation": 0.10,
            "efficiency": 0.10,
        }
        composite_score = sum(asymptotic_scores[k] * weights[k] for k in weights)
        final_score = min(composite_score, self.theoretical_max)

        challenge_injected = random.random() < self.inject_challenge_probability
        if challenge_injected:
            final_score *= 0.92

        return {
            "overall": final_score,
            "breakdown": asymptotic_scores,
            "improvement_areas": self.identify_improvement_areas(asymptotic_scores),
            "challenge_injected": challenge_injected,
        }
