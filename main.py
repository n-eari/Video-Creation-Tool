import praw
import json
import re
import os
import random
import emoji 
import textwrap
from pytube import YouTube
from selenium import webdriver
from selenium.webdriver.common.by import By
from moviepy.editor import *
from moviepy.video.fx.all import crop
from RedDownloader import RedDownloader
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from subprocess import check_output
from mutagen.mp3 import MP3
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'

# Video Creation Tool (21/09/22)
# Written by Navraj Eari

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
            f.write("https://www.reddit.com" + str(submission.permalink) + "\n")
            f.write("post by u/" + str((submission.author).name) + "\n")
            f.write("#reddit #askreddit #fyp #foryoupage #redditreadings #redditstories #aita #tifu" + "\n")
            f.write("#reddit, #askreddit, #fyp, #foryoupage, #redditreadings, #redditstories, #aita, #tifu" + "\n")
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
            f.write("https://www.reddit.com" + str(submission.permalink) + "\n")
            f.write("post by u/" + str((submission.author).name) + "\n")
            f.write("#reddit #askreddit #fyp #foryoupage #redditreadings #redditstories #aita #tifu" + "\n")
            f.write("#reddit, #askreddit, #fyp, #foryoupage, #redditreadings, #redditstories, #aita, #tifu" + "\n")
            f.close()
        
    finally:
        return submission # returns a submission object of our post

def textCleaner(text): # cleans the selftext for special chars, acryonyms, and profanity
    text = text.replace('\n', '. ').replace('\r', '').replace('"', '').replace("\\", "").replace("/", "").replace("*", "")
    text = re.sub("http\S+", "", text)
    text = re.sub(emoji.get_emoji_regexp(), "", text)

    profan1 = {"TIFU":"Today I efed up", "AITA":"Am I the a-hole", "BIL":"brother-in-law", "SIL":"sister-in-law",
               "MIL": "mother-in-law"}
    profan2 = {"tf":"the hell", "ass":"butt", "cum":"liquids", "rapist":"criminal"}
    profan3 = {"fuck":"f", "bitch":"dog", "cunt":"cow", "asshole":"a-hole", "rape":"defile", "dick":"schlong",
               "wtf":"what the hell", "porn":"pork", "masturbate":"got off", "slut":"sloth",
               "suicide":"death", "bastard":"dog", "pussy":"wussy", "sex":"bonk", "horny":"bonky", "foreplay":"touching",
               "shit":"dam", "fingering":"touching", "raping":"defiling", "spank":"clap", "masturbating":"jerking",
               "wank":"jerk", "idk":"i dont know", "eli5": ""}

    for word, replacement in profan1.items():
        text = re.sub(word, replacement, text)
    for word, replacement in profan2.items():
        text = re.sub("\W" + word + "\W", replacement, text, flags=re.IGNORECASE)
    for word, replacement in profan3.items():
        text = re.sub(word, replacement, text, flags=re.IGNORECASE)

    return text

def add_corners(im, rad): # adds rounded corners to images. rad = 30 is good
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

def imageOpt(img): # optimises the image. increases width to 600 and sharpens
    basewidth = 600
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def imFilter(im): # censors profanity words in the image itself
    profan1 = ["fuck", "bitch", "cunt", "rape", "dick", "porn", "masturbate", "slut", "suicide",
               "bastard", "pussy", "sex", "horny", "foreplay", "shit", "fingering", "raping", "spank",
               "masturbat", "wank"]
    profan2 = ["ass", "asshole", "cum", "cumming", "rapist"]
    data = pytesseract.image_to_data(im, output_type='dict')
    boxes = len(data['level'])
    for i in range(boxes):
        for word in profan1:
            if word in re.sub('\W', '', data['text'][i], flags=re.IGNORECASE).lower():
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                draw = ImageDraw.Draw(im)
                draw.line((x, y + (h/2), x + w, y + (h/2)), fill = "black", width = round(h/3))
        for word in profan2:
            if re.sub('\W', '', data['text'][i], flags=re.IGNORECASE).lower() == word:
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                draw = ImageDraw.Draw(im)
                draw.line((x, y + (h/2), x + w, y + (h/2)), fill = "black", width = round(h/3))
    return im

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result # function to add margins to images

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

