import praw
import json
import re
import os
import random
import numpy as np
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.common.by import By
from moviepy.editor import *
from moviepy.video.fx.all import crop
from RedDownloader import RedDownloader
from PIL import Image, ImageDraw
from cleantext import clean
from subprocess import check_output

options = webdriver.EdgeOptions()
options.headless = True
driver = webdriver.Edge(options=options)
# loads the webdriver

tts = 'cmd /c edge-tts --voice en-US-JennyNeural --rate=1.50 --volume=150 --text "{}" --write-media {}'
# initates shell command for edge tts. can change voice and speed.

credentials = 'client_secrets.json' 
with open(credentials) as f:
    creds = json.load(f)
    reddit = praw.Reddit(client_id=creds['client_id'], client_secret=creds['client_secret'], user_agent=creds['user_agent'],
                        redirect_uri=creds['redirect_uri'], refresh_token=creds['refresh_token'], username=creds['username'],
                        password=creds['password']) # reddit credentials to use praw
    f.close()

def getSubmissions(): # prepares reddit post for further work
    print("\n(Press enter to just use ones in .txt)")

    try: # allows the user to copy/paste own reddit link
        question = input("Input reddit link: ")
        submission = reddit.submission(url = question)
        submission.comment_sort = 'top'
        link = "https://www.reddit.com" + submission.permalink
        submissionID = re.search('(?<=comments/)(\w+)', link).group(1)
        # gets a bunch of info from submission, sorts comment by top

        with open('finalVid\\' + submissionID + '_info' + '.txt', 'w') as f:
            f.write(str(submission.title) + "\n")
            f.write("https://www.reddit.com" + str(submission.permalink) + " post by u/" + str((submission.author).name) + "\n")
            f.write("#reddit #askreddit #fyp #foryoupage #reddit_tiktok #redditreadings #redditstories" + "\n")
            f.write("#reddit, #askreddit, #fyp, #foryoupage, #reddit_tiktok, #redditreadings, #redditstories" + "\n")
            f.close()
            # writes submission info into a .txt for later viewing

    except: # if you press "enter", script will use the first reddit link found in the "links.txt" file
        with open("links.txt", "r+") as fp:
            firstline = fp.readline()
            lines = fp.readlines()
            fp.seek(0)
            fp.truncate()
            fp.writelines(lines[0:])
            fp.close()
            # logic to open "links.txt", read first line, then delete it
        
        submission = reddit.submission(url = firstline) # we are using this to test capabilities with a post
        submission.comment_sort = 'top'
        link = "https://www.reddit.com" + submission.permalink
        submissionID = re.search('(?<=comments/)(\w+)', link).group(1)
        
        with open('finalVid\\' + submissionID + '_info' + '.txt', 'w') as f:
            f.write(str(submission.title) + "\n")
            f.write("https://www.reddit.com" + str(submission.permalink) + " post by u/" + str((submission.author).name) + "\n")
            f.write("#reddit #askreddit #fyp #foryoupage #reddit_tiktok #redditreadings #redditstories #atia" + "\n")
            f.write("#reddit, #askreddit, #fyp, #foryoupage, #reddit_tiktok, #redditreadings, #redditstories, #aita" + "\n")
            f.close()
        
    finally:
        return submission # a submission object is returned

def textCleaner(text): # cleans the selftext for special chars, acryonyms, and profanity
    text = clean(text, no_urls = True, no_emoji = True, replace_with_url = "")
    text = text.replace('\n', '. ').replace('\r', '').replace('"', '').replace("'", '').replace("/", "").replace("*", "")

    profan1 = {"TIFU":"Today I efed up", "AITA":"Am I the a-hole", "BIL":"brother-in-law", "SIL":"sister-in-law"}
    profan2 = {"tf":"the hell", "ass":"butt"}
    profan3 = {"fuck":"f", "bitch":"dog", "cunt":"cow", "asshole":"a-hole", "rape":"defile", "dick":"schlong",
               "wtf": "what the hell"}

    for word, replacement in profan1.items():
        text = re.sub(word, replacement, text)
    for word, replacement in profan2.items():
        text = re.sub("\W" + word + "\W", replacement, text, flags=re.IGNORECASE)
    for word, replacement in profan3.items():
        text = re.sub(word, replacement, text, flags=re.IGNORECASE)
    
    return text

def add_corners(im, rad): # adds rounded corners to images
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def imageOpt(img): # optimises the image. inreases width to 600
    basewidth = 600
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    return img

