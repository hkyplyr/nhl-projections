import csv
import json
import re
import requests
import tempfile

from bs4 import BeautifulSoup
from openpyxl import load_workbook
from player import Goalie, Skater


class Fetcher:
    pass


class GoogleSheet(Fetcher):
    def __init__(self, sheet_id, gid, header_row, type, translations, provider):
        self.sheet_id = sheet_id
        self.gid = gid
        self.header_row = header_row
        self.type = type
        self.translations = translations
        self.provider = provider

    def cast(self, headers, data):
        return self.type(headers, data, self.translations, self.provider)

    def get_projections(self):
        headers, data = self.__download()
        return [self.cast(headers, row) for row in data]

    def __download(self):
        url = f"https://docs.google.com/spreadsheet/ccc?key={self.sheet_id}&output=csv&gid={self.gid}"
        content = requests.get(url).content.decode("utf-8").split("\n")
        data = list(csv.reader(content))
        return data[self.header_row], data[self.header_row + 1 :]


class ExcelSheet(Fetcher):
    def __init__(self, url, translations):
        self.url = url
        self.translations = translations

    def download(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
            response = requests.get(self.url)
            f.write(response.content)
            return load_workbook(filename=f.name)

class LaidlawSheet(ExcelSheet):
    def get_projections(self): 
        book = self.download()["Total Skaters"]

        headers = [cell.value for cell in book[1]]
        return list(self.__get_projections(book, headers))

    def __get_projections(self, book, headers):
        for row in list(book.rows)[1:]:
            data = [cell.value for cell in row]

            if not data[0]:
                continue

            data[0] = self.__translate_name(data[0])

            yield Skater(headers, data, self.translations, "Laidlaw")

    def __translate_name(self, name):
        if name in self.translations:
            return self.translations.get(name)
        else:
            return name

class DomSheet(ExcelSheet):
    def get_projections(self):
        book = self.download()["Player Data"]

        headers = [cell.value for cell in book[2]]
        headers.append('Team')
        return list(self.__get_projections(book, headers))

    def __get_projections(self, book, headers):
        positions = self.__get_positions()
        for row in list(book.rows)[2:]:
            data = [cell.value for cell in row]

            if not data[0]:
                continue
            
            data.append(positions[data[0]])

            if data[1] == "G":
                yield Goalie(headers, data, self.translations, "Dom", fix_rate_stats=True)
            else:
                yield Skater(headers, data, self.translations, "Dom", fix_rate_stats=True)

    def __get_positions(self):
        positions = {}
        book = self.download()["ADP"]

        headers = [cell.value for cell in book[1]]
        for row in list(book.rows)[1:]:
            data = dict(zip(headers, [cell.value for cell in row]))
            positions[data['NAME']] = data['TEAM']

        return positions

class Website(Fetcher):
    def download(self, url):
        return BeautifulSoup(requests.get(url).text, "html.parser")


class YahooParser(Website):
    def __init__(self, translations):
        self.base_url = "https://hockey.fantasysports.yahoo.com/hockey/15141/players?status=ALL&pos={position}&cut_type=33&stat1=S_PSR&myteam=0&sort=OR&sdir=1&count={count}"
        self.translations = translations

    def get_projections(self):
        skaters = [self.__get_projections("P", page) for page in range(60)]

        goalies = [self.__get_projections("G", page) for page in range(60)]

        players = skaters + goalies

        return [item for sublist in players for item in sublist]

    def __get_projections(self, position, page):
        soup = self.download(self.base_url.format(position=position, count=page * 25))

        section = soup.find("section", {"id": "players-table-wrapper"})
        if not section:
            print(
                "Error.. retrying",
                self.base_url.format(position=position, count=page * 25),
            )
            self.__get_projections(position, page)
        table = section.find("table")

        headers = self.__extract_headers(table)
        return list(self.__extract_players(table, headers))

    def __extract_headers(self, table):
        return [cell.get_text() for cell in table.find_all("tr")[1].find_all("th")]

    def __extract_players(self, table, headers):
        for row in table.find_all("tr")[1:]:
            values = [cell.get_text() for cell in row.find_all("td")]

            if not values:
                continue

            name, team, position = self.__extract_name_team_position(values)
            if position == "G":
                player = Goalie(
                    headers,
                    values,
                    {"GP*": "GP"},
                    extra={"Name": name, "Team": team, "Pos": position},
                )
                print(player)
                yield player
            else:
                player = Skater(
                    headers,
                    values,
                    {"GP*": "GP"},
                    extra={"Name": name, "Team": team, "Pos": position},
                )
                print(player)
                yield player

    def __extract_name_team_position(self, player_info):
        raw_value = (
            player_info[1]
            .replace("\n", "")
            .replace("No new player Notes", "")
            .replace("New Player Note", "")
            .replace("Player Note", "")
            .replace(",", "/")
            .strip()
        )

        search = re.search("(^[A-Za-z-.' ]+) ([A-Za-z]{2,}) - ([A-Za-z\/]+)", raw_value)
        return search.group(1), search.group(2).upper(), search.group(3)

class NumberfireParser(Website):
    def __init__(self, url, translations):
        self.url = url
        self.translations = translations

    def get_projections(self):
        soup = self.download(self.url)
        table = soup.find_all("table")[0]

        player_info = {}
        for row in table.find_all("tr"):
            data_row_index = row.attrs.get("data-row-index")
            cell = row.find("td")

            if not cell:
                continue

            name = cell.find("span", {"class": "full"}).get_text()
            search = re.search("\(([A-Z]+), ([A-Z]+)\)", cell.get_text())
            position = search.group(1)
            team = search.group(2)

            player_info[data_row_index] = {"Name": name, "Pos": position, "Team": team}
            
        stat_table = soup.find_all("table")[1]
        for row in stat_table.find_all("tr"):
            data_row_index = row.attrs.get("data-row-index")

            cells = row.find_all("td")

            if not cells:
                continue
            
            player_name_stuff = player_info.get(data_row_index)
            data = {
                cell.attrs.get("class")[0].upper(): cell.get_text()
                for cell in cells
            }

            data['PPP'] = data['PPG'] + data['PPA']

            combined = player_name_stuff | data
            skater = Skater(combined.keys(), combined.values(), self.translations, "Numberfire")

            print(skater)

            

class CbsParser(Website):
    def __init__(self, translations):
        self.base_url = "https://www.cbssports.com/fantasy/hockey/stats/{position}/2022/season/projections/"
        self.translations = translations

    def get_projections(self):
        return (
            self.__get_projections("C")
            + self.__get_projections("W")
            + self.__get_projections("D")
            + self.__get_projections("G")
        )

    def __get_projections(self, position):
        soup = self.download(self.base_url.format(position=position))
        table = soup.find("table")

        headers = self.__extract_headers(table)
        return list(self.__extract_players(table, headers))

    def __extract_headers(self, table):
        return [
            self.__safe_extract_text(cell)
            for cell in table.find_all("tr")[0].find_all("th")
        ]
    
    def __safe_extract_text(self, cell):
        if cell.find("a"):
            return cell.find("a").get_text().upper()
        else:
            None

    def __extract_players(self, table, headers):
        for row in table.find_all("tr"):
            cells = [cell for cell in row.find_all("td")]

            if not cells:
                continue

            name, team, position = self.__extract_name_team_position(cells[0])
            extra_data = {"Name": name, "Team": team, "Pos": position}
            stats = [
                None if cell.get_text().strip() == "-" else cell.get_text().strip()
                for cell in cells
            ]

            if position == "G":
                yield Goalie(headers, stats, self.translations, "CBS", extra_data)
            else:
                yield Skater(headers, stats, self.translations, "CBS", extra_data)

    def __extract_name_team_position(self, name_cell):
        name_cell = name_cell.find("span", {"class": "CellPlayerName--long"})

        if not name_cell.find("a"):
            return None, None, None

        name = name_cell.find("a").get_text().strip()
        team = (
            name_cell.find("span", {"class": "CellPlayerName-team"}).get_text().strip()
        )
        position = (
            name_cell.find("span", {"class": "CellPlayerName-position"})
            .get_text()
            .strip()
        )

        return name, team, position


class EspnApi(Fetcher):
    def __init__(self, season, translations, positions, teams):
        self.season = season
        self.translations = translations
        self.teams = teams
        self.positions = positions

    def get_projections(self):
        players = self.__download()["players"]
        return list(self.__get_projections(players))

    def __get_projections(self, players):
        for p in players:
            player = p["player"]
            stats = [
                stats.get("stats", {})
                for stats in player.get("stats", {})
                if stats["id"] == "102023"
            ]

            if not stats or not stats[0]:
                continue

            player_name = player["fullName"]
            team = self.teams[player["proTeamId"]]
            position = self.positions[player["defaultPositionId"]]
            extra_data = {"Name": player_name, "Team": team, "Pos": position}

            if position == "G":
                yield Goalie(
                    stats[0].keys(), stats[0].values(), self.translations, "ESPN", extra_data
                )
            else:
                yield Skater(
                    stats[0].keys(), stats[0].values(), self.translations, "ESPN", extra_data
                )

    def __download(self):
        url = f"https://fantasy.espn.com/apis/v3/games/fhl/seasons/{self.season}/segments/0/leaguedefaults/1?view=kona_player_info"
        headers = {
            "players": {
                "filterStatsForExternalIds": {"value": [self.season]},
                "filterStatsForSourceIds": {"value": [1]},
                "sortDraftRanks": {
                    "sortPriority": 2,
                    "sortAsc": True,
                    "value": "STANDARD",
                },
            }
        }

        return requests.get(
            url, headers={"x-fantasy-filter": json.dumps(headers)}
        ).json()
