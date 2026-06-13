import pandas as pd


def suggest_structure(row: pd.Series) -> str:
    decision = row.get("decision", "")
    bias = row.get("bias", "")
    iv = float(row.get("implied_volatility", 0.0) or 0.0)
    dte = float(row.get("days_to_expiration", 0.0) or 0.0)
    spread_pct = float(row.get("spread_pct", 1.0) or 1.0)

    if decision not in {"A+ setup", "Tradable"}:
        return "No trade"

    if spread_pct > 0.18:
        return "No trade - spread too wide"

    if bias == "Bullish":
        if iv > 0.70 or dte < 21:
            return "Call debit spread"
        return "Long call or call debit spread"

    if bias == "Bearish":
        if iv > 0.70 or dte < 21:
            return "Put debit spread"
        return "Long put or put debit spread"

    return "No trade"


def suggested_risk_rules(row: pd.Series) -> str:
    if row.get("decision", "") not in {"A+ setup", "Tradable"}:
        return "N/A"
    return "Risk 0.25%-1.00% of account; target +75%-150%; stop -40%-60%; avoid holding through earnings unless intentional."
