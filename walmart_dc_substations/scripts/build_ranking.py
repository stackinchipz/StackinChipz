#!/usr/bin/env python3
"""
build_ranking.py — rank Walmart US distribution centers by likelihood of usable
substation capacity for a 10–20 MW Megapod deployment.

Inputs
  data/dc_roster.csv            merged DC roster (one row per facility, cited)
  data/hifld_substations.csv    HIFLD Electric Substations (substations only)
  data/retail_utilities.json    HIFLD retail-territory id -> utility name (optional)
  data/known_dedicated_subs.csv cited, press-confirmed dedicated substations that
                                post-date the HIFLD vintage (e.g. Belvidere, IL)
  data/dc_geocoded.json         geocode cache (created/updated by this script)

Outputs
  out/walmart-dc-substations.csv
  out/walmart-dc-substations.md

Geocoding: the session cannot reach Nominatim or the Census geocoder, so every
DC is geocoded OFFLINE to a ZIP-code centroid (python `zipcodes` package) or, if
no ZIP is known, to the city centroid (python `geonamescache`). Precision is
recorded per row and the on-parcel flag is only asserted at address precision.
"""
import csv, json, math, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "out")

# ----------------------------------------------------------------- helpers
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def voltage_weight(kv):
    if kv is None:
        return 0
    if kv >= 345:
        return 5
    if kv >= 230:
        return 4
    if kv >= 115:
        return 3
    if kv >= 69:
        return 2
    return 1


def proximity_weight(km):
    if km is None:
        return 0
    if km < 0.4:
        return 3
    if km < 0.8:
        return 2
    if km < 3.0:
        return 1
    return 0


def to_int(s):
    if s is None:
        return None
    s = str(s).strip().replace(",", "")
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None


# ----------------------------------------------------------------- geocoding
def geocode(row, cache):
    """Offline geocode. Returns (lat, lon, precision, note)."""
    key = f"{row.get('address','')}|{row['city']}|{row['state']}|{row.get('zip','')}".strip().lower()
    if key in cache:
        c = cache[key]
        return c["lat"], c["lon"], c["precision"], c["note"]

    lat = lon = None
    precision = note = ""
    z = (row.get("zip") or "").strip()[:5]
    if re.fullmatch(r"\d{5}", z):
        try:
            import zipcodes
            m = zipcodes.matching(z)
            if m:
                lat, lon = float(m[0]["lat"]), float(m[0]["long"])
                precision = "zip_centroid"
                note = f"ZIP {z} centroid ({m[0]['city']}, {m[0]['state']})"
        except Exception as e:  # pragma: no cover
            note = f"zip lookup failed: {e}"
    if lat is None:
        try:
            import geonamescache
            gc = geonamescache.GeonamesCache()
            city = row["city"].strip().lower()
            st = row["state"].strip().upper()
            cands = [c for c in gc.get_cities().values()
                     if c["countrycode"] == "US" and c["admin1code"] == st
                     and (c["name"].lower() == city or city in [a.lower() for a in c.get("alternatenames", [])])]
            if cands:
                c = max(cands, key=lambda c: c["population"])
                lat, lon = c["latitude"], c["longitude"]
                precision = "city_centroid"
                note = f"city centroid ({c['name']}, {st}; GeoNames {c['geonameid']})"
        except Exception as e:  # pragma: no cover
            note = f"city lookup failed: {e}"
    if lat is None:
        precision = "none"
        note = "could not geocode offline"
    cache[key] = {"lat": lat, "lon": lon, "precision": precision, "note": note}
    return lat, lon, precision, note


