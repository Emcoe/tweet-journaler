import wget
import sys
import re
import os
import html


def addressMobilizer(inputAddress):
    cleanaddress = inputAddress
    if cleanaddress.find("mobile.twitter.com") > -1:
        return cleanaddress
    else:
        loc = cleanaddress.find("twitter.com")
        cleanaddress = "https://mobile." + cleanaddress[loc:]
    return cleanaddress

def addressRegexCleaner(address):
    match = re.search('\d\d\d\d\d+', address)
    if match:
        return match.group(0)
    else:
        return "No match"
    print('Success')

def getName(address):
    begloc = address.find("twitter.com/") + 12
    endloc = address.find("/", begloc)
    return address[begloc:endloc]

def downloader(address, filename):
    wget.download(address, out=filename)

def returnFileList(filename):
    with open(filename, "r") as ht:
        raw = ht.readlines()
        if raw[-1][-1] == '\n':
            raw[-1] = raw[-1][:-1]
    return raw

def linkGetter(dirtytext):
    cleantext = dirtytext
    linkscollected = ""
    link_range  = range(cleantext.count('<'))
    startposition = 0
    tagopen = False
    for i in link_range:
        startposition = cleantext.find('<', startposition)
        nextposition = cleantext.find('<', startposition)
        endposition = cleantext.find('>')
        if (nextposition < 0) & (nextposition < endposition):
            startposition = nextposition
        cleantext = cleantext[:startposition] + cleantext[endposition+1:]
        startposition += 1
    return cleantext

def linkGetterBreakoutLinksToo(dirtytext):
    cleantext = dirtytext
    linkscollected = ""
    link_range  = range(cleantext.count('<'))
    startposition = 0
    tagopen = False
    for i in link_range:
        startposition = cleantext.find('<', startposition)
        nextposition = cleantext.find('<', startposition)
        endposition = cleantext.find('>')
        if (nextposition < 0) & (nextposition < endposition):
            startposition = nextposition
        # linkscollected.append(cleantext[endposition+1:endposition+3])
        # if cleantext[endposition:endposition+2] == "p":
        if cleantext[endposition+1:endposition+17] == "pic.twitter.com/":
            piclinkend = cleantext.find('<', endposition + 17)
            linkscollected = linkscollected + '\n>' + cleantext[endposition + 1:piclinkend]
        cleantext = cleantext[:startposition] + cleantext[endposition+1:]
        startposition += 1
    return cleantext + linkscollected + '\n'

def tweetExtract(filename, tweetid):
    with open(filename, "r") as ht:
        raw = ht.readlines()
    counter = 0
    for i in raw:
        counter += 1
        if i.find('<div class="tweet-text" data-id="' + tweetid) > -1:
            break
    cleantweet = raw[counter][51:]
    cleantweet = html.unescape(cleantweet)
    return linkGetter(cleantweet)

def entryComposer(filename, tweetid, cleanaddress):
    return tweetExtract(filename, tweetid) + "-" + cleanaddress

def writeComposed(filename, extra, composed):
   with open(filename, "a") as ft:
       ft.write(extra + "\n" + "\n" + "---\n" + "\n" + composed)

def checkForFile(name, filename):
    if os.path.isfile(filename) == False:
        with open(filename, "a") as ft:
            ft.write(name)
    return

def writeToFile(name, composed):
    filename = name + ".txt"
    checkForFile(name, filename)
    writeComposed(filename, "", composed)

def checkForDuplicate(tweetid, filename):
    if os.path.isfile(filename) == False:
        return False
    with open(filename, "r") as ht:
        raw = ht.read()
        if raw.find(tweetid) == -1:
            return False
        else:
            return True

def main(address):
    cleanAddress = addressMobilizer(address)
    name = getName(cleanAddress)
    tweetID = addressRegexCleaner(cleanAddress)
    tweetfilename = tweetID + ".txt"
    logfilename = name + ".txt"
    if checkForDuplicate(tweetID, logfilename) == True:
        print('Tweet ' + tweetID + ' is already in log of ' + name + '.')
        return False
    else:
        wget.download(cleanAddress, out=tweetfilename)
        composition = entryComposer(tweetfilename, tweetID, cleanAddress)
        writeToFile(name, composition)
        os.remove(tweetfilename)
        print('\n' + name + ' Tweet Logged:\n')
        print(composition)
        return True


print('Tweet Logger v0.9.1')
if len(sys.argv) == 2:
    rawAddress = str(sys.argv[1])
    main(rawAddress)
else:
    print('\nNo address found at end of command')
