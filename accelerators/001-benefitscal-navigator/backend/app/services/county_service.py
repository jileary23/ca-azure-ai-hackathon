"""CA county welfare office lookup service."""

from app.models.schemas import CountyOffice

COUNTY_OFFICES_DB: list[dict] = [
    {
        "name": "Los Angeles County DPSS",
        "county": "Los Angeles",
        "address": "12860 Crossroads Pkwy S, City of Industry, CA 91746",
        "phone": "(866) 613-3777",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        "languages_served": ["en", "es", "zh", "vi", "ko", "hy", "tl"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief", "CAPI"],
    },
    {
        "name": "San Francisco HSA",
        "county": "San Francisco",
        "address": "1235 Mission St, San Francisco, CA 94103",
        "phone": "(415) 557-5000",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        "languages_served": ["en", "es", "zh", "tl", "vi"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief"],
    },
    {
        "name": "Sacramento County DHA",
        "county": "Sacramento",
        "address": "2700 Fulton Ave, Sacramento, CA 95821",
        "phone": "(916) 874-3100",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        "languages_served": ["en", "es", "zh", "vi", "fa"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief", "CAPI"],
    },
    {
        "name": "San Diego County HHSA",
        "county": "San Diego",
        "address": "1255 Imperial Ave, Suite 100, San Diego, CA 92101",
        "phone": "(866) 262-9881",
        "hours": "Mon-Fri 7:30 AM - 5:00 PM",
        "languages_served": ["en", "es", "tl", "vi", "ar"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief"],
    },
    {
        "name": "Fresno County DSS",
        "county": "Fresno",
        "address": "2135 Fresno St, Suite 301, Fresno, CA 93721",
        "phone": "(559) 600-1176",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        "languages_served": ["en", "es"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief"],
    },
    {
        "name": "Alameda County SSA",
        "county": "Alameda",
        "address": "2000 San Pablo Ave, Oakland, CA 94612",
        "phone": "(510) 263-2420",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        "languages_served": ["en", "es", "zh", "vi", "tl"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief"],
    },
    {
        "name": "Riverside County DPSS",
        "county": "Riverside",
        "address": "4060 County Circle Dr, Riverside, CA 92503",
        "phone": "(877) 410-8827",
        "hours": "Mon-Fri 8:00 AM - 5:00 PM",
        "languages_served": ["en", "es"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief"],
    },
    {
        "name": "Orange County SSA",
        "county": "Orange",
        "address": "1928 S Grand Ave, Santa Ana, CA 92705",
        "phone": "(800) 281-9799",
        "hours": "Mon-Fri 7:30 AM - 5:00 PM",
        "languages_served": ["en", "es", "vi", "ko", "zh"],
        "services": ["CalFresh", "CalWORKs", "Medi-Cal", "General Relief", "CAPI"],
    },
]

ALL_CA_COUNTIES: list[str] = [
    "Alameda", "Alpine", "Amador", "Butte", "Calaveras", "Colusa",
    "Contra Costa", "Del Norte", "El Dorado", "Fresno", "Glenn",
    "Humboldt", "Imperial", "Inyo", "Kern", "Kings", "Lake", "Lassen",
    "Los Angeles", "Madera", "Marin", "Mariposa", "Mendocino", "Merced",
    "Modoc", "Mono", "Monterey", "Napa", "Nevada", "Orange", "Placer",
    "Plumas", "Riverside", "Sacramento", "San Benito", "San Bernardino",
    "San Diego", "San Francisco", "San Joaquin", "San Luis Obispo",
    "San Mateo", "Santa Barbara", "Santa Clara", "Santa Cruz", "Shasta",
    "Sierra", "Siskiyou", "Solano", "Sonoma", "Stanislaus", "Sutter",
    "Tehama", "Trinity", "Tulare", "Tuolumne", "Ventura", "Yolo", "Yuba",
]


def get_offices(county: str | None = None) -> list[CountyOffice]:
    """Return offices optionally filtered by county name (case-insensitive)."""
    if county is None:
        return [CountyOffice(**o) for o in COUNTY_OFFICES_DB]
    normalized = county.strip().title()
    return [
        CountyOffice(**o)
        for o in COUNTY_OFFICES_DB
        if o["county"].lower() == normalized.lower()
    ]


def get_all_counties() -> list[str]:
    """Return all 58 CA county names."""
    return ALL_CA_COUNTIES
