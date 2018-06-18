'''
##################################################################################
###############################      INFO      ###################################

# Program to get URLs of Malware Samples as a CSV - file.
# Therefore you just need to enter a website such as "malc0de.com" (-> IDEA)

# ONE POSS.:    Generic Style for ALL Malware Websites?? -> Is this even possible??
                    * Would be possible, if there were multiple fetchData()-methods.
                    * Needs to differentiate between used URLs. (Conditions!)

# OR:           Code has to be changed, when other Websites are used??
                    * Would be annoying. -> Rather write different new Methods. (see above)


© Maximilian Karl, 2018


##################################################################################
##################################    LOG    #####################################

# 10.04.2018 | Start of the implementation.

    - Layed out a first structure.

    - Imported useful modules.

    - Started to implement goToWebsite()...
        * Test with google.com was successfull.
        * _PROBLEM_ occurred while trying to access malc0de.com -> HTTP Error 403: Forbidden >>> Further Research Neccessary!!



# 11.04.2018 | Went away from malc0de. Used vxvault.net. -> WORKED!

    - Tried hard to get malc0de.com working. But kept saying: Forbidden 403.

    - Analized vxvault.net. It worked. Started to work with BeautifulSoup:
        * Style has to be "lxml"!
        * goToWebsite() works now and returns a "BeautifulSoup"-Object.
        * Added a function: extractInformation(soup) -> will be used to automate the extraction of BeautifulSoup-Content
        * Realized, that I would like to get multiple websites at once. Need new methods, that might break everything.
        --> WENT to VERSION: crawler0_2.py

    - Added a progress-bar which I wrote some time ago

    - finished extractInformation() & fetchData()
        * extractInformation only takes valuable info (drops rest)



# 13.04.2018 | Implemented Infos about the download status.

    - Added "elapsed_time", "eta" (estimated_timeOf_arrival) & "wps" (webpages_per_second)

    - Found out, that there is more info in the HTML Code -> "Jaune = Yellow", "Rouge = Red" & "[nothing] = Green"
        * Could be helpfull for "Status" (online | unknown | offline)
        * Should be a new column in the CSV!



# 14.04.2018 | Moving towards storing data in .csv-file.

    - Wanted to add a feature to the progressbar...
        * Tried to access data within HTML-Header. There was no "content-length" info there.
        * Wanted to use it because of (n) KB/s & downloaded 300KB in 00:00:01 "h:m:s". (Maybe other websites support it?) -> Moved methods in "downloadSize.py"

    - Tried hard to store the data. Not done at the moment.
        * Added method "saveToCSV()" -> Loop within Loop, to access the data -> NOT working recently.
        --> WENT to VERSION: crawler0_3.py



# 15.04.2018 | Trying to get saveToCSV() working.

    - Added new method : concatWebpages() -> Makes ONE big list out of the many websites

    - Changed functionality of the method saveToCSV()

    - Added method: updateCSV()



# 16.04.2018 | SaveToCSV() works now!

    - crawler0_3.py is now able to save 5 columns (directly from webpage)

    - New IDEA: Access the url of the ID of a malware-sample (Like so: http://vxvault.net/ViriFiche.php?ID= + 37941)
        * New methods have to be implemented + update CSV
        --> WENT to VERSION: crawler0_4.py

    - I also want to add the status_info (rouge, jaune, vert)



# 17.04.2018 | Status_info is now working! + It is now possible to update an existing CSV!

    - Removed the DATE Column from .csv-file.

    - Added a STATUS Column to .csv-file.
        * Got rid of the "live-info"
        * Progressbar now operates in only 1 line! :D

    - Want to add a new method for the start of the program, to check if there already is a .csv-file!
        * Therefore, when not already there -> download all.
        * Else     , when already there -> take last ID & fetch from there (only new ones)
        --> WENT to VERSION: crawler0_5.py

    - Added new method: startProgram() -> Starts the program and lets the user decide which website he wants to download from.
        * Only vxVault works at the moment (for obvious reasons).

    - Added new method: downloadInfoFrom() -> Checks if file exists (update!) or not (createNew!)

    - Added new method: updateCSV() -> Checks if there are any new IDs online (and if, how many!)
        * From here it should be possible, to update only new stuff.

    - updateCSV() WORKS now!
        --> You can now fully use this program for:
        * Retrieving new data
        * Checking for new updates
        * Downloading new updates (if there are some)



# 29.04.2018 | Fixed a bug that occurred, when updating a csv with more than 40 new samples.

    - The global list "webpages[]" got appended everytime, when the fetchData() method was called.
        * Only a problem during update! (And then only, when there are >40 Samples.)
        * There would be 2 times the same pages for the first 2 pages in the webpages[] list.
        * Fixed it by clearing the content of the webpages[] list after vistiting site1 for the newest ID.

    <DONE>



##################################################################################
'''

