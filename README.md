# Video-Creation-Tool
### Written by Navraj Eari

- Creates a 60s video from a reddit post via Web Scraping. With Text-To-Speech (TTS), dictates the title, selftext, and comments + replies to compile a short video with background gameplay and music for entertainment.

## Libraies Used:
- PRAW
- Emoji
- Textwrap
- PyTube
- Selenium
- MoviePy
- RedDownloader
- PIL
- Subprocess
- Mutagen
- PyTesseract

## How to use:
- Download the required libraies.
- The "client_secrets.json" file has not been provided for obvious reasons, hence you must create it youself. [Follow guide here.](https://www.geeksforgeeks.org/how-to-get-client_id-and-client_secret-for-python-reddit-api-registration/)
- Ensure you have a .mp4 and .mp3 in the "backgroundVid" and "music" folder respectfully, aswell as the link for the reddit post you want to scrape.
- The name of the .mp3 file will be shown in the top left, so ensure it is named appropriately (name, artist). 
- Run the "main.py" script, and either copy/paste the reddit post link, or click enter to use the ones in the "links.txt file"
- After a few minutes, the final video will be created in the "finalVid" folder.

## Features:
- Works for any post from any subreddit, whether its a selftext, link, image, and video post.
- If its a image or video post, will display the content in the final video.
- Reddit post links can be stored in the "links.txt" file in bulk; 1 per line. If you run the script and press "Enter", it will scrape the first link.
- Script will automatically get enough comments and replies (max 1 reply per parent) to fufil a 60s video.
- If the selftext is > 60s, allow for the video to be this long, but gets no comments
- Uses Edge TTS. change TTS voice, speed, volume and pitch. [Learn more here.](https://github.com/rany2/edge-tts)
- Abilty to filter and censor words from dictation and image itself, and replacing them with other words.
- Can use your own custom background music and gameplay. Simply place them in the "music" and "backgroundVid" folder respectfully, and the script will choose one at random.
- Final video is 720 x 1280 and 60s long. However the length can vary depending on how long the selftext is.
- Added watermark in the top left to give credit to whose background music you are using by simply using the name of the music file.
- Also creates a supplementive .txt file, which contains information abou the video, such as the link author, and tags to use for social media. 

## Examples:
https://user-images.githubusercontent.com/102254245/184902050-8ff216d4-4145-4588-b503-4702542a3e94.mp4

https://user-images.githubusercontent.com/102254245/184902301-c23ead63-fbc6-4f1c-a113-cd59162a376a.mp4
