from app.genai_core.query_router import QueryRouter


def test_rule_based_routes_missing_values_to_null_tool():
    router = QueryRouter(client=object())

    decision = router.rule_based("Show missing values in the data")

    assert decision is not None
    assert decision["route"] == "data_tools"
    assert decision["tool"] == "null_values"


def test_rule_based_routes_outliers_to_outlier_tool():
    router = QueryRouter(client=object())

    decision = router.rule_based("Find anomalies and outliers in price")

    assert decision is not None
    assert decision["route"] == "data_tools"
    assert decision["tool"] == "outliers"


def test_rule_based_routes_profile_to_select_star_tool():
    router = QueryRouter(client=object())

    decision = router.rule_based("Profile this table")

    assert decision is not None
    assert decision["route"] == "data_tools"
    assert decision["tool"] == "select_star"


def test_rule_based_routes_normal_count_to_database():
    router = QueryRouter(client=object())

    decision = router.rule_based("Count orders by customer")

    assert decision is not None
    assert decision["route"] == "database"
    assert decision["tool"] is None


def test_parse_llm_data_tools_json():
    router = QueryRouter(client=object())

    decision = router._parse_llm_decision(
        '{"route": "data_tools", "tool": "select_star", "reason": "profile request"}'
    )

    assert decision == {
        "route": "data_tools",
        "tool": "select_star",
        "reason": "profile request",
    }


def test_parse_llm_invalid_output_falls_back_to_database():
    router = QueryRouter(client=object())

    decision = router._parse_llm_decision("not json")

    assert decision["route"] == "database"
    assert decision["tool"] is None
