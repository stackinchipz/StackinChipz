from signalos.scoring.convergence import compute_convergence_score
import pandas as pd


def test_convergence_score_bounds():
    # Convergence now has 8 components (added the fundamental conviction layer:
    # power_gauge_score + capital_efficiency_score). All maxed -> 100.
    row = pd.Series({
        "uoa_score": 100,
        "money_flow_score": 100,
        "trend_score": 100,
        "rs_score": 100,
        "liquidity_score": 100,
        "catalyst_score": 100,
        "power_gauge_score": 100,
        "capital_efficiency_score": 100,
    })
    assert compute_convergence_score(row) == 100

    # Without the fundamental layer present, the original six components cap the
    # score at their summed weight (the layer simply contributes 0).
    partial = pd.Series({
        "uoa_score": 100, "money_flow_score": 100, "trend_score": 100,
        "rs_score": 100, "liquidity_score": 100, "catalyst_score": 100,
    })
    assert compute_convergence_score(partial) == 80
