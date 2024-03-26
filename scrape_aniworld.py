#!/usr/bin/env python3
import requests
import sys
import bs4
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urljoin

ARGS = sys.argv
URL = ""

if len(ARGS) > 1:
    URL = ARGS[1]
else:
    print("Usage: ", ARGS[0], " ANIME_URL")
    print("NOTE: URL without seasons or episodes")
    exit(-1)
has_movie = False

page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
seasons = int(soup.find("meta", itemprop="numberOfSeasons").get("content"))
if seasons >= 1:
    if soup.find("a", title="Alle Filme") != None:
        seasons -= 1
        has_movie = True

prompt = str("Enter Season[1-" + str(seasons) + "]:\n")
season: int = input(prompt)

page_season = requests.get(URL + "/staffel-" + str(season))
soup = BeautifulSoup(page_season.content, "html.parser")

episodes: bs4.element.ResultSet = soup.find_all("tr", itemprop="episode")
links = dict()
e_max = 0
for episode in episodes:
    e_id = int(episode.get("data-episode-season-id"))
    links[e_id] = episode.find("a", itemprop="url")["href"]
    e_max = max(e_max, e_id)

prompt = str("Enter Episode to start from [1-" + str(e_max) + "]:\n")
start_episode = input(prompt)
prompt = str("Download all? [y|s|N] (s = single choose):\n")
download = input(prompt)
processes = []

for num, link_id in enumerate(links):
    if int(link_id) >= int(start_episode):
        new_url = urljoin(URL, str(links[link_id]))
        episode_page = requests.get(new_url)
        soup = BeautifulSoup(episode_page.content, "html.parser")
        next_link = soup.find("i", title="Hoster Vidoza").find_parent(
            "a", {"class": "watchEpisode"})["href"]
        real_page = requests.get(urljoin(URL, str(next_link)))
        soup = BeautifulSoup(real_page.content, "html.parser")
        real_link = soup.find("video", id="player").find("source")["src"]
        print(real_link)
        if (download.__eq__("y")):
            p = subprocess.Popen([
                "wget", "-O",
                str("episode-" + str(num + 1) + ".mp4"), real_link
            ])
            processes.append(p)

        elif (download.__eq__("s")):
            prompt = str("Download Episode " + str(num + 1) + "? [y|N]:\n")
            download_single = input(prompt)
            if download_single.__eq__("y"):
                p = subprocess.Popen([
                    "wget", "-O",
                    str("episode-" + str(num + 1) + ".mp4"), real_link
                ])
                processes.append(p)

for process in processes:
    process.wait()

# prompt = str("Enter Episode[1-" + str(e_max) + "] (0 for all):\n")
# episode: int = input(prompt)

# print(episodes)
