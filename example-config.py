# Most of this can be re-used, but stuff like the link to Dom's spreadsheet
# needs to be provided. Save this as config.py in the directory.

AAG_SHEET_ID = "1gtUEwyFjahDSWyHn3VdxAOXMrsbY5wg42Q6d_2SSk1s"
AAG_GID = "0"
AAG_HEADER_ROW = 4
AAG_TRANSLATIONS = {"": "Name", "Proj Pos": "Pos"}

D2Z_SHEET_ID = "1gejB9XqTto3iBoXtYBurS1tD0lJQ5VtcrnNyZKuYxO0"
D2Z_SKATER_GID = "1047483062"
D2Z_GOALIE_GID = "1325856504"
D2Z_HEADER_ROW = 0
D2Z_TRANSLATIONS = {
    "Goals": "G",
    "Assists": "A",
    "PP Points": "PPP",
    "Hits": "HIT",
    "Player": "Name",
    "player": "Name",
    "team": "Team",
}

CBS_TRANSLATIONS = {"PPG": "PPP", "SHG": "SHP"}

DOM_URL = "" # Need to add
DOM_TRANSLATIONS = {"NAME": "Name", "POS": "Pos", "Player": "Name"}

ESPN_SEASON = 2023
ESPN_TRANSLATIONS = {
    "0": "GP",
    "1": "W",
    "2": "L",
    "4": "GA",
    "6": "SV",
    "7": "SO",
    "30": "GP",
    "13": "G",
    "14": "A",
    "29": "SOG",
    "31": "HIT",
    "32": "BLK",
    "38": "PPP",
}
ESPN_POSITIONS = {
    1: "C",
    2: "LW",
    3: "RW",
    4: "D",
    5: "G",
}
ESPN_TEAMS = {
    1: "BOS",
    2: "BUF",
    3: "CGY",
    4: "CHI",
    5: "DET",
    6: "EDM",
    7: "CAR",
    8: "LA",
    9: "DAL",
    10: "MON",
    11: "NJ",
    12: "NYI",
    13: "NYR",
    14: "OTT",
    15: "PHI",
    16: "PIT",
    17: "COL",
    18: "SJ",
    19: "STL",
    20: "TB",
    21: "TOR",
    22: "VAN",
    23: "WAS",
    24: "ARI",
    25: "ANH",
    26: "FLA",
    27: "NSH",
    28: "WPG",
    29: "CLS",
    30: "MIN",
    37: "VGK",
    124292: "SEA",
}

LAIDLAW_URL = "https://download2287.mediafire.com/hn54uvz6gteg/bbb90i1t5sawnxc/2022-23+Steve+Laidlaw+Fantasy+Hockey+Rankings.xlsx"
LAIDLAW_TRANSLATIONS = {
    None: 'Name',
    'Alexander Ovechkin': 'Alex Ovechkin',
    'JT Miller': 'J.T. Miller',
    'Mitch Marner': 'Mitchell Marner',
    'TJ Oshie': 'T.J. Oshie',
    'JG Pageau': 'Jean-Gabriel Pageau',
    'Maxime Comtois': 'Max Comtois',
    'Sam Girard': 'Samuel Girard',
    'JT Compher': 'J.T. Compher',
    'Alex Martinez': 'Alec Martinez',
    'Oskar Lindlom': 'Oskar Lindblom'
}

NUMBERFIRE_URL = "https://www.numberfire.com/nhl/fantasy/yearly-projections"
NUMBERFIRE_TRANSLATIONS = {'S': 'SOG'}

YAHOO_TRANSLATIONS = {"GP*": "GP"}

SCOTT_CULLEN_SHEET_ID = "14S0RP2Vvn-uY8zp6-YBKI7EKs-dFY_pS4q7TU8WEw_s"
SCOTT_CULLEN_GID = "1851906377"
SCOTT_CULLEN_HEADER_ROW = 0
SCOTT_CULLEN_TRANSLATIONS = {
    "Player": "Name",
    "POS": "Pos"
}