import re


class Skater:
    def __init__(self, headers, data, translations, provider, extra={}, fix_rate_stats=False):
        data = build_data(headers, data, extra, translations)

        self.provider = provider
        self.name = data.get("Name")
        self.team = normalize_team(data.get("Team"))
        self.position = re.sub(r"\d+", "", data.get("Pos")) if data.get("Pos") else None

        self.gp = as_float(data.get("GP"))
        self.g = normalize(data, "G", fix_rate_stats)
        self.a = normalize(data, "A", fix_rate_stats)
        self.ppp = normalize(data, "PPP", fix_rate_stats)
        self.shp = normalize(data, "SHP", fix_rate_stats)
        self.sog = normalize(data, "SOG", fix_rate_stats)
        self.hit = normalize(data, "HIT", fix_rate_stats)
        self.blk = normalize(data, "BLK", fix_rate_stats)

    def __repr__(self):
        return str(self.__dict__)

    def insert(self, cursor, player_id):
        cursor.execute("""
        INSERT INTO skater_projections (player_id, provider, gp, g, a, ppp, sog, hit, blk)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (player_id, self.provider, self.gp, self.g, self.a, self.ppp, self.sog, self.hit, self.blk))

class Goalie:
    def __init__(self, headers, data, translations, provider, extra={}, fix_rate_stats=False):
        data = build_data(headers, data, extra, translations)

        self.provider = provider
        self.name = data.get("Name")
        self.team = normalize_team(data.get("Team"))
        self.position = "G"

        self.gp = as_float(data.get("GP"))
        self.w = normalize(data, "W", fix_rate_stats)
        self.l = normalize(data, "L", fix_rate_stats)
        self.ga = normalize(data, "GA", fix_rate_stats)
        self.sv = normalize(data, "SV", fix_rate_stats)
        self.so = normalize(data, "SO", fix_rate_stats)

    def __repr__(self):
        return str(self.__dict__)

    def insert(self, cursor, player_id):
        cursor.execute("""
        INSERT INTO goalie_projections (player_id, provider, gp, w, l, ga, sv, so)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (player_id, self.provider, self.gp, self.w, self.l, self.ga, self.sv, self.so))


def build_data(headers, data, extra, translations):
    headers = [normalize_headers(h, translations) for h in headers]
    return safe_zip(headers, data) | extra


def normalize_headers(header, translations):
    translated = translations.get(header)
    return header if translated is None else translated


def safe_zip(headers, data):
    result = {}
    for (header, input) in zip(headers, data):
        if header not in result or result[header] is None:
            result[header] = input

    return result


def as_float(value):
    if value in [None, ""]:
        return None
    elif type(value) != str:
        return value
    else:
        try:
            return float(value.replace("%", ""))
        except ValueError:
            return None

def normalize(data, key, fix_rate_stats):
    stat = as_float(data.get(key))

    if fix_rate_stats:
        gp = as_float(data.get("GP"))
        gp = 82 if gp is None else gp
        return multiply(gp, stat)
    else:
        return stat


def multiply(value1, value2):
    if value1 is None or value2 is None:
        return None
    return value1 * value2


TEAMS = {
    "ANA": "ANH",
    "CLB": "CLS",
    "CBJ": "CLS",
    "FA": "FLA",
    "LAK": "LA",
    "L.A": "LA",
    "LV": "VGK",
    "MTL": "MON",
    "NJD": "NJ",
    "SJS": "SJ",
    "TBL": "TB",
    "WSH": "WAS",

}
def normalize_team(team):
    if not team:
        return team

    normalized = team.replace('?', '')

    if normalized in TEAMS:
        return TEAMS.get(normalized)
    else:
        return normalized