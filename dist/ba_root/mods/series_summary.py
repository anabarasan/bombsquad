"""
series_summary module for BombSquad version 1.6.5
Provides functionality for storing match results at the end of a series
"""

from datetime import datetime
import os

import ba
from ba._gameresults import GameResults

import mysettings

SUMMARY_HTML = """<!doctype html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Vaaichol Veerargal</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3"
      crossorigin="anonymous"
    />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.0/font/bootstrap-icons.css"
    />
    <script
      src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
      integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"
      crossorigin="anonymous"
    ></script>
  </head>
  <body class="container">
    <h1 style="text-align: center">
      &#x0BB5;&#x0BBE;&#x0BAF;&#x0BCD;&#x0B9A;&#x0BCD;&#x0B9A;&#x0BCA;&#x0BB2;&#x0BCD;
      &#x0BB5;&#x0BC0;&#x0BB0;&#X0BB0;&#X0BCD;&#x0B95;&#x0BB3;&#X0BCD;
    </h1>
    <h2 style="text-align:center">series at <<<series_time_stamp>>></h2>
    <h3 style="text-align:center">won by <<<team_name>>></h3>
    <br/><br/>
    <<<details>>>
  </body>
</html>
"""


class SeriesSummary:
    match_results = []

    @classmethod
    def append(cls, results: GameResults, stats: ba.Stats) -> None:
        data = {}
        player_scores = {}
        for player in stats.get_records().values():
            player_scores[player.getname(True)] = player.accumscore

        winning_team = results.winning_sessionteam
        data["winner"] = winning_team.name.evaluate() if winning_team else "no winner"
        data["teams"] = []

        for team in results.sessionteams:
            players = []
            for player in team.players:
                name = player.getname(True)
                players.append((name, player_scores.get(name, "-")))

            data["teams"].append(
                {
                    "name": team.name.evaluate(),
                    "score": results.get_sessionteam_score(team),
                    # score_str = results.get_sessionteam_score_str(team).evaluate(),
                    "players": players,
                }
            )
        cls.match_results.append(data)

    @classmethod
    def save_summary(cls):
        now = datetime.strftime(datetime.now(), "%Y%m%d%H%m%S%f")
        filename = os.path.join(mysettings.series_dir, f"{now}.html")

        html = ""
        for idx, match_result in enumerate(cls.match_results):
            winner = match_result["winner"]
            html += """<div class="row">"""
            html += f"""<div class="row"><h3>Match {idx +1}</h3></div>"""
            html += f"""<div class="row"><h3>Won by {winner}</h3></div>"""
            html += """<div class="row">"""
            for team in match_result["teams"]:
                html += """<div class="col">"""
                html += """<div class="row">"""
                html += f"""{team["name"]} ({team["score"]})"""
                html += """</div>"""
                for player, player_score in team["players"]:
                    html += """<div class="row">"""
                    html += f"""{player} ({player_score})"""
                    html += """</div>"""
                html += """</div>"""
            html += """</div>"""
            html += "</div>"
            html += "<br/><br/><br/>"
        html = (
            SUMMARY_HTML.replace("<<<details>>>", html)
            .replace("<<<series_time_stamp>>>", now)
            .replace("<<<team_name>>>", "")
        )

        with open(filename, "w") as f:
            f.write(html)
        print(f"saved summary to {filename}")
