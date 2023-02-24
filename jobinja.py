# Scraping the jobinja.ir

# %%
import requests
from bs4 import BeautifulSoup
import json
import time
from unidecode import unidecode
import re
import datetime
import jdatetime
from hijri_converter import Gregorian
import cookies
import os
import random

# %%
class jobinjaCrawler():
    def __init__(self) -> None:
        self.baseUrl = f"https://jobinja.ir/"
        self.jobsUrl = self.baseUrl + "jobs/latest-job-post-%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85%DB%8C-%D8%AC%D8%AF%DB%8C%D8%AF?&sort_by=published_at_desc"
        tryingToConnect = 10 # number of trying for connect to jobinja.ir
        for i in range(tryingToConnect):
            try:
                ### doesn't work ###
                # self.response = requests.get(self.jobsUrl)
                # self.response.raise_for_status()

                ### use this section instead of previous block ###
                ### accourding to this link 'https://stackoverflow.com/questions/69141055/python-requests-does-not-get-website-that-opens-on-browser'
                ### i'm using this site 'https://sqqihao.github.io/trillworks.html' to set headers & params
                # getting new cookies by creating a browser session with selenium
                self.cookieObject = cookies.getCookies()
                self.headers = {
                    'authority': 'jobinja.ir',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-language': 'en-US,en;q=0.9',
                    'cache-control': 'max-age=0',
                    'cookie': str(open("./cookie.txt", "r", encoding="utf-8").readline()),
                    'if-none-match': 'W/"bcfde84dd07f0d9c98299f12924e62bb"',
                    'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78',
                }
                params = (
                    ('sort_by', 'published_at_desc'),
                    ('page', '1'),
                )
                # initial request to website
                response = requests.get(self.jobsUrl, headers=self.headers, params=params)
                response.raise_for_status()
                # create beautifulsoup object for first jobs page
                self.soup = BeautifulSoup(response.text, "html.parser")
                break

            except:
                if i == tryingToConnect - 1:
                    raise ConnectionError(f"Can't connect to '{self.jobsUrl}'")
                else:
                    print(f"Can't connect to '{self.jobsUrl}'\nRetry to connect. please Wait...\n")

        self.__getNumberOfPages()


    def __getNumberOfPages(self):
        self.numberOfPages = int(unidecode(self.soup.find("div", {"class": "paginator"}).findAll("li")[-2].text))


    def __jsonFileIsEmpty(self, path: str) -> bool:
        try:
            if os.path.getsize(path) == 0:
                return True
            else:
                return False
        except:
            return True


    def findjobs(self):
        self.allResults = {}
        tempResults = {}
        requestCounter = 0
        # check crawled file is empty or not and load it if not empty
        if not self.__jsonFileIsEmpty("jobinja.json"):
            with open("jobinja.json", "r", encoding="utf-8") as f:
                self.allResults = json.load(f)
                f.close()
            
        for page in range(1, self.numberOfPages + 1):
            # set new params
            params = (
                ('sort_by', 'published_at_desc'),
                ('page', str(page)),
            )

            requestCounter += 1
            if requestCounter % 5 == 0:
                del self.headers
                del self.cookieObject
                self.cookieObject = cookies.getCookies()
                self.headers = {
                    'authority': 'jobinja.ir',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-language': 'en-US,en;q=0.9',
                    'cache-control': 'max-age=0',
                    'cookie': str(open("./cookie.txt", "r", encoding="utf-8").readline()),
                    'if-none-match': 'W/"bcfde84dd07f0d9c98299f12924e62bb"',
                    'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78',
                }

            try:
                # request to website for every page
                response = requests.get(self.jobsUrl + f"&page={page}", headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                # create beautifulsoup object for first jobs page
                soup = BeautifulSoup(response.text, "html.parser")

            except requests.exceptions.Timeout:
                while True:
                    try:
                        response = requests.get(self.jobsUrl + f"&page={page}", headers=self.headers, params=params, timeout=10)
                        response.raise_for_status()
                        # create beautifulsoup object for first jobs page
                        soup = BeautifulSoup(response.text, "html.parser")
                        break
                    except:
                        print(f"Page [{self.jobsUrl + f'&page={page}'}] --> Status code: {response.status_code}\n")
            
            except Exception:
                print(f"Page [{self.jobsUrl + f'&page={page}'}] --> Status code: {response.status_code}\n")
                break
            
            # list all of the jobs on the page
            jobs = soup.find("ul", {"class": "c-jobListView__list"}).findAll("li", {"class": "c-jobListView__item"})
            
            # get information of each job
            for job in jobs:
                checkPremiumJobAdvertising = True if "c-jobListView__item--premium" in job["class"] else False

                titleTag = job.select("h2")[0].findNext("a")
                jobLink = "/".join(titleTag["href"].split("/")[0:7])
                companyLinkInJobinja = "/".join(titleTag["href"].split("/")[0:5])
                title = titleTag.text.strip()

                # check job Ad already exists or not
                try:
                    flag = False
                    if self.allResults.get(companyLinkInJobinja.split("/")[4]) != None:
                        for tempJob in self.allResults[companyLinkInJobinja.split("/")[4]]["JobsList"]:
                            if tempJob["JobLink"] == jobLink:
                                # job Ad already exists
                                flag = True
                                break
                        if flag:
                            continue
                except:
                    pass


                info = job.find("ul", {"class": "o-listView__itemComplementInfo"}).findAll("li")

                nameOfCompany = info[0].find("span").text.split("|")
                persianNameOfCompany = (nameOfCompany[0]).strip()
                englishNameOfCompany = (nameOfCompany[1]).strip()

                location = info[1].find("span").text.strip().split("،")
                province = location[0]
                city = location[1]

                jobType = [" ".join(info[2].find("span").findNext("span").text.strip().replace("\n", " ").replace("\u200c", " ").split()[1:3])]

                # find published date of the job Ad
                date = None
                if (dateTag := job.find("div", {"class": "o-listView__itemInfo"}).find("h2", {"class": "c-jobListView__title"}).find("span", {"class": "c-jobListView__passedDays"})) != None:
                    if "امروز" in dateTag.text.strip():
                        date = datetime.date.today() - datetime.timedelta(days=0)
                    else:
                        if "روز" in dateTag.text.strip():
                            if (findNumber := re.search(r"\d+", unidecode(dateTag.text.strip()))) != None:
                                date = datetime.date.today() - datetime.timedelta(days=int(findNumber.group()))

                publishDate = {}
                if date != None:
                    publishDate["gregorian"] = date.__str__()
                    publishDate["jalali"] = jdatetime.date.fromgregorian(date=date).__str__()
                    publishDate["hijri"] = Gregorian(date.year, date.month, date.day).to_hijri().__str__()
                else:
                    publishDate["gregorian"] = None
                    publishDate["jalali"] = None
                    publishDate["hijri"] = None
                

                try:
                    # request to every job page
                    response = requests.get(jobLink, headers=self.headers, params=params)
                    response.raise_for_status()
                    # create beautifulsoup object
                    soup = BeautifulSoup(response.text, "html.parser")
                
                except requests.exceptions.Timeout:
                    while True:
                        try:
                            response = requests.get(jobLink, headers=self.headers, params=params, timeout=10)
                            response.raise_for_status()
                            # create beautifulsoup object for first jobs page
                            soup = BeautifulSoup(response.text, "html.parser")
                            break
                        except:
                            print(f"Page [{self.jobsUrl + f'&page={page}'}] --> Status code: {response.status_code}\n")
                
                except Exception:
                    print(f"Page [{self.jobsUrl + f'&page={page}'}] --> Status code: {response.status_code}\n")
                    break


                jobGroup = []
                workExperienceText = None
                salary = None
                skills = []
                gender = None
                militaryState = "Not_Important"
                encouraged = None
                companyType = None
                companyWebsite = None
                companySize = None
                foundedYearOfComapny = None
                categoryTypeLink = None

                companyInformation = soup.find("div", {"class": "body"})
                companyHeader = companyInformation.find("div", {"class": "c-companyHeader"})
                metaItems = companyHeader.select(".c-companyHeader__info div")[0].findAll("span")

                # check company is premium in jobinja or not
                premiumCompany = True if "c-companyHeader--premium" in companyHeader["class"] else False
    
                for item in metaItems:
                    # find type of company and company website
                    if (Atag := item.find("a")) != None:
                        if re.match(r"(http|https)://(www\.)?\w+\.\w{1,63}", str(Atag["href"]).strip()):
                            if re.match(r"(http|https)://(www\.)?jobinja\.\w{1,63}", str(Atag["href"]).strip()):
                                companyType = str(Atag.text).strip()
                                categoryTypeLink = str(Atag["href"]).strip()
                            else:
                                companyWebsite = str(Atag["href"]).strip()

                        else:
                            companyType = None
                            companyWebsite = None

                    # find size of company
                    elif (text := str(item.text).strip()).find("نفر") != -1:
                        if (findNumber := re.findall(r"\d+", unidecode(text))) != None:
                            if len(findNumber) == 2:
                                findNumber = [int(unidecode(str(number).strip())) for number in findNumber]
                                companySize = f"{min(findNumber)}-{max(findNumber)}"
                            elif len(findNumber) == 1:
                                findNumber = int(unidecode(str(findNumber[0]).strip()))
                                if "بیش" in text:
                                    companySize = f"cs>{findNumber}"
                                elif "کم" in text:
                                    companySize = f"cs<{findNumber}"
                                else:
                                    companySize = None
                    
                    # find established year of company
                    elif (text := str(item.text).strip()).find("تاسیس") != -1:
                        if (findNumber := re.search(r"\d+", unidecode(text))) != None:
                            foundedYearOfComapny = int(findNumber.group())


                jobDetails = soup.findAll("ul", {"class": "c-infoBox"})
                # jobDetails have 2 section:
                # first section in above of page & second section is in end of page
                # first section
                for detail in jobDetails[0]:
                    # find job group
                    if "دسته‌بندی شغلی" in detail.text:
                        jobTypeTags = detail.find("div").findAll("span")
                        for type in jobTypeTags:
                            jobGroup.append(type.text)

                    # find type of job
                    elif "نوع همکاری" in detail.text:
                        typesOfWorkTag = detail.find("div").findAll("span")
                        for type in typesOfWorkTag:
                            if str(type.text).strip() in ["دورکاری", "کارآموزی", "تمام‌ وقت", "پاره‌ وقت"] and str(type.text).strip() not in jobType:
                                jobType.append(type.text)

                    # find work experience
                    elif "حداقل سابقه کار" in detail.text:
                        workExperienceText = detail.find("div").find("span").text
                        if "مهم نیست" in workExperienceText:
                            workExperience = f"No_Need"
                        elif "کمتر از سه سال" in workExperienceText:
                            workExperience = f"we<3"
                        elif "سه تا شش سال" in workExperienceText:
                            workExperience = f"6>we>3"
                        elif "بیش از شش سال" in workExperienceText:
                            workExperience = f"we>6"
                        else:
                            workExperience = None

                    elif "حقوق" in detail.text:
                        salaryText = detail.find("div").find("span").text
                        if (s := re.search(r"\d+", unidecode(salaryText).replace(",", ""))) != None:
                            salary = int(s.group())
                        if "توافقی" in salaryText:
                            salary = "Adaptive"

                # second section
                for detail in jobDetails[1]:
                    # finding skills that needed for the job
                    if "مهارت‌های مورد نیاز" in detail.text:
                        skillTags = detail.find("div").findAll("span")
                        for skill in skillTags:
                            skills.append(skill.text)

                    # find gender
                    elif "جنسیت" in detail.text:
                        if g := "نیست" in detail.find("div").find("span").text:
                            gender = "Not_Important"
                        elif g := "مرد" in detail.find("div").find("span").text:
                            gender = "Male"
                        elif g := "زن" in detail.find("div").find("span").text:
                            gender = "Female"
                        else:
                            gender = None

                    # find military state
                    elif "وضعیت نظام وظیفه" in detail.text:
                        if "نیست" in detail.find("div").find("span").text:
                            militaryState = "Not_Important"
                        else:
                            militaryState = "Important"

                    elif "حداقل مدرک تحصیلی" in detail.text:
                        if "نیست" in detail.find("div").find("span").text:
                            encouraged = "Not_Important"
                        else:
                            encouraged = detail.find("div").find("span").text

                # this link is a short link for access to the advertise job
                uniqueURL = None
                if (temp := soup.find("a", {"class": re.compile(r"c-.+uniqueURL")})) != None:
                    uniqueURL = temp["href"]

                # link of company logo
                companyImg = None
                if (temp := soup.find("a", {"class": "c-companyHeader__logoLink"})) != None:
                    companyImg = temp.find("img")["src"]

                tempResults = {}
                
                # checking if the company exist in result or not
                # not exist -> first create information for company then append the job
                if self.allResults.get(companyLinkInJobinja.split("/")[4]) == None:
                    self.allResults[companyLinkInJobinja.split("/")[4]] = {}
                    self.allResults[companyLinkInJobinja.split("/")[4]]["NameOfCompany"] = {"Persian": persianNameOfCompany, "English": englishNameOfCompany}
                    self.allResults[companyLinkInJobinja.split("/")[4]]["Location"] = {"Province": province, "City": city}
                    self.allResults[companyLinkInJobinja.split("/")[4]]["CompanyLinkInJobinja"] = companyLinkInJobinja
                    self.allResults[companyLinkInJobinja.split("/")[4]]["CompanyType"] = companyType
                    self.allResults[companyLinkInJobinja.split("/")[4]]["CompanyWebsite"] = companyWebsite
                    self.allResults[companyLinkInJobinja.split("/")[4]]["CompanySize"] = companySize
                    self.allResults[companyLinkInJobinja.split("/")[4]]["FoundedYearOfComapny"] = foundedYearOfComapny
                    self.allResults[companyLinkInJobinja.split("/")[4]]["PremiumCompanyInJobinja"] = premiumCompany
                    self.allResults[companyLinkInJobinja.split("/")[4]]["CompanyImage"] = companyImg
                    self.allResults[companyLinkInJobinja.split("/")[4]]["CategoryTypeLink"] = categoryTypeLink
                    self.allResults[companyLinkInJobinja.split("/")[4]]["JobsList"] = []
                    tempResults["Title"] = title
                    tempResults["Premium"] = checkPremiumJobAdvertising
                    tempResults["JobLink"] = jobLink
                    tempResults["JobType"] = jobType
                    tempResults["WorkExperience"] = workExperience
                    tempResults["Salary"] = salary
                    tempResults["Skills"] = skills
                    tempResults["Gender"] = gender
                    tempResults["MilitaryState"] = militaryState
                    tempResults["Encouraged"] = encouraged
                    tempResults["JobLinkShort"] = uniqueURL
                    tempResults["JobGroup"] = jobGroup
                    tempResults["PublishDate"] = publishDate
                    self.allResults[companyLinkInJobinja.split("/")[4]]["JobsList"].append(tempResults)

                # exist -> only append new job
                else:
                    tempResults["Title"] = title
                    tempResults["Premium"] = checkPremiumJobAdvertising
                    tempResults["JobLink"] = jobLink
                    tempResults["JobType"] = jobType
                    tempResults["WorkExperience"] = workExperience
                    tempResults["Salary"] = salary
                    tempResults["Skills"] = skills
                    tempResults["Gender"] = gender
                    tempResults["MilitaryState"] = militaryState
                    tempResults["Encouraged"] = encouraged
                    tempResults["JobLinkShort"] = uniqueURL
                    tempResults["JobGroup"] = jobGroup
                    tempResults["PublishDate"] = publishDate
                    self.allResults[companyLinkInJobinja.split("/")[4]]["JobsList"].append(tempResults)

                self.exportToJson()
                time.sleep(random.random())
            # temp line, it will delete in the future
            # break
            time.sleep(1)

    def exportToJson(self):
        try:
            with open("jobinja.json", "w", encoding="utf-8") as file:
                json.dump(self.allResults, file, ensure_ascii=False, indent=4)
                file.close()
        except:
            raise ValueError("Can Not Save !")

# %%
temp = jobinjaCrawler()
temp.findjobs()

# %%
temp.exportToJson()