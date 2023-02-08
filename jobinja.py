# Scraping the jobinja.ir

# %%
import requests
from bs4 import BeautifulSoup
import json
import time
from unidecode import unidecode

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
                self.headers = {
                    'authority': 'jobinja.ir',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-language': 'en-GB,en;q=0.9',
                    'cache-control': 'max-age=0',
                    'cookie': 'logglytrackingsession=585d6f0a-27b5-45ad-a926-a94cf6b5a5e4; _gid=GA1.2.1151604004.1675846448; _gat_gtag_UA_129125700_1=1; XSRF-TOKEN=eyJpdiI6IkliRlwvY29WRWY4SmFzUEcxT1RJaHd3PT0iLCJ2YWx1ZSI6Ik5EUzlsYmFqc3J4bE1USHNlQVY1dlNhdDN1REhPQlZWUU9US2phOGQ2MWZaXC9lcEpjY1pNZzJ5b210YVBZSktWRThiVVd5ZTFUSVViQmZcL2Fhc0ZMQWc9PSIsIm1hYyI6IjNkODE2MDJkZWY4NDU4ZjBjYmZiOTQzOGNhMDVhNWEyY2Y0MjFmZjEyNGRiZDEzZjAzOGM0ZGMxZjA1NmY1NjQifQ%3D%3D; JSESSID=eyJpdiI6Ik0rekpsQkwwQ05XTkJxQ2dZTkx3Nnc9PSIsInZhbHVlIjoid1M4aStQaE4xSzNZak0wU0N4TFVZaUR0NlppWnVjVllkMlRtdG5CSVE2XC82bDg5cmh5K0ZuSEdaM1QwZjJHdVdHSjdHVzM0aGhhTG1scXlzSWVCeWl3PT0iLCJtYWMiOiJhNzMxMjA2OTE5NjU4NTA1MGYxZGEzMGI2ZWQxYWUyMzFlYWYxMGEwYTNjYmVmZDljYzcwNGNmZmE0ZGRlNzQ2In0%3D; _ga=GA1.1.467218268.1675846448; _ga_T8HC2S1534=GS1.1.1675872983.5.1.1675877899.18.0.0',
                    'if-none-match': 'W/"a15be6a478dbad9d15762e68819f26cb"',
                    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
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


    def findjobs(self):
        self.allResults = {}
        tempResults = {}
        
        for page in range(1, self.numberOfPages + 1):
            # set new params
            params = (
                ('sort_by', 'published_at_desc'),
                ('page', str(page)),
            )

            try:
                # request to website for every page
                response = requests.get(self.jobsUrl + f"&page={page}", headers=self.headers, params=params)
                response.raise_for_status()
                # create beautifulsoup object for first jobs page
                soup = BeautifulSoup(response.text, "html.parser")

            except:
                print(f"Page [{self.jobsUrl + f'&page={page}'}] --> Status code: {response.status_code}\n")
                break
            
            # list all of the jobs on the page
            jobs = soup.find("ul", {"class": "c-jobListView__list"}).findAll("li", {"class": "c-jobListView__item"})
            
            # get information of each job
            for job in jobs:
                checkPremium = True if "c-jobListView__item--premium" in job["class"] else False

                titleTag = job.select("h2")[0].findNext("a")
                jobLink = "/".join(titleTag["href"].split("/")[0:7])
                companyLink = "/".join(titleTag["href"].split("/")[0:5])
                title = titleTag.text.strip()

                info = job.find("ul", {"class": "o-listView__itemComplementInfo"}).findAll("li")

                nameOfCompany = info[0].find("span").text.split("|")
                persianNameOfCompany = (nameOfCompany[0]).strip()
                englishNameOfCompany = (nameOfCompany[1]).strip()

                location = info[1].find("span").text.strip().split("،")
                province = location[0]
                city = location[1]

                jobType = " ".join(info[2].find("span").findNext("span").text.strip().replace("\n", " ").replace("\u200c", " ").split()[1:3])
                
                # checking if the company exist in result or not
                # not exist -> first create information for company then append the job
                if self.allResults.get(companyLink.split("/")[4]) == None:
                    self.allResults[companyLink.split("/")[4]] = {}
                    self.allResults[companyLink.split("/")[4]]["NameOfCompany"] = {"Persian": persianNameOfCompany, "English": englishNameOfCompany}
                    self.allResults[companyLink.split("/")[4]]["Location"] = {"Province": province, "City": city}
                    self.allResults[companyLink.split("/")[4]]["CompanyLink"] = companyLink
                    self.allResults[companyLink.split("/")[4]]["JobsList"] = []
                    tempResults["Title"] = title
                    tempResults["Premium"] = checkPremium
                    tempResults["JobLink"] = jobLink
                    tempResults["JobType"] = jobType
                    self.allResults[companyLink.split("/")[4]]["JobsList"].append(tempResults)

                # exist -> only append new job
                else:
                    tempResults["Title"] = title
                    tempResults["Premium"] = checkPremium
                    tempResults["JobLink"] = jobLink
                    tempResults["JobType"] = jobType
                    self.allResults[companyLink.split("/")[4]]["JobsList"].append(tempResults)

            # temp line, it will delete in the future
            break

    def exportToJson(self):
        try:
            with open("jobinja.json", "w", encoding="utf-8") as file:
                json.dump(self.allResults, file, ensure_ascii=False, indent=4)
        except:
            raise ValueError("Can Not Save !")

# %%
temp = jobinjaCrawler()
temp.findjobs()

# %%
temp.exportToJson()