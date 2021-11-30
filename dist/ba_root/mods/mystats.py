damage_data = {}
# Don't touch the above line
"""
mystats module for BombSquad version 1.6.5
Provides functionality for dumping player stats to disk between rounds.
"""

import threading, json, os, urllib.request
import mysettings

table_style = "{width:100%;border: 3px solid black;border-spacing: 5px;border-collapse:collapse;text-align:center;background-color:#fff}"
heading_style = "{border: 3px solid black;text-align:center;}"
html_start = f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Test Server</title>
        <style>table{table_style} th{heading_style}</style>
    </head>
    <body>
        <h3 style="text-align:center">Top 200 Players of {mysettings.server_name}</h3>
        <table border=1>
            <tr>
                <th><b>Rank</b></th>
                <th style="text-align:center"><b>Name</b></th>
                <th><b>Score</b></th>
                <th><b>Kills</b></th>
                <th><b>Deaths</b></th>
                <th><b>Games Played</b></th>
            </tr>
"""
#                <th><b>Total Damage</b></th>  #removed this line as it isn't crt data
def refreshStats():
    # lastly, write a pretty html version.
    # our stats url could point at something like this...
    stats = mysettings.get_stats()
    # f = open(mysettings.html_file, "w")
    # f.write(html_start)
    entries = [
        (a["scores"], a["kills"], a["deaths"], a["games"], a["name_html"], a["aid"])
        for a in stats.values()
    ]
    # this gives us a list of kills/names sorted high-to-low
    entries.sort(reverse=True)
    rank = 0
    # toppers = {}
    pStats = stats
    toppersIDs = []
    for entry in entries:
        if True:
            rank += 1
            scores = str(entry[0])
            kills = str(entry[1])
            deaths = str(entry[2])
            games = str(entry[3])
            name = str(entry[4])
            aid = str(entry[5])
            if rank < 6:
                toppersIDs.append(aid)
            # The below kd and avg_score will not be added to website's html document, it will be only added in stats.json
            try:
                kd = str(float(kills) / float(deaths))
                kd_int = kd.split(".")[0]
                kd_dec = kd.split(".")[1]
                p_kd = kd_int + "." + kd_dec[:3]
            except Exception:
                p_kd = "0"
            try:
                avg_score = str(float(scores) / float(games))
                avg_score_int = avg_score.split(".")[0]
                avg_score_dec = avg_score.split(".")[1]
                p_avg_score = avg_score_int + "." + avg_score_dec[:3]
            except Exception:
                p_avg_score = "0"
            if damage_data and aid in damage_data:
                dmg = damage_data[aid]
                dmg = str(str(dmg).split(".")[0] + "." + str(dmg).split(".")[1][:3])
            else:
                dmg = 0
            pStats[str(aid)]["rank"] = int(rank)
            pStats[str(aid)]["scores"] = int(scores)
            pStats[str(aid)]["total_damage"] += float(dmg)  # not working properly
            pStats[str(aid)]["games"] = int(games)
            pStats[str(aid)]["kills"] = int(kills)
            pStats[str(aid)]["deaths"] = int(deaths)
            pStats[str(aid)]["kd"] = float(p_kd)
            pStats[str(aid)]["avg_score"] = float(p_avg_score)

    #             if rank < 201:
    #                 # <td>{str(dmg)}</td> #removed this line as it isn't crt data
    #                 f.write(
    #                     f"""
    #             <tr>
    #                 <td>{str(rank)}</td>
    #                 <td style="text-align:center">{str(name)}</td>
    #                 <td>{str(scores)}</td>
    #                 <td>{str(kills)}</td>
    #                 <td>{str(deaths)}</td>
    #                 <td>{str(games)}</td>
    #             </tr>"""
    #                 )
    #     f.write(
    #         """
    #         </table>
    #     </body>
    # </html>"""
    #     )
    #     f.close()

    f2 = open(mysettings.stats_file, "w")
    f2.write(json.dumps(pStats, indent=4))
    f2.close()

    # if True:  # mysettings.mysettings[enableTop5commands]:
    #     import roles

    #     roles.toppersList = toppersIDs
    #     with open(mysettings.python_path + "/roles.py") as file:
    #         s = [row for row in file]
    #         s[7] = "toppersList = " + str(roles.toppersList) + "\n"
    #         f = open(mysettings.python_path + "/roles.py", "w")
    #         for i in s:
    #             f.write(i)
    #         f.close()


