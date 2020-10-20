import EgybestScrapeService
from VidstreamScrapeService import extractDownloadLink
import os

obj = EgybestScrapeService.Series("https://room.egybest.biz/series/narcos-2015/?ref=search-p1")

# print(obj.info["title"], obj.synopsis)

# print(extractDownloadLink(obj.getSeasonByNum(2).getEpisodeByNum(5).getDl()[0]['link']))

# for season in obj.getAllSeasons().values():
#     for episode in season.getAllEpisodes().values():
#         print(f'doing {episode.info["title"]}')
#         with open('/home/fedi/Desktop/links.txt', 'a') as f:
#             f.write('{0}\n'.format(extractDownloadLink(episode.getDl()[0]['link'])))