def getPageImage(submission): # prepares our post for a screenshot
    bodyCounter = 0
    link = "https://www.reddit.com" + submission.permalink
    submissionID = re.search('(?<=comments/)(\w+)', link).group(1)
    driver.get(link) # loads page into webdriver for further work
    driver.find_element_by_xpath('//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[3]/div[1]/section/div/section/section/form[2]/button').click()

    if driver.find_elements_by_class_name('gCpM4Pkvf_Xth42z4uIrQ'):
        driver.find_element_by_class_name('gCpM4Pkvf_Xth42z4uIrQ').click()
        # if the page has a SPOILER button, it will press it so the post can be seen
    if driver.find_elements_by_xpath('//*[@id="AppRouter-main-content"]/div/div[1]/div/div/div[2]/button'):
        driver.find_element_by_xpath('//*[@id="AppRouter-main-content"]/div/div[1]/div/div/div[2]/button').click()
        driver.find_element_by_class_name('gCpM4Pkvf_Xth42z4uIrQ').click()
        # if the page is NSFW, will click buttons to allow viewing
        
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    driver.set_window_size(420, S('Height')) # May need manual adjustment                                                                                                         
    # logic to just page size

    if hasattr(submission, 'post_hint'):
        if submission.post_hint == 'hosted:video':
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)                                                                                                 
            driver.find_element(By.CLASS_NAME, '_eYtD2XCVieq6emjKBH3m').screenshot("image\\0.png")
            im = imageOpt(Image.open("image\\0.png"))
            add_corners(im, rad = 10).save("image\\0.png")
            RedDownloader.Download(url = link, quality = 360, destination = "")
            bodyCounter += 1
            return bodyCounter
            # if post is a video, will only dictate and ss the title, and also downloads vid for later

        elif submission.post_hint == 'image':
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)                                                                                                   
            driver.find_element(By.CLASS_NAME, '_eYtD2XCVieq6emjKBH3m').screenshot("image\\0.png")
            im = imageOpt(Image.open("image\\0.png"))
            add_corners(im, rad = 10).save("image\\0.png")
            RedDownloader.Download(url = link, quality = 360, destination = "")
            bodyCounter += 1
            return bodyCounter
            # if post is an image, will only dictate and ss the title, and also downloads image for later

        elif submission.post_hint == 'link':
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)                                                                                                   
            driver.find_element(By.ID, 't3_' + submissionID).screenshot("image\\0.png")
            im = imageOpt(Image.open("image\\0.png"))
            add_corners(im, rad = 30).save("image\\0.png")
            bodyCounter += 1
            return bodyCounter
            # if post is a link post, only dicatate title
        
    elif re.match("https://www.youtube.com/\S+", submission.url):
        command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
        os.system(command)                                                                                                   
        driver.find_element(By.CLASS_NAME, '_eYtD2XCVieq6emjKBH3m').screenshot("image\\0.png")
        im = imageOpt(Image.open("image\\0.png"))
        add_corners(im, rad = 10).save("image\\0.png")
        YouTube(submission.url).streams.get_by_resolution("360p").download(filename = "downloaded.mp4")
        bodyCounter += 1
        return bodyCounter
        # if post is a youtube link, download video, and only ss and dictate title

    else: # selftext post
        if str(submission.subreddit) == "AskReddit": # this sub doesnt have a selftext, so we will get a good looking title element
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)
            driver.find_element(By.ID, 't3_' + submissionID).screenshot("image\\0.png")
            im = imageOpt(Image.open("image\\0.png"))
            add_corners(im, rad = 30).save("image\\0.png")
            bodyCounter += 1
            return bodyCounter
        else: # saves an audio file of the title and selftext, sepearted per paragraph
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)                                                                                                 
            driver.find_element(By.CLASS_NAME, '_eYtD2XCVieq6emjKBH3m').screenshot("image\\0.png")
            im = imageOpt(Image.open("image\\0.png"))
            add_corners(im, rad = 10).save("image\\0.png")
            bodyCounter += 1

            for para in driver.find_elements_by_xpath("//div[@class='_3xX726aBn29LDbsDtzr_6E _1Ap4F5maDtT1E1YuCiaO0r D3IL3FD0RFy_mkKLPwL4']//p[@class='_1qeIAgB0cPwnLhDF9XSiJM']"):
                command = tts.format(textCleaner(para.text), "audio/" + str(bodyCounter) + ".mp3")
                os.system(command)  
                para.screenshot("image\\" + str(bodyCounter) + ".png")
                im = imageOpt(Image.open("image\\" + str(bodyCounter) + ".png"))
                add_corners(im, rad = 10).save("image\\" + str(bodyCounter) + ".png")
                bodyCounter += 1

            return bodyCounter
        
