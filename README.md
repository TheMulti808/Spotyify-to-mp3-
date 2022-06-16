# Spotyify-to-mp3-
Simple music downloader

How it works?
Its using Selenium to get and analyze your Spotify playlist, and then searching videos by author and title on youtube.
You have two ways to search videos, using youtube-search or again Selenium. Change 'searchWithSelenium' variable in code.
I have been rate-limited by youtube-search so thats why i added option with Selenium.

When script have all youtube links its starting download it one by one using yt_dlp (better fork of youtube-dl)