def audioLength(name): # returns the length of an audio file in seconds
    audio_info = MP3("audio\\" + str(name) + ".mp3").info    
    return int(audio_info.length)

def getPageImage(submission): # prepares our post for a screenshot
    clock = 0 # sum of audio file times
    bodyCounter = 0 # number of images
    objectNames = [str(0)] # a list with the number of images
    postType = "text" # variable which tells us what type our post is (video, image, or text)
    link = "https://www.reddit.com" + submission.permalink
    submissionID = re.search('(?<=comments/)(\w+)', link).group(1)
    driver.get(link) # loads page into webdriver for further work
    driver.find_element_by_xpath('//*[@id="SHORTCUT_FOCUSABLE_DIV"]/div[3]/div[1]/section/div/section/section/form[2]/button').click()

    def easySS(): # a few posts of diff types ss the same elements, so this function makes it simplier to do
        driver.find_element(By.CLASS_NAME, '_eYtD2XCVieq6emjKBH3m').screenshot("image\\0.png")
        driver.find_element(By.CLASS_NAME, 'cZPZhMe-UCZ8htPodMyJ5').screenshot("image\\temp1.png")
        driver.find_element(By.CLASS_NAME, '_1hwEKkB_38tIoal6fcdrt9').screenshot("image\\temp2.png")
        im1 = add_margin(Image.open("image\\0.png"), 0, 20, 0, 20, (255,255,255))
        im1 = imageOpt(im1)
        im2 = add_margin(Image.open("image\\temp1.png"), 10, 20, 10, 20, (255,255,255))
        im2 = imageOpt(im2)
        im3 = add_margin(Image.open("image\\temp2.png"), 0, 20, 10, 10, (255,255,255))
        im3 = imageOpt(im3)
        im = get_concat_v_resize(im2, im1, resize_big_image = True)
        im = get_concat_v_resize(im, im3, resize_big_image = True)
        im = imFilter(im)
        add_corners(im, rad = 30).save("image\\0.png")
        os.remove("image\\temp1.png")
        os.remove("image\\temp2.png")

    if driver.find_elements_by_class_name('gCpM4Pkvf_Xth42z4uIrQ'):
        driver.find_element_by_class_name('gCpM4Pkvf_Xth42z4uIrQ').click()
        # if the page has a SPOILER button, it will press it so the post can be seen
    if driver.find_elements_by_xpath('//*[@id="AppRouter-main-content"]/div/div[1]/div/div/div[2]/button'):
        driver.find_element_by_xpath('//*[@id="AppRouter-main-content"]/div/div[1]/div/div/div[2]/button').click()
        driver.find_element_by_class_name('gCpM4Pkvf_Xth42z4uIrQ').click()
        # if the page is NSFW, will click buttons to allow viewing
        
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    driver.set_window_size(390, S('Height')) # May need manual adjustment                                                                                                         
    # logic to just page size

    if hasattr(submission, 'post_hint'):
        if submission.post_hint == 'hosted:video':
            postType = "video"
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)   
            clock += audioLength(bodyCounter)                                                                                           
            easySS()
            RedDownloader.Download(url = link, quality = 360, destination = "")
            # if post is a video, will only dictate and ss the title, and also downloads vid for later

        elif submission.post_hint == 'image':
            postType = "image"
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)   
            clock += audioLength(bodyCounter)                                                                                               
            easySS()
            RedDownloader.Download(url = link, quality = 360, destination = "")
            # if post is an image, will only dictate and ss the title, and also downloads image for later

        elif submission.post_hint == 'link':
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)  
            clock += audioLength(bodyCounter)                                                                                               
            driver.find_element(By.XPATH, '//*[@id="t3_{}"]/div'.format(submissionID)).screenshot("image\\0.png")
            im = add_margin(Image.open("image\\0.png"), 10, 5, 10, 5, (255,255,255))
            im = imageOpt(im)
            add_corners(im, rad = 30).save("image\\0.png")
            # if post is a link post, only dicatate title
        
    elif re.match("https://www.youtube.com/\S+", submission.url):
        postType = "video"
        command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
        os.system(command)    
        clock += audioLength(bodyCounter)                                                                                           
        easySS()
        YouTube(submission.url).streams.get_by_resolution("360p").download(filename = "downloaded.mp4")
        # if post is a youtube link, download video, and only ss and dictate title

    else: # selftext post
        if driver.find_elements_by_xpath("//div[@class='_3xX726aBn29LDbsDtzr_6E _1Ap4F5maDtT1E1YuCiaO0r D3IL3FD0RFy_mkKLPwL4']//p[@class='_1qeIAgB0cPwnLhDF9XSiJM']"):
            # saves an audio file of the title and selftext, sepearted per paragraph
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)
            clock += audioLength(bodyCounter)
            easySS()

            def easyP(para, top, bottom): # seperate function to ss paragraph elements
                para.screenshot("image\\" + str(bodyCounter) + ".png")
                im = add_margin(Image.open("image\\" + str(bodyCounter) + ".png"), top, 20, bottom, 20, (255,255,255))
                im = imageOpt(im)
                im = imFilter(im)
                add_corners(im, rad = 30).save("image\\" + str(bodyCounter) + ".png")

            paras =  driver.find_elements_by_xpath("//div[@class='_3xX726aBn29LDbsDtzr_6E _1Ap4F5maDtT1E1YuCiaO0r D3IL3FD0RFy_mkKLPwL4']//p[@class='_1qeIAgB0cPwnLhDF9XSiJM']")
            for para in paras:
                bodyCounter += 1
                command = tts.format(textCleaner(para.text), "audio/" + str(bodyCounter) + ".mp3")
                os.system(command)  
                clock += audioLength(bodyCounter)
                if paras.index(para) == 0: # if its the 1st paragraph, add slightly diff margins
                    easyP(para, 10, 5)
                elif paras.index(para) == (len(paras) - 1): # if its the last paragraph, add slightly diff margins
                    easyP(para, 0, 10)
                else: # if a normal paragraph, add slightly diff margins
                    easyP(para, 0, 5)
                objectNames.append(str(bodyCounter))

        else: # this sub doesnt have a selftext
            command = tts.format(textCleaner(submission.title), "audio/" + "0" + ".mp3")
            os.system(command)
            clock += audioLength(bodyCounter)
            easySS()

    BodyClockObType = [bodyCounter, clock, objectNames, postType]
    '''
    - bodyCounter: int variable with the number of elements it has ss. so 4 would mean we took an ss of the title
      (0) and 4 paragraphs (1, 2, 3, 4)
    - clock: int variable which shows how long it takes the tts to speak aloud those elements
    - objectNames: list which contains how many elements have been ss. looks like, where each element is a string.
      so if 4 elements have been ss (title element and 4 paragraphs), it would look like ["0", "1", "2", "3", "4"]
    - postType: str variable which tells us what type our post is, eitheir video, image, or text
    '''
    return BodyClockObType

