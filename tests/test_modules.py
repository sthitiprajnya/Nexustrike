from evaluation.asymptotic_scorer import NeverPerfectEvaluator
from memory.compressed_learning import CompressedKnowledgeBase
from reporting.html_dashboard import HTMLDashboardGenerator


def test_scorer_output_shape():
    evaluator = NeverPerfectEvaluator()
    result = evaluator.calculate_engagement_score({})
    assert "overall" in result
    assert result["overall"] <= 0.97


def test_compressed_knowledge_roundtrip(tmp_path):
    db_path = tmp_path / "mem.db"
    kb = CompressedKnowledgeBase(str(db_path))
    kb.store_engagement_learning({"id": "1", "target": "example.com", "tech_stack": ["fastapi"]})
    data = kb.retrieve_relevant_knowledge({"tech_stack": ["fastapi"]})
    assert len(data) >= 1


def test_html_report_contains_doctype():
    html = HTMLDashboardGenerator().generate({"target": "example.com", "vulns": {}})
    assert "<!DOCTYPE html>" in html