def getComments(submission): # gets comments from submission, if its <= 1000 characters
    allComments = {}
    submission.comments.replace_more() # this takes alot of time
    for comment in ([comment for comment in list(submission.comments) if (comment.stickied == False) & (len(textCleaner(comment.body)) <= 600)])[:10]: # first [7] parent comments
        allComments.update({comment: 1}) # value 1 is parent

        if len(list(comment.replies)) > 0: # if the parent comment has children
            for comment1 in ([comment for comment in list(comment.replies) if len(textCleaner(comment.body)) <= 600])[:1]: # for each child comment, up till [1] children...
                allComments.update({comment1: 2}) # value 2 is child

    return allComments 
    # a dictionary, with the key as the comment object, and value as 1 or 2. 1 is parent, 2 is child

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result # function to add left margin to child image

def get_concat_v_resize(im1, im2, resample=Image.BICUBIC, resize_big_image=True):
    if im1.width == im2.width:
        _im1 = im1
        _im2 = im2
    elif (((im1.width > im2.width) and resize_big_image) or
          ((im1.width < im2.width) and not resize_big_image)):
        _im1 = im1.resize((im2.width, int(im1.height * im2.width / im1.width)), resample=resample)
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize((im1.width, int(im2.height * im1.width / im2.width)), resample=resample)
    dst = Image.new('RGB', (_im1.width, _im1.height + _im2.height))
    dst.paste(_im1, (0, 0))
    dst.paste(_im2, (0, _im1.height))
    return dst # function to stitch 2 images vertically

def generateMedia(comments, bodyCounter): # for each comment in the list, get the link, body, screenshot and audio
    objectNames = list(str(i) for i in range(bodyCounter))
    no = bodyCounter
    parent = bodyCounter - 1
    for comment, type in comments.items():

        if type == 1: # if its a parent comment, take a ss
            commentlink = "https://www.reddit.com" + comment.permalink
            URL = commentlink
            driver.get(URL)
            S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
            driver.set_window_size(420, S('Height')) # May need manual adjustment
            driver.find_element(By.XPATH, '//*[@id="t1_{}"]/div[2]'.format(comment.id)).screenshot("image\\"+ str(no) + ".png")

            try: # if this parent comment has no child, do the processing now
                if list(comments.values())[no] == 1: 
                    im1 = Image.open("image\\"+ str(no) + ".png")
                    im1 = imageOpt(im1)
                    add_corners(im1, rad = 30).save("image\\"+ str(no) + ".png")
            except Exception:
                    im1 = Image.open("image\\"+ str(no) + ".png")
                    im1 = imageOpt(im1)
                    add_corners(im1, rad = 30).save("image\\"+ str(no) + ".png")

        elif type == 2: # if its a child comment, stich it vertically with the parent comment
            commentlink = "https://www.reddit.com" + comment.permalink
            URL = commentlink
            driver.get(URL)
            S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
            driver.set_window_size(420, S('Height')) # May need manual adjustment
            driver.find_element(By.XPATH, '//*[@id="t1_{}"]/div[2]'.format(comment.id)).screenshot("image\\"+ str(no) + ".png")

            im1 = Image.open("image\\"+ str(parent) + ".png")
            im1 = imageOpt(im1)
            im2 = Image.open("image\\"+ str(no) + ".png")
            im2 = imageOpt(im2)
            im2 = add_margin(im2, 0, 0, 0, 25, (245, 246, 246))
            
            im = get_concat_v_resize(im1, im2, resize_big_image=True)
            add_corners(im, rad = 30).save("image\\"+ str(no) + ".png")
            add_corners(im1, rad = 30).save("image\\"+ str(parent) + ".png") # for logic reasons, round of the parent here, and not above
        
        parent += 1
        
        command = tts.format(textCleaner(comment.body), "audio/" + str(no) + ".mp3")
        os.system(command)
        # dictate comments

        objectNames.append(str(no))
        no += 1

    driver.quit() # driver no longer needed

    return objectNames # a list with strings, each one representing the name of the media generated
    # so "1" is the name of the file of the first comment, for the image (.png) and audio (.mp3)