def generateMedia(comment, bodyCounter, parent, isChild): # generates audio and image for a comment object
    commentlink = "https://www.reddit.com" + comment.permalink
    URL = commentlink
    driver.get(URL)
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    driver.set_window_size(420, S('Height')) # May need manual adjustment
    driver.find_element(By.XPATH, '//*[@id="t1_{}"]/div[2]'.format(comment.id)).screenshot("image\\"+ str(bodyCounter) + ".png")
    command = tts.format(textCleaner(comment.body), "audio/" + str(bodyCounter) + ".mp3")
    os.system(command)

    if isChild == True: # if its a child comment
        im1 = Image.open("image\\" + str(parent) + ".png")
        im1 = imageOpt(im1)
        im2 = Image.open("image\\" + str(bodyCounter) + ".png")
        im2 = add_margin(im2, 0, 0, 0, 15, (245, 246, 246))
        im2 = imageOpt(im2)
        
        im = get_concat_v_resize(im1, im2, resize_big_image = True)
        im = imFilter(im)
        add_corners(im, rad = 30).save("image\\"+ str(bodyCounter) + ".png")
        im1 = imFilter(im1)
        add_corners(im1, rad = 30).save("image\\"+ str(parent) + ".png") # for logic reasons, round of the parent here, and not above