# ----------------------------------------------------------------- main
def main():
    subs = []
    with open(os.path.join(DATA, "hifld_substations.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            try:
                lat, lon = float(r["lat"]), float(r["lon"])
            except ValueError:
                continue
            kv = to_int(r["max_kv"])
            if kv is not None and kv < 0:
                kv = None
            r["_lat"], r["_lon"], r["_kv"] = lat, lon, kv
            subs.append(r)
    # coarse spatial grid (0.1 deg ≈ 11 km) for nearest-neighbour search
    grid = defaultdict(list)
    for s in subs:
        grid[(int(s["_lat"] * 10), int(s["_lon"] * 10))].append(s)

    retail = {}
    rp = os.path.join(DATA, "retail_utilities.json")
    if os.path.exists(rp):
        retail = json.load(open(rp))

    known = {}
    kp = os.path.join(DATA, "known_dedicated_subs.csv")
    if os.path.exists(kp):
        with open(kp, newline="") as fh:
            for r in csv.DictReader(fh):
                known[(r["city"].strip().lower(), r["state"].strip().upper())] = r

    cache_path = os.path.join(DATA, "dc_geocoded.json")
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}

    rows = []
    with open(os.path.join(DATA, "dc_roster.csv"), newline="") as fh:
        for dc in csv.DictReader(fh):
            lat, lon, prec, gnote = geocode(dc, cache)
            notes = [f"roster source: {dc['source_url']}"]
            if dc.get("notes"):
                notes.append(dc["notes"])
            notes.append(f"geocode: {gnote}")
            within08, within3 = [], []
            nearest = None
            if lat is not None:
                gi, gj = int(lat * 10), int(lon * 10)
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        for s in grid.get((gi + di, gj + dj), []):
                            d = haversine_km(lat, lon, s["_lat"], s["_lon"])
                            if d <= 3.0:
                                within3.append((d, s))
                                if d <= 0.8:
                                    within08.append((d, s))
                within3.sort(key=lambda t: t[0])
                if within3:
                    nearest = within3[0]
            open_year = to_int(dc.get("open_year"))
            new_build_bonus = 1 if (open_year and open_year >= 2022) else 0

            k = known.get((dc["city"].strip().lower(), dc["state"].strip().upper()))
            if nearest:
                d, s = nearest
                sub_name = s["name"] if (s["name"] and not s["name"].upper().startswith("UNKNOWN")) else f"(unnamed in HIFLD, id {s['hifld_id']})"
                sub_kv = s["_kv"]
                owner = "; ".join(retail.get(i, f"retail-territory id {i}") for i in s["retail_ids"].strip("|").split("|") if i) or "NOT IN HIFLD"
                sub_dist = round(d, 2)
                on_parcel = "TRUE" if (d < 0.4 and prec == "address") else ("UNVERIFIED" if d < 0.4 else "FALSE")
                score = voltage_weight(sub_kv) * proximity_weight(d) + new_build_bonus
                notes.append(f"HIFLD id {s['hifld_id']} ({s['type']}, {s['status']}); {len(within08)} sub(s) within 0.8 km, {len(within3)} within 3 km")
                if sub_kv is None:
                    notes.append("HIFLD max voltage not available for nearest sub (voltage weight 0)")
                sub_source = "HIFLD"
            else:
                sub_name, sub_kv, owner, sub_dist, on_parcel = "NONE", None, "NONE", None, "FALSE"
                score = 0 + new_build_bonus
                notes.append("no HIFLD substation within 3 km of geocoded point")
                sub_source = "HIFLD"
            if k:
                # press-confirmed dedicated substation that post-dates HIFLD vintage
                kkv = to_int(k["max_kv"])
                kd = float(k["distance_km"])
                kscore = voltage_weight(kkv) * proximity_weight(kd) + new_build_bonus
                if kscore >= score:
                    sub_name, sub_kv, owner, sub_dist = k["sub_name"], kkv, k["owner"], kd
                    on_parcel = "TRUE" if kd < 0.4 else "FALSE"
                    score = kscore
                    sub_source = "press/utility release"
                    notes.insert(1, f"DEDICATED SUBSTATION (not in HIFLD vintage): {k['evidence']} source: {k['source_url']}")
            rows.append({
                "dc_name": dc["dc_name"], "address": dc.get("address", ""), "city": dc["city"], "state": dc["state"],
                "type": dc["type"], "sqft": dc.get("sqft", ""), "open_year": dc.get("open_year", ""),
                "lat": "" if lat is None else round(lat, 5), "lon": "" if lon is None else round(lon, 5),
                "geocode_precision": prec,
                "nearest_sub_name": sub_name, "sub_distance_km": "" if sub_dist is None else sub_dist,
                "sub_max_kv": "" if sub_kv is None else sub_kv, "sub_owner": owner, "sub_source": sub_source,
                "on_parcel_likely": on_parcel, "score": score, "notes": " | ".join(notes),
            })
    json.dump(cache, open(cache_path, "w"), indent=1)

    rows.sort(key=lambda r: (-r["score"], r["sub_distance_km"] if r["sub_distance_km"] != "" else 99, r["state"], r["city"]))
    os.makedirs(OUT, exist_ok=True)
    cols = ["dc_name", "address", "city", "state", "type", "sqft", "open_year", "lat", "lon", "geocode_precision",
            "nearest_sub_name", "sub_distance_km", "sub_max_kv", "sub_owner", "sub_source", "on_parcel_likely", "score", "notes"]
    with open(os.path.join(OUT, "walmart-dc-substations.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    json.dump(rows, open(os.path.join(OUT, "ranked_rows.json"), "w"), indent=1)
    print(f"{len(rows)} DCs ranked; {sum(1 for r in rows if r['nearest_sub_name']!='NONE')} with a sub within 3 km")
    write_markdown(rows)
    return rows


def write_markdown(rows):
    top = rows[:25]
    L = []
    L.append("# Walmart US distribution centers ranked by likely substation capacity (10–20 MW Megapod screen)\n")
    L.append("Generated by `scripts/build_ranking.py` from `data/dc_roster.csv` (search-cited roster), the HIFLD Electric "
             "Substations layer (public-domain DHS/ORNL vintage mirrored on GitHub; taps, risers and dead-ends removed), "
             "the HIFLD retail service-territory layer (utility names), and `data/known_dedicated_subs.csv` "
             "(press-confirmed dedicated substations newer than the HIFLD vintage).\n")
    L.append("**Score** = voltage weight (345 kV+ = 5, 230 = 4, 115/138/161 = 3, 69 = 2, <69 = 1) × proximity weight "
             "(<0.4 km = 3, <0.8 km = 2, <3 km = 1) + 1 if open year ≥ 2022. `NONE` means no HIFLD substation within 3 km.\n")
    L.append("**Read the geocode precision column before trusting any distance.** The environment could not reach Nominatim "
             "or the Census geocoder, so every DC is placed at its ZIP-code centroid (or city centroid when no ZIP was found). "
             "That is typically 1–5 km from the actual parcel, so distances are a neighbourhood screen, not a parcel "
             "measurement, and `on_parcel_likely` is only TRUE where a cited utility release confirms a dedicated substation.\n")
    n_sub = sum(1 for r in rows if r["nearest_sub_name"] != "NONE")
    L.append(f"Roster size: {len(rows)} facilities. {n_sub} have a HIFLD substation within 3 km of the geocoded point.\n")
    L.append("## Top 25 by score\n")
    L.append("| # | DC | City, ST | Type | Sq ft | Open | Nearest substation | km | Max kV | Serving utility (HIFLD retail territory) | On parcel | Score |")
    L.append("|--:|----|----------|------|------:|-----:|--------------------|---:|------:|------------------------------------------|-----------|------:|")
    for i, r in enumerate(top, 1):
        L.append(f"| {i} | {r['dc_name']} | {r['city']}, {r['state']} | {r['type']} | {r['sqft'] or ''} | {r['open_year'] or ''} | "
                 f"{r['nearest_sub_name']} | {r['sub_distance_km']} | {r['sub_max_kv']} | {r['sub_owner']} | {r['on_parcel_likely']} | {r['score']} |")
    L.append("")
    L.append("## What HIFLD can't tell us\n")
    L.append("- **Spare capacity.** HIFLD records location and voltage class only. It has no transformer MVA ratings, no "
             "loading, and no hosting-capacity figure. A 138 kV substation can be fully subscribed; a 69 kV one can have "
             "20 MVA to spare. Only the utility's interconnection or load study answers this.")
    L.append("- **Customer-owned vs utility-owned.** The HIFLD substations layer has no owner field. The `sub_owner` column "
             "is the retail service territory the substation sits in, i.e. the utility (or utilities) that would serve a new "
             "load there, not necessarily the owner of the substation. Some substations near DCs are customer-owned "
             "(industrial park, rail, or the DC itself), which changes who you negotiate with and whether the capacity is "
             "contractually committed.")
    L.append("- **Feeder and transformer loading.** Whether the distribution feeders from that substation to the DC parcel "
             "are loaded at 40% or 95% is invisible here, as is whether the DC takes service at distribution or "
             "transmission voltage.")
    L.append("- **Vintage.** The public HIFLD layer stopped updating around 2022 and the open portal closed in 2025. New "
             "substations built for 2023+ DCs (Belvidere IL, Lancaster TX, Wellford SC, Stockton CA, Pilesgrove NJ, "
             "Carnesville GA) are not in it; only Belvidere has a cited utility release, so the others may be under-ranked.")
    L.append("- **Geocode precision.** See above. A DC that geocodes to a ZIP centroid 3 km from its parcel can show NONE "
             "while a substation sits across the road from the actual site, and vice versa.")
    L.append("- **Walmart's own on-site electrical.** Many large DCs have a customer-owned step-down yard or a utility "
             "'dedicated' sub inside the fence that HIFLD names generically (UNKNOWN*) or omits (<69 kV).")
    L.append("")
    L.append("## Questions to ask Walmart facilities / energy procurement for each top site\n")
    L.append("Generic to every site:\n")
    L.append("1. What is the service voltage and contracted demand (kW) at this DC today, and who is the serving utility and rate schedule?")
    L.append("2. Is the substation feeding the DC utility-owned or Walmart-owned? If Walmart-owned, what is the transformer nameplate (MVA) and the current peak load?")
    L.append("3. Has the utility stated available capacity at the serving substation or feeder (MW) for additional load, and is there a pending interconnection or load-addition study?")
    L.append("4. How much developable land is inside the fence or on the adjoining parcel (acres), and is any of it already reserved for solar, EV charging, or expansion?")
    L.append("5. Does the DC's existing onsite generation (solar, battery, backup gensets) or Walmart's PPA portfolio constrain adding a 10–20 MW behind-the-meter or co-located load?")
    L.append("6. Who at Walmart Realty / Energy signs on a ground lease or easement for a co-located battery + compute installation, and what is the approval path?\n")
    L.append("Site-specific:\n")
    for i, r in enumerate(top, 1):
        q = []
        if r["sub_source"] == "press/utility release":
            q.append(f"Confirm the dedicated {r['sub_max_kv']} kV substation's transformer rating and how much of its capacity is contractually reserved for the DC versus available for a co-located 10–20 MW load.")
        elif r["nearest_sub_name"] == "NONE":
            q.append("No HIFLD substation within 3 km of the geocoded point: confirm the actual serving substation, its voltage, and the distance of its feeder run to the parcel.")
        else:
            q.append(f"Is '{r['nearest_sub_name']}' ({r['sub_max_kv']} kV, ~{r['sub_distance_km']} km from the geocoded point) the substation that actually serves this DC, and is it on or adjoining the parcel?")
        if r["sub_owner"] not in ("NONE", "NOT IN HIFLD") and ";" in r["sub_owner"]:
            q.append(f"Multiple retail territories overlap here ({r['sub_owner']}): which utility holds the DC account?")
        if r["open_year"] and str(r["open_year"]).isdigit() and int(r["open_year"]) >= 2022:
            q.append("As a 2022+ build, was a dedicated substation or transmission-level tap built for this site, and what is its nameplate MVA?")
        L.append(f"**{i}. {r['dc_name']} — {r['city']}, {r['state']}**")
        for x in q:
            L.append(f"- {x}")
        L.append("")
    with open(os.path.join(OUT, "walmart-dc-substations.md"), "w") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