def get_name_from_master_server(account_id):
    """
    Get the player name from the master bombsquad server
    """
    url = "http://bombsquadgame.com/accountquery?id=" + account_id
    try:
        response = json.loads(urllib.request.urlopen(urllib.Request(url)).read())
        print("response variable from mystats.py line 183:")
        print(response)
        return response["name_html"]
    except Exception as exn:
        print(exn)
        return None


def update(score_set):
    """
    Given a Session's ScoreSet, tallies per-account kills
    and passes them to a background thread to process and
    store.
    """
    # look at score-set entries to tally per-account kills for this round
    account_names = {}
    account_kills = {}
    account_deaths = {}
    account_scores = {}

    for p_entry in score_set.get_records().values():
        account_id = p_entry.player.get_account_id()
        if account_id is not None:
            full_name = p_entry.getname(True)
            name = full_name if full_name else p_entry.getname()
            print(f"fn => {full_name}, n => {name}")
            account_names.setdefault(account_id, "")
            account_names[account_id] = name if name else str(account_id)
            account_kills.setdefault(account_id, 0)  # make sure exists
            account_kills[account_id] += p_entry.accum_kill_count
            account_deaths.setdefault(account_id, 0)  # make sure exists
            account_deaths[account_id] += p_entry.accum_killed_count
            account_scores.setdefault(account_id, 0)  # make sure exists
            account_scores[account_id] += p_entry.accumscore
    # Ok; now we've got a dict of account-ids and kills.
    # Now lets kick off a background thread to load existing scores
    # from disk, do display-string lookups for accounts that need them,
    # and write everything back to disk (along with a pretty html version)
    # We use a background thread so our server doesn't hitch while doing this.
    if account_scores:
        UpdateThread(
            account_names, account_kills, account_deaths, account_scores
        ).start()


class UpdateThread(threading.Thread):
    def __init__(self, account_names, account_kills, account_deaths, account_scores):
        threading.Thread.__init__(self)
        self._account_names = account_names
        self._account_kills = account_kills
        self.account_deaths = account_deaths
        self.account_scores = account_scores

    def run(self):
        # pull our existing stats from disk
        try:
            stats = mysettings.get_stats()
        except:
            return

        # now add this batch of kills to our persistant stats
        for account_id, kill_count in self._account_kills.items():
            # add a new entry for any accounts that dont have one
            if account_id not in stats:
                # also lets ask the master-server for their account-display-str.
                # (we only do this when first creating the entry to save time,
                # though it may be smart to refresh it periodically since
                # it may change)
                name_html = get_name_from_master_server(account_id)
                stats[account_id] = {
                    "rank": 0,
                    "name_html": (
                        name_html if name_html else self._account_names[account_id]
                    ),
                    "scores": 0,
                    "total_damage": 0,
                    "kills": 0,
                    "deaths": 0,
                    "games": 0,
                    "kd": 0,
                    "avg_score": 0,
                    "aid": str(account_id),
                }
            # now increment their kills whether they were already there or not
            # stats[account_id]["name_html"] = self._account_names[account_id]
            stats[account_id]["kills"] += kill_count
            stats[account_id]["deaths"] += self.account_deaths[account_id]
            stats[account_id]["scores"] += self.account_scores[account_id]
            # also incrementing the games played and adding the id
            stats[account_id]["games"] += 1
            stats[account_id]["aid"] = str(account_id)
        # dump our stats back to disk
        print(json.dumps(stats, indent=2))
        from datetime import datetime

        with open(mysettings.stats_file, "w") as f:
            json.dump(stats, f)
        # aaand that's it!  There IS no step 27!
        now = datetime.now()
        update_time = now.strftime("%S:%M:%H - %d %b %y")
        print(
            f"Added {str(len(self._account_kills))} account's stats entries. || {str(update_time)}"
        )
        refreshStats()