def getComments(submission, BodyClockObType): # gets comments from submission
    chars = 600 # only comments which are <= 600 chars are used
    clock = BodyClockObType[1]

    if clock < 59: # if the selftext was short, then we get enough comments to reach 60s
        bodyCounter = BodyClockObType[0]
        long = False
        no = 0
        parent = bodyCounter
        submission.comments.replace_more() # this takes alot of time
        allComments = [comment for comment in list(submission.comments) if (comment.stickied == False) & (len(textCleaner(comment.body)) <= chars)]
        maxCom = len(allComments)

        while clock < 59:
            if no == maxCom:
                break
            bodyCounter += 1
            parent += 1
            comment = allComments[no]
            generateMedia(comment, bodyCounter, parent, isChild = False)
            clock += audioLength(bodyCounter)   
            BodyClockObType[2].append(str(bodyCounter))
            no += 1
            if clock >= 59:
                im1 = Image.open("image\\" + str(parent) + ".png")
                im1 = imageOpt(im1)
                im1 = imFilter(im1)
                add_corners(im1, rad = 30).save("image\\" + str(parent) + ".png")
                break

            allReps = [comment for comment in list(comment.replies) if len(textCleaner(comment.body)) <= chars]
            if (len(allReps) > 0) and (BodyClockObType[3] == "text"): # if the parent comment has children
                bodyCounter += 1
                comment2 = allReps[0] # for each child comment, up till [1] children...
                generateMedia(comment2, bodyCounter, parent, isChild = True)
                clock += audioLength(bodyCounter)   
                parent += 1
                BodyClockObType[2].append(str(bodyCounter))
            else:
                im1 = Image.open("image\\" + str(parent) + ".png")
                im1 = imageOpt(im1)
                im1 = imFilter(im1)
                add_corners(im1, rad = 30).save("image\\" + str(parent) + ".png")

    else: # if selftext is long, then get no comments since we wont have time for them
         long = True
         
    driver.quit()
    '''
    - long: boolean which lets us know if we are over 60s. if False, then video will be 60s. if True, then video
      will be over 60s (mainly for posts from AITA/TIFU where the selftext is long and of importance, so we dont
      get any comments)
    '''
    return long # boolean which lets us know if we are over 60s. 

def movieCreator(BodyClockObType): # for each commenet, combine .png and .mp3 into a video
    objectNames = BodyClockObType[2] # objectNames: see above. if we ss comments, for each comment, this variable increased by 1
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

    return compositeList # returns a list, where each element is a video clip object. this has the image of the
    # optimised image of the element, tts audio, and time at which clip should start and end before next one begins playing.

