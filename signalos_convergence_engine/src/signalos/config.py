from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScannerConfig:
    # --- Options-flow convergence (original engine) ---
    min_uoa_score: float = 70.0
    strong_uoa_score: float = 85.0
    min_money_flow_score: float = 70.0
    strong_money_flow_score: float = 80.0
    min_liquidity_score: float = 60.0

    bullish_cmf_confirm: float = 0.10
    bullish_cmf_strong: float = 0.20
    bearish_cmf_confirm: float = -0.10
    bearish_cmf_strong: float = -0.20

    max_option_spread_pct: float = 0.18
    preferred_max_option_spread_pct: float = 0.10
    min_open_interest: int = 100
    min_option_volume: int = 50
    min_premium_traded: float = 100_000

    convergence_weights: dict = field(default_factory=lambda: {
        "uoa_score": 0.30,
        "money_flow_score": 0.20,
        "trend_score": 0.10,
        "rs_score": 0.08,
        "liquidity_score": 0.07,
        "catalyst_score": 0.05,
        # New fundamental conviction layer (Chaikin Power Gauge + capital efficiency):
        "power_gauge_score": 0.10,
        "capital_efficiency_score": 0.10,
    })

    # --- Capital efficiency / Uniform-Accounting-lite (UAFRS approximation) ---
    # NOTE: This is a PUBLIC APPROXIMATION of the Uniform Accounting framework,
    # not the proprietary Valens/New Constructs model. It reconstructs adjusted
    # economics from raw filings to reduce common GAAP distortions.
    assumed_tax_rate: float = 0.21
    cost_of_capital: float = 0.09          # WACC proxy; ROIIC above this = value creation
    rd_amortization_years: int = 5         # straight-line capitalization of R&D
    excess_cash_pct_of_revenue: float = 0.02  # cash above this is treated as non-operating
    roiic_lookback_years: int = 3
    compounder_min_uniform_roa: float = 0.12
    compounder_min_roiic: float = 0.12
    compounder_min_capex_to_depreciation: float = 1.1
    destroyer_max_roiic: float = 0.05

    # --- Implied-volatility regime (options structure selection) ---
    iv_rank_low: float = 25.0     # below -> favor long premium / debit
    iv_rank_high: float = 60.0    # above -> favor defined-risk credit
    iv_rank_extreme: float = 80.0
    earnings_block_dte: int = 7   # block long premium within N days of earnings

    # --- Risk engine ---
    account_size: float = 100_000.0
    max_risk_per_trade_pct: float = 0.0100   # 1.0% of account at risk per position
    aplus_risk_per_trade_pct: float = 0.0150 # allow up to 1.5% on A+ setups (aggressive)
    max_portfolio_heat_pct: float = 0.0600   # total open risk cap (6% of account)
    max_positions: int = 12
    max_sector_heat_pct: float = 0.0300      # per-sector open-risk cap
    daily_drawdown_kill_pct: float = 0.0400  # halt new entries past -4% on the day

    # Chaikin Power Gauge bucket weights (Financials, Earnings, Technicals, Experts)
    power_gauge_weights: dict = field(default_factory=lambda: {
        "financials": 0.30,
        "earnings": 0.30,
        "technicals": 0.25,
        "experts": 0.15,
    })


DEFAULT_CONFIG = ScannerConfig()
