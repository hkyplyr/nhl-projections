from math import ceil
from config import *
import difflib
from player import Goalie, Skater
from fetcher import CbsParser, DomSheet, EspnApi, GoogleSheet, LaidlawSheet, NumberfireParser, YahooParser
from yfantasy_api.api import YahooFantasyApi
import psycopg2

apples_and_gino_skaters = GoogleSheet(
    AAG_SHEET_ID, AAG_GID, AAG_HEADER_ROW, Skater, AAG_TRANSLATIONS, "ApplesAndGinos"
)

datsyuk_to_zetterberg_skaters = GoogleSheet(
    D2Z_SHEET_ID, D2Z_SKATER_GID, D2Z_HEADER_ROW, Skater, D2Z_TRANSLATIONS, "Datsyuk2Zetterberg"
)

datsyuk_to_zetterberg_goalies = GoogleSheet(
    D2Z_SHEET_ID, D2Z_GOALIE_GID, D2Z_HEADER_ROW, Goalie, D2Z_TRANSLATIONS, "Datsyuk2Zetterberg"
)

cbs_players = CbsParser(CBS_TRANSLATIONS)

espn_players = EspnApi(ESPN_SEASON, ESPN_TRANSLATIONS, ESPN_POSITIONS, ESPN_TEAMS)

dom_players = DomSheet(DOM_URL, DOM_TRANSLATIONS)

laidlaw_players = LaidlawSheet(LAIDLAW_URL, LAIDLAW_TRANSLATIONS)

numberfire_parser = NumberfireParser(NUMBERFIRE_URL, NUMBERFIRE_TRANSLATIONS)

scott_cullen = GoogleSheet(
    SCOTT_CULLEN_SHEET_ID, SCOTT_CULLEN_GID, SCOTT_CULLEN_HEADER_ROW, Skater, SCOTT_CULLEN_TRANSLATIONS, "ScottCullen"
)

yahoo_players = YahooParser(YAHOO_TRANSLATIONS)

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost dbname=projections user=postgres password=postgres port=5544")
    cursor = conn.cursor()
#
    #api = YahooFantasyApi(6738, 'nhl')
    #for i in range(100):
    #    players = api.league().players(start=i*25).draft_analysis().get().players
    #    for player in players:
    #        print(player.id, player.name, player.position, player.nfl_team, player.average_pick)
#
    #        if 'RW' in player.position:
    #            single_position = 'RW'
    #        elif 'LW' in player.position:
    #            single_position = 'LW'
    #        elif 'C' in player.position:
    #            single_position = 'C'
    #        elif 'D' in player.position:
    #            single_position = 'D'
    #        elif 'G' in player.position:
    #            single_position = 'G'
    #        else:
    #            single_position = player.position
    #            
    #        cursor.execute('INSERT INTO players (id, name, position, team, single_position) VALUES (%s, %s, %s, %s, %s)', \
    #                (player.id, player.name, player.position, player.nfl_team, single_position))
#
    #        if player.average_pick:
    #            r = ceil(player.average_pick / 12)
    #            p = player.average_pick - (12 * (ceil(player.average_pick / 12) - 1))
#
    #            cursor.execute('INSERT INTO adp (player_id, adp, round, pick) VALUES (%s, %s, %s, %s)', (player.id, player.average_pick, r, p))
#
    #conn.commit()
#
    #exit()



    players = [
        fetcher.get_projections()
        for fetcher in [
            apples_and_gino_skaters,
            datsyuk_to_zetterberg_skaters,
            datsyuk_to_zetterberg_goalies,
            cbs_players,
            espn_players,
            dom_players,
            scott_cullen
        ]
    ]

    players = [item for sublist in players for item in sublist]
    
    for player in players:
        cursor.execute("""
        SELECT id FROM players
        WHERE similarity(name, %s) > 0.8
        """, (player.name,))

        result = cursor.fetchall()

        if len(result) == 0:
            cursor.execute("""
            SELECT id FROM players
            WHERE team = %s
            AND similarity(name, %s) > 0.5
            """, (player.team, player.name))

            result = cursor.fetchall()

        if len(result) > 1:
            position = f'%{player.position}%'

            cursor.execute("""
            SELECT id FROM players
            WHERE team = %s
            AND position like %s
            AND similarity(name, %s) > 0.5
            """, (player.team, position, player.name))

            result = cursor.fetchall()
        
        if len(result) != 1:
            position = f'%{player.position}%'

            cursor.execute("""
            SELECT id FROM players
            WHERE position like %s
            AND similarity(name, %s) > 0.5
            """, (position, player.name))

            result = cursor.fetchall()

        if len(result) == 1:
            player.insert(cursor, result[0][0])
        else:
            print(player.name, player.team, player.provider)
    conn.commit()

    # results = {}
    # for player in players:
    #     if player.name not in results:
    #         results[player.name] = 1
    #     else:
    #         results[player.name] += 1
    # for (k, v) in sorted(results.items()):
    #     possibilities = results.keys() - [k]
    #     print(k, difflib.get_close_matches(k, possibilities, cutoff=0.8))