def movieCreator(objectNames): # for each commenet, combine .png and .mp3 into a video
    compositeList = []
    cum = 0 # cumlative time of clips
    for name in objectNames:
        image_path = "image/" + name + ".png"
        audio_path = "audio/" + name + ".mp3"
        audio_clip = AudioFileClip(audio_path) # loads .mp3
        image_clip = ImageClip(image_path) # loads image as a clip
        video_clip = image_clip.set_audio(audio_clip) # sets the audio on clip
        video_clip.duration = audio_clip.duration # sets the clip duration to be aslong as audio
        video_clip.fps = 1
        compositeList.append(video_clip.set_start(cum)) # appends video vlip to a list
        cum += video_clip.duration

    return compositeList # returns a lists, where each element is a video clip object

def hasAudio(file_path): # checks if downloaded video has audio
  command = ['ffprobe', '-show_streams',
           '-print_format', 'json', file_path]
  output = check_output(command)
  parsed = json.loads(output)
  streams = parsed['streams']
  audio_streams = list(filter((lambda x: x['codec_type'] == 'audio'), streams))
  return len(audio_streams) > 0

def finalVideoTT(compositeList, submission, bodyCounter): # creates the final video for tiktok
    finalList = []

    bodyCheck = [clip.duration for clip in compositeList[:bodyCounter]]
    cumBodyCheck = sum(bodyCheck) # this checks the length of the selftext

    if cumBodyCheck <= 60: # if selftext is short, just make sure enough clips are passed for 60s
        timeList = [clip.duration for clip in compositeList]
        cumList = (np.cumsum(timeList)).tolist()
        cumList60 = [x for x in cumList if x <= 70]
        compositeList60 = compositeList[:len(cumList60)] # logic which only passes enough clips for 60s
        cum = sum(clip.duration for clip in compositeList60)

    elif cumBodyCheck > 60: # if selftext is long, then only pass the clips related to the title + selftext
        compositeList60 = compositeList[:bodyCounter]
        cum = cumBodyCheck

    link = "https://www.reddit.com" + submission.permalink
    submissionID = re.search('(?<=comments/)(\w+)', link).group(1)

    backTemp = VideoFileClip("backgroundVid/" + random.choice(os.listdir("backgroundVid/"))).without_audio()    
    if backTemp.duration >= cum:
        backTemp = backTemp.subclip(0, cum)
    elif backTemp.duration < cum:
        backTemp = backTemp.loop(duration = cum)
    (w, h) = backTemp.size
    if (w == 720) & (h == 1280):
        back = backTemp
    elif (w == 1080) & (h == 1920):
        back = backTemp.resize((720,1280))
    else:
        backCropped = crop(backTemp, width=405, height=h, x_center=w/2, y_center=h/2)
        back = backCropped.resize((720,1280))
    # loads a random background clip from folder, and adjusts it for stuff

    musicTemp = AudioFileClip("music/" + random.choice(os.listdir("music/")))
    if musicTemp.duration >= cum:
        music = musicTemp.subclip(0, cum).volumex(0.10)
    elif musicTemp.duration < cum:
        music = musicTemp.volumex(0.10)
        music = afx.audio_loop(music, duration = cum)
    if hasattr(submission, 'post_hint'): # no music if theres a video
        if submission.post_hint == 'hosted:video':
            if hasAudio("downloaded.mp4") == True:
                music = musicTemp.volumex(0)
            else:
                pass
    if re.match("https://www.youtube.com/\S+", submission.url):
        if hasAudio == True:
            music = musicTemp.volumex(0)
        else:
            pass
    # loads a music clip from folder, and adjusts it for stuff

    background = back.set_audio(music)
    # loads a random music file from folder, adjusts some stuff, and appends it to the background video

    finalList.append(background) # the first video is used as the background

    if hasattr(submission, 'post_hint'):
        if submission.post_hint == 'hosted:video': # if post is a video, will play video in background
            userVidTemp = VideoFileClip("downloaded.mp4")
            if userVidTemp.duration >= cum:
                if hasAudio("downloaded.mp4") == True:
                    userVid = userVidTemp.subclip(0, cum).volumex(0.3)
                else:
                    userVid = userVidTemp.subclip(0, cum)
            elif userVidTemp.duration < cum: # loops the audio and video seperately, then combines
                if hasAudio("downloaded.mp4") == True:
                    audio = AudioFileClip("downloaded.mp4")
                    audio = afx.audio_loop(audio, duration=cum)
                    clip1 = VideoFileClip("downloaded.mp4")
                    clip1 = vfx.loop(clip1, duration=cum)
                    userVidTemp = clip1.set_audio(audio)
                    userVid = userVidTemp.volumex(0.3)
                else:
                    userVid = vfx.loop(userVidTemp, duration=cum)
            userVid = userVid.resize(width=600)
            (w, h) = userVid.size
            userVid = userVid.set_position(("center", 1280 - h - 20))
            finalList.append(userVid)

        elif submission.post_hint == 'image': # if post is an image, will show image in background
            userImTemp = ImageClip("downloaded.jpeg")
            userImTemp = userImTemp.resize(width=600)
            (w, h) = userImTemp.size
            userIm = userImTemp.set_duration(cum).set_position(("center", 1280 - h - 20))
            finalList.append(userIm)

    elif re.match("https://www.youtube.com/\S+", submission.url): # if the post is a youtube link, will play video
        userVidTemp = VideoFileClip("downloaded.mp4")
        if userVidTemp.duration >= cum:
            if hasAudio("downloaded.mp4") == True:
                userVid = userVidTemp.subclip(0, cum).volumex(0.3)
            else:
                userVid = userVidTemp.subclip(0, cum)
        elif userVidTemp.duration < cum:
            if hasAudio("downloaded.mp4") == True:
                audio = AudioFileClip("downloaded.mp4")
                audio = afx.audio_loop(audio, duration=cum)
                clip1 = VideoFileClip("downloaded.mp4")
                clip1 = vfx.loop(clip1, duration=cum)
                userVidTemp = clip1.set_audio(audio)
                userVid = userVidTemp.volumex(0.3)
            else:
                userVid = vfx.loop(userVidTemp, duration=cum)
        userVid = userVid.resize(width=600)
        (w, h) = userVid.size
        userVid = userVid.set_position(("center", 1280 - h - 20))
        finalList.append(userVid) 

    elif str(submission.subreddit) == "anime": # if post is from r/anime or op, show a .gif (for fun)
        extenCheck = "filler/" + random.choice(os.listdir("filler/"))
        if extenCheck.endswith(".gif"):
            fillerTemp = VideoFileClip(extenCheck).loop().set_duration(cum).resize(width=400).set_position(("center", 0.65), relative=True).set_opacity(0.75)
            finalList.append(fillerTemp)

    first = compositeList60.pop(0) # the title image will be in a better location
    first = first.set_position(("center",240)).set_opacity(0.85)
    finalList.append(first)

    for clip in compositeList60: # for each clip, adjust and time it so the next clip plays straight after, currently video clip objects
        clip = clip.set_position(("center",240)).set_opacity(0.85)
        if (clip.h > 800) & (clip.h < 1280):
            clip = clip.set_position(("center", "center"), relative=True)
        elif clip.h > 1280:
            clip = clip.resize(height=1160).set_position(("center", "center"), relative=True)

        if hasattr(submission, 'post_hint'):
            if (submission.post_hint == 'hosted:video') or (submission.post_hint == 'image'):
                clip = clip.set_position(("center",120))
        elif (submission.author).name == "AutoLovepon":
            clip = clip.set_position(("center",120))
        elif re.match("https://www.youtube.com/\S+", submission.url):
            clip = clip.set_position(("center",120))
        elif str(submission.subreddit) == "anime":
            clip = clip.set_position(("center",120))

        finalList.append(clip) # each video clip object is appended to a list

    videoTemp = CompositeVideoClip(finalList) # compilies all video clip objects together to create final video

    if (videoTemp.duration > 60) & (cumBodyCheck <= 60): # extra logic which trims the video to 60s for tiktok is the selftext is short
        video = videoTemp.subclip(0, 59)
    elif (videoTemp.duration <= 60) & (cumBodyCheck <= 60):
        video = videoTemp.subclip(0, videoTemp.duration)
    elif cumBodyCheck > 60: # if the selftext is long, allow it to go over 60, but no comments will be seen
        video = videoTemp.subclip(0, videoTemp.duration)

    video.write_videofile("finalVid/" + submissionID + "_FinalVideoTT" + ".mp4")

submission = getSubmissions()
bodyCounter = getPageImage(submission)
comments = getComments(submission)
objectNames = generateMedia(comments, bodyCounter)
compositeList = movieCreator(objectNames)
finalVideoTT(compositeList, submission, bodyCounter)