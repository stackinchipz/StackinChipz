# Walmart DC substation screen (Megapod siting)

Ranks Walmart US distribution centers by the likelihood of usable substation
capacity near the site for a 10–20 MW Megapod (battery + compute) deployment.

```
data/dc_roster.csv            DC roster, one row per facility, every row cites its source URL
data/hifld_substations.csv    HIFLD Electric Substations (56,039 substations; taps/risers/dead-ends removed)
data/retail_utilities.json    HIFLD retail service-territory id -> utility name (2,930 utilities)
data/known_dedicated_subs.csv press-confirmed dedicated substations newer than the HIFLD vintage
data/dc_geocoded.json         offline geocode cache (ZIP / city centroids)
scripts/build_ranking.py      distance search, scoring, CSV + Markdown output
out/walmart-dc-substations.csv
out/walmart-dc-substations.md
```

Rebuild: `python3 -I scripts/build_ranking.py`

## Sources and provenance

- **HIFLD substations**: the DHS/ORNL public-domain layer. The HIFLD Open portal
  closed in 2025 and this session's network policy blocks ArcGIS, so the layer was
  taken from two public GitHub mirrors:
  `Colin-Hanley1/DSCapstoneVisualization` (`hifld_substations.geojson`, 77,945
  records with NAME / TYPE / STATUS / MAX_VOLT / CITY / COUNTY) and
  `BenHutchinsWPP/TransmissionMap` (`data-static` branch, adds retail-territory
  ids per substation and the `retail_territories.pmtiles` layer used for utility
  names). HIFLD's substation layer has no owner field; `sub_owner` in the output
  is the retail service territory the substation sits in.
- **DC roster**: mwpvl.com and spscommerce.com were unreachable under the
  session's network policy, so the roster was assembled from web-search results
  (SupplyPike, Logimatcher/Ankpost master lists, link-trans, Warehouse Ninja,
  AMZ Prep, trade press and Walmart newsroom coverage). Each row's `source_url`
  is the page the search result quoted. Square footage and open year are blank
  where no source stated them.
- **Geocoding**: Nominatim and the Census geocoder were unreachable, so DCs are
  geocoded offline to ZIP centroids (`zipcodes` package) or city centroids
  (`geonamescache`). `geocode_precision` is recorded on every output row.

## Known limits

See the "What HIFLD can't tell us" section of `out/walmart-dc-substations.md`.
The biggest one: centroid geocoding means `sub_distance_km` is a neighbourhood
screen, and `on_parcel_likely` is only TRUE where a cited utility release
confirms a dedicated substation (Belvidere, IL).

## Run of 2026-10-27

| Item | Count |
|------|------:|
| Facilities in roster | 163 |
| Rows with a HIFLD substation within 3 km of the geocoded point | 143 |
| Rows with square footage / open year from a cited source | 83 / 60 |
| Rows geocoded (ZIP centroid / city centroid / none) | 92 / 70 / 1 |

Belvidere, IL ranks first (score 10) on the cited ComEd 138 kV dedicated
substation. Everything else scores on the strongest HIFLD substation within
3 km of its centroid, so the rest of the table is a grid-strength screen, not
a parcel-level finding.

Follow-ups that would sharpen this materially:

1. Allow `nominatim.openstreetmap.org` or `geocoding.geo.census.gov` in the
   environment's network settings and rerun: rows with street addresses get
   address-level coordinates and the full <0.4 / <0.8 km tiers switch on.
2. Allow `www.mwpvl.com` and `www.spscommerce.com` to replace the search-derived
   roster with the full tables (square footage and open years are the gap).
3. Utility releases for the other 2022+ builds were checked on 2026-10-27
   (`data/newbuild_power_checks.csv`): none of Lancaster TX, Wellford SC,
   Stockton CA, Pilesgrove NJ, Carnesville GA, Greencastle PA or McCordsville IN
   surfaced a substation release, so Belvidere IL remains the only row with a
   press-confirmed dedicated substation. Utility interconnection filings or
   local permit records would be the next place to look.

Second-pass gap fill (2026-10-27, three agents, 94 searches): square footage
rose from 60 to 83 rows and open year from 48 to 60; Irvington AL import DC,
Shepherdsville KY FC and a low-confidence Opelika AL row were added. Several
fills are flagged in `notes` as planned sizes, prior-tenant building sizes or
single weak sources; read the note before quoting a number.
