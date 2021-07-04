import EgybestScrapeService
from VidstreamScrapeService import extractDownloadLink
import os
# obj = EgybestScrapeService.Series("http://room.egybest.biz/series/dark-2017/?ref=search-p1")

# print(obj.info["title"], obj.synopsis)

# print(extractDownloadLink(obj.getSeasonByNum(2).getEpisodeByNum(5).getDl()[0]['link']))
print(extractDownloadLink("https://vidstream.online/f/nbXsnL934v"))
# for season in obj.getAllSeasons().values():
#     for episode in season.getAllEpisodes().values():
#         print(f'doing {episode.info["title"]}')
#         with open('/home/fedi/Desktop/links.txt', 'a') as f:
#             f.write('{0}\n'.format(extractDownloadLink(episode.getDl()[0]['link'])))

