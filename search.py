# -*- coding:utf-8 -*-
#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
#from oauth2client.tools import argparser
import argparse
import os


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyB19DjZmBGlpRLFGA-42-8JSF05U5ETouA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_BASE_VIDEO_URL = "https://www.youtube.com/watch?v="

nextPageToken = ""
videoNames = []
videoUrls = ""
downloadNumber = 0;

def youtube_search(options):
  global nextPageToken
  global videoNames
  global videoUrls

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    videoCategoryId=options.videoCategoryId,
    pageToken=options.pageToken,
    type=options.type,
    order=options.order,
    part="id,snippet",
    maxResults=options.max_results
  ).execute()

  print "PageToken for this search: " + nextPageToken + " (you can use this token to restart download if it fails)"

  # update token for next search
  nextPageToken = search_response.get("nextPageToken")

  #videos = []
  #channels = []
  #playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videoNames.append("%s" % (search_result["snippet"]["title"]))
      videoUrls += (YOUTUBE_BASE_VIDEO_URL + search_result["id"]["videoId"]) + " "
      #videoUrls.append("%s" % (YOUTUBE_BASE_VIDEO_URL + search_result["id"]["videoId"]))
      #videos.append("%s (%s)" % (search_result["snippet"]["title"],
      #                           search_result["id"]["videoId"]))
    #elif search_result["id"]["kind"] == "youtube#channel":
    #  channels.append("%s (%s)" % (search_result["snippet"]["title"],
    #                               search_result["id"]["channelId"]))
    #elif search_result["id"]["kind"] == "youtube#playlist":
    #  playlists.append("%s (%s)" % (search_result["snippet"]["title"],
    #                                search_result["id"]["playlistId"]))

  #print "Videos:\n", "\n".join(videos), "\n"
  #print "Channels:\n", "\n".join(channels), "\n"
  #print "Playlists:\n", "\n".join(playlists), "\n"


if __name__ == "__main__":
  global videoUrls
  global videoNames
  global downloadNumber

  while(1):
    # init before while loop
    parser = argparse.ArgumentParser()
    videoNames = []
    videoUrls = ""

    # search query
    parser.add_argument("--q", help="Search term", default="")
    # 10 : Music
    parser.add_argument("--videoCategoryId", help="Video Category Id", default="10")
    # type : channel or playlist or video
    parser.add_argument("--type", help="Search Type", default="video")
    # order by view count asc
    parser.add_argument("--order", help="Order", default="viewCount")
    parser.add_argument("--max-results", help="Max results", default=50)

    parser.add_argument("--pageToken", help="search token", default=nextPageToken)
    args = parser.parse_args()

    try:
      youtube_search(args)
    except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

    # termination condition
    if not videoUrls:
      break

    downloadNumber += len(videoNames)
    print "Downloading number of videos: %d" % (downloadNumber)
    print "Downloading video list:\n", "\n".join(videoNames), "\n"
    #print videoUrls

    os.system("youtube-dl -f bestaudio " + videoUrls)
  