import bs4 as bs
from urllib.request import Request, urlopen
import requests
import urllib.request as req
import urllib.parse as parse
import pandas as pd
import os
import sys
import csv
import json
import math
import glob
import time
import datetime as dt



class crawler:


    # Path where the .csv's will be stored
    path = '/Users/Maxi/Desktop/atom/python/informationSecurity/seminar/tests/crawler/databases'
    vx_csv_name = 'vxVault'
    vx_test_name = "testVault"
    test_test_name = "test_test"

    # To test if goToWebsite() is working.
    test_url = "https://www.google.com"

    mal_page = 1
    url_malc0de = "http://www.malc0de.com/database/"                    # URL of malc0de.com ( page=1  is the first page)
    mal_value = {'page':str(mal_page)}
    mal_extension = "/?&page=" + str(mal_page)


    url_vxVault = "http://vxvault.net/ViriList.php"                     # URL of vxvault.net ( page=1  is the first page)

    webpages = []
    column_names = []
    url_list = []


    def __init__(self):
        #self.goToWebsite(test_url)
        print()
        self.startProgram()


    # Starts the progam.
    def startProgram(self):
        print("######### C  R  A  W  L  E  R #########\n")
        print("[-] Download malware from: ")
        print("[-] %s (=vxvault)\n" % (self.url_vxVault))
        self.website = str(input("[>] ENTER a website: "))

        if self.website == "":
            self.website = self.url_vxVault
            print("[*] Selected Website: %s (STANDARD)\n" % self.website)
            self.downloadInfoFrom(self.website, self.vx_csv_name)
        elif self.website == "vxvault":
            self.website = self.url_vxVault
            print("[*] Selected Website: %s\n" % self.website)
            self.downloadInfoFrom(self.website, self.vx_csv_name)
        else:
            print("[*] ERROR! Try again!\n")
            self.startProgram()


    # Checks out, if it has to be updated or created.
    def downloadInfoFrom(self, website, filename):
        self.filepath = self.path + '/' + filename + '.csv'

        if os.path.exists(self.filepath):
            print("[*] UPDATING CSV...")
            print("[*] CHECKING Status...\n")
            self.updateCSV(self.filepath, website)
        else:
            print("[*] STARTING DOWNLOAD...\n")
            self.webpages = self.fetchData(943, website)
            self.allInfo = self.concatWebpages(self.webpages)
            print("[*] Concated info of all webpages!")
            self.saveToCSV(self.allInfo, filename)


    # Updates the CSV, by adding only new mw-samples.
    def updateCSV(self, filepath, website):
        self.executions = 0
        self.all_data = pd.DataFrame(columns=['ID', 'URL', 'MD5', 'IP', 'STATUS'])
        self.webpages = []
        self.df = pd.read_csv(self.filepath)
        self.top = self.df.head(1)
        self.lastID = self.top.iloc[0]["ID"]                                    # Gets the ID of the last ENTRY in the CSV-File.
        self.newID = self.getFirstID(self.fetchData(1, website))
        print()
        print("[*] Newest ID in CSV: " + str(self.lastID))
        print("[*] Newest ID on site: %s" % (self.newID))
        print()

        if int(self.lastID) == int(self.newID):
            print("[*] No need for UPDATE! Already got the newest malware samples!")
            print("[*] SHUTTING DOWN...")
            print()
        else:
            self.entries = int(self.newID) - int(self.lastID)
            self.pages = math.ceil(float(self.entries / 40.0))
            print("[*] STARTING DOWNLOAD...")
            print()
            self.webpages = []
            webpages = []
            self.webpages = self.fetchData(self.pages, website)
            self.allInfo = self.concatWebpages(self.webpages)
            self.new_data = self.collectNewData(self.allInfo, self.entries)

            self.new_df = pd.DataFrame(self.new_data, columns=['ID', 'URL', 'MD5', 'IP', 'STATUS'])       # As init
            for f in glob.glob(filepath):
                self.dataframe = pd.read_csv(f)
                self.all_data = self.all_data.append(self.new_df)
                self.all_data = self.all_data.append(self.dataframe)
            self.all_data.to_csv(filepath, index=False)
            print("[*] Updated CSV-File @ ~%s\n" % filepath)


    # Returns only new entries as a list.   ----> ERROR in here! (when updating multiple webpages!) (WRONG!! -> was in updateCSV (fetchdata saves webpages globally!!! DANGER! (SET IT TO [] -> Resolved error!))
    def collectNewData(self, info, number):
        print("[*] FILTERING Data...")
        self.stop_point = number * 5
        self.wanted_data = []
        self.virus_info = []
        self.counter = 0

        for i in range(self.stop_point):
            if ((i % 5) == 0):
                print()
                print("####     VIRUS[%i]:     ####" % (self.counter+1))
                self.virus_info.append(self.trimVirusInfo(info[i]))
            elif ((i % 5) == 1):
                self.virus_info.append(self.trimVirusInfo(info[i]))
            elif ((i % 5) == 2):
                self.virus_info.append(self.trimVirusInfo(info[i]))
            elif ((i % 5) == 3):
                self.virus_info.append(self.trimVirusInfo(info[i]))
            else:
                self.virus_info.append(self.trimVirusInfo(info[i]))
                self.counter += 1
                self.wanted_data.append(self.virus_info)
                self.virus_info = []

        print("\n[*] Downloaded %i new malware-samples..." % self.counter)
        return self.wanted_data


    # Returns the ID of the newest SAMPLE on vxVault.net.
    def getFirstID(self, pageInfo):
        return self.trimVirusInfoSilent(str(pageInfo[0][0]))


    # Fetches data from vxVault | returns a webpages array -> Maybe customizable in future?
    def fetchData(self, total_pages, website):
        self.start_time = time.time()
        self.content_size = 0                                           # In Bytes -> Has to be transformed!
        self.vault_page = 0                                             # 40, 80, 120, 160 ..... Iterate by adding 40 to previous page

        # Walks through the first 900 webpages -> 900 * 40 = 36000
        while self.vault_page < total_pages:
            self.content_size += 30
            self.vault_extension = "?s=" + str(self.vault_page * 40) + "&m=40"
            self.soup = self.goToWebsite(website, self.vault_extension)
            self.webpages.append(self.extractInformation(self.soup))
            self.vault_page += 1
            self.elapsed_time = self.getTime(self.start_time)
            self.progress(self.vault_page, total_pages, " | (" + str(int(self.vault_page)) + ") Webpages", self.elapsed_time, self.content_size * 1024)

        return self.webpages


    # Accesses the website and returns a BeautifulSoup - Object
    def goToWebsite(self, website, page):
        self.source = req.urlopen(website + page).read()
        self.soup = bs.BeautifulSoup(self.source, 'lxml')
        return self.soup


    # Displays the current progress of something
    def progress(self, count, total, status, elapsed_time, content_size):
        sys.stdout.flush()
        self.fill = '█'
        self.bar_len = 60
        self.filled_len = int(round(self.bar_len * count / float(total)))

        self.wps = float(count / elapsed_time)
        self.vps = self.wps * 40.0
        self.size = self.checkSizeFormat(content_size)
        self.unit = self.getUnit(content_size)
        self.speed = self.checkSizeFormat(float(content_size / elapsed_time))
        self.speed_unit = self.getUnit(float(content_size / elapsed_time)) + "/s"

        self.eta = float((total - count) / self.wps)

        self.hours = 0
        self.mins = 0
        self.secs = 0

        if elapsed_time < 60:
            self.hours = 0
            self.mins = 0
            self.secs = int(elapsed_time)
        elif (elapsed_time >= 60) & (elapsed_time < 3600):
            self.hours = 0
            self.mins = int(elapsed_time / 60)
            self.secs = int(elapsed_time % 60)
        elif elapsed_time >= 3600:
            self.hours = int(elapsed_time / 3600)
            self.mins = int(elapsed_time % 3600)
            self.secs = int(mins % 60)

        self.hours = self.checkTimeFormat(self.hours)
        self.mins = self.checkTimeFormat(self.mins)
        self.secs = self.checkTimeFormat(self.secs)

        self.percents = round(100.0 * count / float(total), 1)
        self.bar = str(self.fill * self.filled_len + ' ' * (self.bar_len - self.filled_len))

        output1 = "\r[*] [%s]  " % (self.bar)
        output2 = '\b%s%% %s in %s:%s:%s | ETA: %.1f sec | Samples/s: %.2f | Downloaded %.2f%s @ %d%s...' % (self.percents, status, self.hours, self.mins, self.secs, self.eta, self.vps, self.size, self.unit, self.speed, self.speed_unit)

        sys.stdout.write(output1 + output2)
        sys.stdout.flush()
        if self.filled_len == self.bar_len:
            print("\n\n[*] DOWNLOAD successfull...")


    # Formats the size of a file
    def checkSizeFormat(self, size):
        if size < 1024:
            return float(size)                             # BYTES
        elif (size >= 1024) & (size < 1048576):
            return float(size / 1024.0)                      # KILO-BYTES
        elif (size >= 1048576) & (size < 1073741824):
            return float(size / 1048576.0)                   # MEGA-BYTES
        else:
            return float(size / 1073741824.0)


    # Returns the unit of a certain size
    def getUnit(self, size):
        if size < 1024:
            return "B"                              # BYTES
        elif (size >= 1024) & (size < 1048576):
            return "KB"                             # KILO-BYTES
        elif (size >= 1048576) & (size < 1073741824):
            return "MB"                             # MEGA-BYTES
        else:
            return "GB"


    # Does further work with the soup-content
    def extractInformation(self, soup):
        self.nextIsURL = False
        self.count = 0
        self.info_arr = []
        self.green_count = 0
        self.yellow_count = 0
        self.red_count = 0
        self.id_count = 0

        # Goes through every line of the webpage and searches for a specific tag (Example: <a>)
        for self.line in self.soup.find_all('a'):
            self.info = [" ", " "]
            self.status_info = [" ", " "]
            # Splits the line into 2 parts. We need the second part (after ...?).
            self.info = self.line.get('href').split('?')                                  # line.get('href').encode('utf-8') does not work correctly -> 'b before every URL

            if 'pedump.me' in self.info[-1]:
                # Do nothing -> Drop it
                self.count -= 1
                self.count += 1
            elif 'q=' in self.info[-1]:
                # Do nothing -> Drop it
                self.count -= 1
                self.count += 1
            elif 'files/' in self.info[-1]:
                # Do nothing -> Drop it
                self.count -= 1
                self.count += 1
            elif 'ID' in self.info[-1]:                                                   # Holt sich momentan leider auch noch das Datum (wegen ID)
                self.id_count += 1
                if self.id_count == 1:
                    #print(self.info[-1])
                    self.info_arr.append(self.info[-1])
                elif self.id_count == 2:
                    #print('>>## ID already collected!')
                    self.id_count = 0

                if len(self.line.text) == 5:
                    # Usually DATE was situated here
                    self.count -= 1
                    self.count += 1
                else:
                    #print("URL=" + self.line.text)
                    self.info_arr.append("URL=" + self.line.text)
                    self.count += 1
                    self.count -= 1
            else:
                if 'siri-urz' in self.info[-1]:
                    self.count -= 1
                    self.count += 1
                elif 's=' in self.info[-1]:
                    self.count -= 1
                    self.count += 1
                elif 'order=' in self.info[-1]:
                    self.count -= 1
                    self.count += 1
                elif '.php' in self.info[-1]:
                    self.count -= 1
                    self.count += 1
                elif 'IP' in self.info[-1]:
                    self.count += 1
                    self.count -= 1
                    self.info_arr.append(self.info[-1])
                    if (self.red_count < 1) & (self.yellow_count < 1):
                        self.info_arr.append("STATUS=online")
                else:
                    self.count += 1
                    self.info_arr.append(self.info[-1])                                           # self.info[1] does not work (out of bounds) Known issue. (But Why?)
            # FOR determining wether the sample is online or offline (if nothing of these is true -> online (see above!))
            if 'class="jaune"' in str(self.line):
                self.yellow_count += 1
                if self.yellow_count == 5:
                    self.info_arr.append("STATUS=unknown")
                    self.yellow_count = 0
            elif 'class="rouge"' in str(self.line):
                self.red_count += 1
                if self.red_count == 5:
                    self.info_arr.append("STATUS=offline")
                    self.red_count = 0

        return self.info_arr


    # Calculates the amount of the passed time (For loading bar)
    def getTime(self, start):
        self.time_passed = time.time() - start
        return self.time_passed


    # Checks the time format and automatically changes it accordingly
    def checkTimeFormat(self, time):
        if time < 10:
            time = "0" + str(time)
        else:
            time = str(time)
        return time


    # Takes different webpages and concats them to one list. -> RESULT into saveToCSV()
    def concatWebpages(self, webpages):
        self.all_info = []
        for self.index in range(len(webpages)):
            self.all_info += webpages[self.index]

        return self.all_info


    # First time saving (CREATE) ----> WORKS!
    def saveToCSV(self, virus_info, name):
        print("\n\n")
        self.count = 0
        self.info_arr = []
        self.virus_db = []
        self.info = ""
        self.virus_count = 0

        for self.index in range(len(virus_info)):
            self.info = virus_info[self.index]
            self.count += 1

            if self.count == 1:
                self.virus_count += 1
                print("####     VIRUS[%i]:     ####" % ((self.virus_count)))
                self.info_arr.append(self.trimVirusInfo(self.info))
            elif self.count == 2:
                self.info_arr.append(self.trimVirusInfo(self.info))
            elif self.count == 3:
                self.info_arr.append(self.trimVirusInfo(self.info))
            elif self.count == 4:
                self.info_arr.append(self.trimVirusInfo(self.info))
            else:
                self.info_arr.append(self.trimVirusInfo(self.info))
                self.virus_db.append(self.info_arr)
                print()
                self.count = 0
                self.info_arr = []

        self.df = pd.DataFrame(self.virus_db, columns=['ID', 'URL', 'MD5', 'IP', 'STATUS'])       # As init

        print()
        self.location = self.path + name + '.csv'

        try:
            self.df.to_csv(self.location, index=False)
            print("[*] Saved INFO as .csv @ ~" + self.location)
        except Exception:
            print("ERROR SAVING FILE!")


    # Cuts off everything on the left side of the INFO (ID= , MD%=, ...)
    def trimVirusInfo(self, info):
        self.array = info.split('=')
        print(self.array[0] + " = " + self.array[1])
        return self.array[1]


    # Cuts off everything on the left side of the INFO (ID= , MD%=, ...) | Silent, because it displays no print().
    def trimVirusInfoSilent(self, info):
        self.array = info.split('=')
        return self.array[1]


crawler()
