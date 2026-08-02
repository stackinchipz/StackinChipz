"""Preflight: verify credentials and connectivity before running the pipeline.

Run this first — it tells you exactly which credential is wrong, instead of
letting the full pipeline fail somewhere in the middle.

    set -a; source .env; set +a
    python scripts/check_setup.py

Checks (each independent; a failure never aborts the rest):
  1. Tradier token valid + account reachable + market clock
  2. Tradier account id matches an account on the token
  3. Options approval level (needed for spreads)
  4. SEC EDGAR reachable with your User-Agent
  5. Databento package + key present (no billable query is made)
"""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OK, BAD, WARN = "✅", "❌", "⚠️ "


def _mask(s: str | None) -> str:
    if not s:
        return "(unset)"
    return f"{s[:4]}...{s[-4:]} ({len(s)} chars)"


def check_tradier() -> bool:
    import requests
    token = os.getenv("TRADIER_TOKEN")
    acct = os.getenv("TRADIER_ACCOUNT_ID")
    env = os.getenv("TRADIER_ENV", "sandbox").lower()
    base = "https://api.tradier.com/v1" if env == "live" else "https://sandbox.tradier.com/v1"

    print(f"\n-- Tradier ({env}) --")
    print(f"   token   : {_mask(token)}")
    print(f"   account : {acct or '(unset)'}")
    if not token:
        print(f"{BAD} TRADIER_TOKEN not set.")
        return False

    h = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    try:
        r = requests.get(f"{base}/user/profile", headers=h, timeout=20)
    except Exception as e:
        print(f"{BAD} Cannot reach {base} ({e}). Network blocked or offline?")
        return False

    if r.status_code == 401:
        print(f"{BAD} 401 Unauthorized — token rejected. Wrong token, or a live "
              f"token used with TRADIER_ENV=sandbox (or vice versa).")
        return False
    if r.status_code >= 400:
        print(f"{BAD} HTTP {r.status_code}: {r.text[:200]}")
        return False

    print(f"{OK} Token accepted by {base}")

    # Account match + options approval.
    try:
        profile = r.json().get("profile", {})
        accounts = profile.get("account", [])
        if isinstance(accounts, dict):
            accounts = [accounts]
        numbers = [a.get("account_number") for a in accounts]
        print(f"   accounts on token: {', '.join(str(n) for n in numbers) or '(none)'}")
        if acct and acct not in numbers:
            print(f"{WARN}TRADIER_ACCOUNT_ID '{acct}' is not in that list — orders will fail.")
        elif acct:
            print(f"{OK} Account {acct} matches this token")
        for a in accounts:
            if a.get("account_number") == acct:
                lvl = a.get("option_level")
                if lvl is None:
                    print(f"{WARN}No option_level reported.")
                elif int(lvl) >= 3:
                    print(f"{OK} Option level {lvl} — spreads permitted")
                else:
                    print(f"{WARN}Option level {lvl} — spreads usually need 3+. "
                          "Request an upgrade in Tradier.")
    except Exception as e:
        print(f"{WARN}Could not parse profile accounts ({e}).")

    # Market data sanity check.
    try:
        q = requests.get(f"{base}/markets/quotes", headers=h,
                         params={"symbols": "AAPL"}, timeout=20)
        quote = q.json().get("quotes", {}).get("quote")
        if quote:
            print(f"{OK} Market data works (AAPL last = {quote.get('last')})")
        else:
            print(f"{WARN}Quote endpoint returned no data (sandbox data is delayed/limited).")
    except Exception as e:
        print(f"{WARN}Quote check failed ({e}).")
    return True


def check_edgar() -> bool:
    import requests
    ua = os.getenv("EDGAR_USER_AGENT")
    print("\n-- SEC EDGAR (fundamentals, free) --")
    if not ua:
        print(f"{WARN}EDGAR_USER_AGENT not set. SEC requires a descriptive "
              "User-Agent with your email.")
        return False
    try:
        r = requests.get("https://data.sec.gov/api/xbrl/companyconcept/"
                         "CIK0000320193/us-gaap/Revenues.json",
                         headers={"User-Agent": ua}, timeout=20)
        if r.status_code == 200:
            print(f"{OK} EDGAR reachable as '{ua}'")
            return True
        print(f"{BAD} EDGAR HTTP {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"{BAD} Cannot reach data.sec.gov ({e}).")
    return False


def check_databento() -> bool:
    print("\n-- Databento OPRA (optional, paid) --")
    key = os.getenv("DATABENTO_API_KEY")
    try:
        import databento  # noqa: F401
        print(f"{OK} databento package installed")
    except ImportError:
        print(f"{WARN}databento not installed (pip install databento). "
              "Engine falls back to Tradier placeholder flow.")
        return False
    if not key:
        print(f"{WARN}DATABENTO_API_KEY not set — real ask-side flow disabled.")
        return False
    print(f"{OK} API key present: {_mask(key)} (no billable query made)")
    return True


def main():
    print("=" * 62)
    print("SignalOS preflight")
    print("=" * 62)
    tradier = check_tradier()
    check_edgar()
    check_databento()
    print("\n" + "=" * 62)
    if tradier:
        print(f"{OK} Ready. Next: python scripts/run_live.py --preview 5")
    else:
        print(f"{BAD} Fix Tradier credentials above, then re-run this check.")
    print("=" * 62)
    return 0 if tradier else 1


if __name__ == "__main__":
    raise SystemExit(main())