def finalVideoTT(compositeList, submission, BodyClockObType, long): # creates the final video for tiktok
    finalList = [] # this will contain, in order, our final clip objects which have been optimised, which will then
    # be composited together to create the final video.
    timeList = [clip.duration for clip in compositeList]
    cum = sum(timeList) # cumaltive time of all our clips. usually not 60s even if long = False.
    link = "https://www.reddit.com" + submission.permalink
    submissionID = re.search('(?<=comments/)(\w+)', link).group(1)
    postType = BodyClockObType[3]

    def hasAudio(file_path): # checks if downloaded video has audio
        command = ['ffprobe', '-show_streams', '-print_format', 'json', file_path]
        output = check_output(command)
        parsed = json.loads(output)
        streams = parsed['streams']
        audio_streams = list(filter((lambda x: x['codec_type'] == 'audio'), streams))
        return len(audio_streams) > 0

    if postType == "video":
        hasAudio = hasAudio("downloaded.mp4")
    else:
        hasAudio = False

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

    musicName = random.choice(os.listdir("music/"))
    musicTemp = AudioFileClip("music/" + musicName)
    if musicTemp.duration >= cum:
        music = musicTemp.subclip(0, cum).volumex(0.10)
    elif musicTemp.duration < cum:
        music = musicTemp.volumex(0.10)
        music = afx.audio_loop(music, duration = cum)
    if hasAudio == True: # if video has audio, no music will be played
        music = musicTemp.volumex(0)
    # loads a music clip from folder, and adjusts it for stuff

    background = back.set_audio(music)
    # loads a random music file from folder, adjusts some stuff, and appends it to the background video

    finalList.append(background) # the first video is used as the background

    if postType == "video": # if post is a video, will play video in background
        userVidTemp = VideoFileClip("downloaded.mp4")
        if userVidTemp.duration >= cum:
            if hasAudio == True:
                userVid = userVidTemp.subclip(0, cum).volumex(0.3)
            else:
                userVid = userVidTemp.subclip(0, cum)
        elif userVidTemp.duration < cum: # loops the audio and video seperately, then combines
            if hasAudio == True:
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
        userVid = userVid.set_position(("center", 120))
        finalList.append(userVid)

    elif postType == "image": # if post is an image, will show image in background
        userImTemp = ImageClip("downloaded.jpeg")
        userImTemp = userImTemp.resize(width=600)
        (w, h) = userImTemp.size
        userIm = userImTemp.set_duration(cum).set_position(("center", 120))
        finalList.append(userIm)

    elif str(submission.subreddit) == "anime": # if post is from r/anime or op, show a .gif (for fun)
        extenCheck = ".filler/" + random.choice(os.listdir(".filler/"))
        if extenCheck.endswith(".gif"):
            fillerTemp = VideoFileClip(extenCheck).loop().set_duration(cum).resize(width=400).set_position(("center", 0.65), relative=True).set_opacity(0.75)
            finalList.append(fillerTemp)

    for clip in compositeList: # for each clip, adjust and time it so the next clip plays straight after, currently video clip objects
        clip = clip.set_position(("center",240)).set_opacity(0.85)
        if (clip.h > 800) & (clip.h < 1280):
            clip = clip.set_position(("center", "center"), relative=True)
        elif clip.h > 1280:
            clip = clip.resize(height=1160).set_position(("center", "center"), relative=True)

        if (postType == "video") or (postType == "image"): # if video or image, adjust comments for it
            clip = clip.set_position(("center", 120 + h + 40)).set_opacity(0.50)
            if clip.h > (1280 - 20 - (120 + h + 40)):
                clip = clip.set_position(("center", 1280 - 20 - clip.h))
                
        finalList.append(clip) # each video clip object is appended to a list

    if hasAudio == False: # set of code to create watermark which credits persons music i am using
        image = Image.new("RGBA", (720, 60), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('calibrib.ttf', 20)
        text = musicName.replace("9", '"').replace(".mp3", "")
        leftMargin = 25 # due to tt trimming sides
        top = 80 # can change freely
        lines = textwrap.wrap(text, width=40)
        textTop = 12
        if len(lines) == 1:
            textTop = textTop * 1.75
        widthList = []
        for line in lines:
            line_width, line_height = font.getsize(line)
            widthList.append(line_width)
        widthList.sort(reverse=True)
        draw.rounded_rectangle((-60, 0, leftMargin + 40 + 25 + widthList[0], 60), fill=(255, 255, 255, 217), radius=60)  
        for line in lines:
            draw.text((leftMargin + 40 + 5, textTop), line, font=font, fill=(0, 0, 0, 217))
            textTop += line_height
        image.save("watermark.png")
        waterClip = ImageClip("watermark.png").set_start(0).set_duration(cum).set_pos(("left", top)).set_fps(1)
        finalList.append(waterClip) # appends video vlip to a list
        finalList.insert(1, waterClip)
        musicIcon = VideoFileClip("musicIcon.gif", has_mask=True).resize(height=40).loop().set_start(0).set_duration(cum).margin(left=leftMargin, opacity=0).set_pos((0, top + 10)).set_opacity(0.85)
        finalList.insert(2, musicIcon)

    videoTemp = CompositeVideoClip(finalList) # compilies all video clip objects together to create final video
    
    if (videoTemp.duration > 60) & (long == False): # extra logic which trims the video to 60s for tiktok is the selftext is short
        video = videoTemp.subclip(0, 59)
    elif (videoTemp.duration <= 60) & (long == False):
        video = videoTemp.subclip(0, videoTemp.duration)
    elif long == True: # if the selftext is long, allow it to go over 60, but no comments will be seen
        video = videoTemp.subclip(0, videoTemp.duration)

    video.write_videofile("finalVid/" + submissionID + "_FinalVideoTT" + ".mp4")

submission = getSubmissions()
BodyClockObType = getPageImage(submission)
long = getComments(submission, BodyClockObType)
compositeList = movieCreator(BodyClockObType)
finalVideoTT(compositeList, submission, BodyClockObType, long)