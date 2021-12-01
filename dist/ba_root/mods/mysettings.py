import json
import os

import _ba

stats_file = "/var/www/html/stats.json"
html_file = "/var/www/html/stats.html"
series_dir = "/var/www/html/series"
server_name = "வாய்ச்சொல் வீரர்கள் (Vaaichol Veerargal)"
python_path = _ba.env()["python_directory_user"]


def get_stats():
    stats = {}
    if os.path.exists(stats_file):
        with open(stats_file) as f:
            stats = json.load(f)
    return stats
