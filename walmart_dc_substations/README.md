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
