import textwrap

from prisma.screening.engine import Decision, load_rules, screen_record

RULES_YAML = """
name: test-ruleset
description: minimal ruleset for tests
exclusion:
  - id: R-MED
    code: EC-MED
    description: Medical topic
    pattern: "\\\\b(covid|pandemic|cancer)\\\\b"
    search_in: both
inclusion:
  require_all_of: [signal, kpi]
  groups:
    signal:
      description: Digital signal
      rules:
        - id: I-S1
          code: IC-SIGNAL
          description: Search data
          pattern: "google trends|search volume"
          search_in: both
    kpi:
      description: Business KPI
      rules:
        - id: I-K1
          code: IC-KPI
          description: Sales / demand
          pattern: "sales|demand|revenue"
          search_in: both
"""


def test_load_rules_and_screen(tmp_path):
    p = tmp_path / "rules.yaml"
    p.write_text(textwrap.dedent(RULES_YAML), encoding="utf-8")
    rs = load_rules(p)
    assert rs.require_all_of == ["signal", "kpi"]

    r = screen_record(
        "doc1",
        "Forecasting retail sales with Google Trends",
        "We use search volume to forecast monthly demand.",
        rs,
    )
    assert r.decision == Decision.INCLUDE

    excluded = screen_record(
        "doc2",
        "Google Trends and COVID-19 cases",
        "We model pandemic data using search volume.",
        rs,
    )
    assert excluded.decision == Decision.EXCLUDE

    maybe = screen_record(
        "doc3",
        "Forecasting retail sales",
        "Pure macroeconomic study, no online data.",
        rs,
    )
    # missing 1 group -> MAYBE per current threshold
    assert maybe.decision in {Decision.MAYBE, Decision.EXCLUDE}
    assert "signal" in maybe.missing_groups
