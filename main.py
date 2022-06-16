from __future__ import unicode_literals
import requests, sys, os, time
import yt_dlp as youtube_dl
from youtube_search import YoutubeSearch
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

spotifyLink = r"https://open.spotify.com/playlist/"
youtubeSearchLink = r"https://www.youtube.com/results?search_query="
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
PATH = "C:\Program Files (x86)\chromedriver.exe" #selenium chrome driver path
driver = webdriver.Chrome(PATH)
searchWithSelenium = True
playlist = {}
playlist["songs"] = []
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist':True,
    'keepvideo': False,
    'http-chunk-size': "10M",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

'''
Quick explanation:
On beggining my idea was to use requests instead of selenium, but i left this idea because of few reasons:
- I wanted to get some more experience with selenium and data-mining
- Spotify forces me to use their API

Thats why final code is writed in Selenium.

'''

def wfe(driver, byWhat, arg): #wait for element, function because im lazy
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((byWhat, arg)))
    return element

def downloadWithApi():
    apiLink = "https://convert2mp3s.com/api/single/mp3?url="
    for song in playlist["songs"]:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([song["youtubelink"]])
    print("Download completed, enjoy your music!")
    sys.exit()

def searchYoutubeWithSelenium(song):
    currentYoutubeLink = "{}{} {}".format(youtubeSearchLink, song["author"], song["title"])
    driver.get(currentYoutubeLink)
    mainContainer = wfe(driver, By.XPATH, "//div[@id = 'contents' and @class= 'style-scope ytd-item-section-renderer']")
    songContainer = mainContainer.find_elements(by=By.TAG_NAME, value='ytd-video-renderer')[0] #always first result, probably best one
    songLink = songContainer.find_element(by=By.TAG_NAME, value='a').get_attribute("href")
    song["youtubelink"] = songLink
    songId = songLink.split("watch?v=", 1)[1]
    song["youtubeid"] = songId
    return True


def getYoutubeLinks():
    try:
        for song in playlist["songs"]:
            if searchWithSelenium:
                searchYoutubeWithSelenium(song)
            else:
                driver.quit()
                contentToSearch = '{} {}'.format(song["author"], song["title"])
                try:
                    results = YoutubeSearch(contentToSearch, max_results=1).to_dict()
                except:
                    pass
                finally:
                    song["youtubelink"] = "{}{}".format("https://www.youtube.com/",results[0]["url_suffix"])
        print("Music links collected!")
    except Exception as e:
        print("Error:", e)
        driver.quit()
        sys.exit("Error")
    finally:
        driver.quit()
        downloadWithApi()


def openSpotifyMiner():
    try:
        driver.get(playlist["link"])
        time.sleep(1)
        wfe(driver, By.ID, "onetrust-accept-btn-handler").click() #cookie window
        playlist["title"] = wfe(driver, By.CLASS_NAME, "hVBZRJ").text
        playlist["author"] = wfe(driver, By.XPATH, '//a[@data-testid="creator-link"]').text
        playlist["totalTime"] = wfe(driver, By.CLASS_NAME, "UyzJidwrGk3awngSGIwv").text
        playlist["totalSongs"] = wfe(driver, By.CLASS_NAME, "ebHsEf ").text.strip(","+playlist["totalTime"])
        songsContainer = driver.find_elements(by=By.XPATH, value='//div[@aria-selected="false"]')
        for songContainer in songsContainer:
            song = {}
            song["title"] = songContainer.find_element(by=By.CLASS_NAME, value='fCtMzo').text
            song["author"] = songContainer.find_element(by=By.CLASS_NAME, value='hHrtFe').text 
            song["duration"] = songContainer.find_element(by=By.CLASS_NAME, value='Btg2qHSuepFGBG6X0yEN').text 
            song["album"] = songContainer.find_element(by=By.CLASS_NAME, value='ebHsEf').text  
            playlist["songs"].append(song)
    except Exception as e:
        print("Error:", e)
        driver.quit()
        sys.exit("Error")
    finally:
        print("Songs in your playlist:")
        for song in playlist["songs"]:
            print('{:25s} - {:35s}, {:5s} ( {:10s} )'.format(song["author"], song["title"], song["duration"], song["album"]))
        print("\n\n")
        getYoutubeLinks()


       


def main():
    os.system("CLS")
    print("Welcome in Spotify To Mp3!\nGet ready and enter your Spotify Playlist Id!\nDont know how to find it? Share your playlist and copy string after '/playlist/'\n")
    print("e.g. for 'https://open.spotify.com/playlist/1bv3QPNiTxX3XTSEd0iaWw' playlist id is  '1bv3QPNiTxX3XTSEd0iaWw'")
    while True:
        playlistId = input("Enter playlist id: ")
        playlist["id"] = playlistId
        playlist["link"] = '{}{}'.format(spotifyLink, playlistId)
        if len(playlistId) < 5:
            os.system("CLS")
            print("Probably invalid playlist id, try again!")
        else: break
    os.system("CLS")
    print(f"Your playlist id is {playlistId}!\nVerifying the existence of the playlist...")
    spotifySite = requests.get(playlist["link"] , headers=headers)
    spotifySite = BeautifulSoup(spotifySite.text, 'html.parser')
    if "Page not found" in spotifySite.text:
        print("Entered wrong playlist id, try Again!")
        time.sleep(3)
        main()
    print("Playlist found!")
    openSpotifyMiner()










if __name__ == "__main__":
    main()
