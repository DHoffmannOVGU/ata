# Define data types and properties
deckung_properties = {
    'Kunde': str,
    'Benennung': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Gewicht': float,
    'Material Kosten': float,
    'Brennen': float,
    'Schlossern': float,
    'Schweißen': float,
    'sonstiges (Eur/hour)': float,
    'sonstiges (hour)': float,
    'Prüfen , Doku': float,
    'Strahlen / Streichen': float,
    'techn. Bearb.': float,
    'mech. Vorbearb.': float,
    'mech. Bearbeitung': float,
    'Zwischentransporte': float,
    'transporte': float,
    'Erlös': float,
    'DB': float,
    'Deckungsbeitrag': float,
}

vk_st0_data = {
    # "Kunde": "",
    # "Gegenstand": "",
    # "Zeichnungs- Nr.": "",
    # "Ausführen Nr.": "",
    "Fertigung Gesamt": 0,
    "bis 90mm Einsatz": 0,
    "bis 90mm Fertig": 0,
    "bis 90mm Preis": 0,
    "ab 100mm Einsatz": 0,
    "ab 100mm Fertig": 0,
    "ab 100mm Preis": 0,
    "Profile Einsatz": 0,
    "Profile fertig": 0,
    "Profile Preis": 0
}

vk0_data = {
    "Brennen": 0,
    "Richten": 0,
    "Heften_Zussamenb_Verputzen": 0,
    "Anzeichnen": 0,
    "Schweißen": 0
}

customers = [
    "Siemens Duisburg",
    "Siemens Berlin",
    "Siemens Erlangen",
    "Siemens Nürnberg",
    "Siemens München",
    "Siemens Karlsruhe",
    "OVGU Magdeburg",
]



units = {
    'Gewicht': 'kg',
    'Material Kosten': '€',
    'Brennen': 'min',
    'Schlossern': 'min',
    'Schweißen': 'min',
    'sonstiges (Eur/hour)': '€/min',
    'sonstiges (hour)': 'min',
    'Prüfen , Doku': '€',
    'Strahlen / Streichen': '€',
    'techn. Bearb.': '€',
    'mech. Vorbearb.': '€',
    'mech. Bearbeitung': '€',
    'Zwischentransporte': '€',
    'transporte': '€',
    'Erlös': '€',
    'DB': '%',
    'Deckungsbeitrag': '€',
    'Richten': 'min',
    'Heften_Zussamenb_Verputzen': 'min',
    'Anzeichnen': 'min',
}