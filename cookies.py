import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# get new cookies
class getCookies():
    def __init__(self) -> None:
        self.cookies = None
        self.__get()
        self.__Write()

    
    def __del__(self):
        self.driver.quit()


    def __get(self):
        # load the options
        op = Options()
        op.page_load_strategy = "none"
        op.add_argument("--headless")
        # create driver in background
        self.driver = webdriver.Firefox(options=op)
        for _ in range(10):
            self.driver.get("https://jobinja.ir/")
            try :
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CLASS_NAME, "c-header__brandingHeading"))
                )
                if self.driver.get_cookies().__len__() == 0:
                    self.driver.quit()
                    self.driver = webdriver.Firefox(options=op)
                    time.sleep(1)
                    continue

                self.cookies = self.driver.get_cookies()
                return

            except:
                self.driver.quit()
                self.driver = webdriver.Firefox(options=op)
                time.sleep(1)

        raise ConnectionError(f"Can't get new cookies!")
    

    def __Write(self):
        if self.cookies == None:
            exit(1)
        else:
            cookies = ""
            for i in self.cookies:
                cookies += f"{i['name']}={i['value']}; "

            with open("./cookie.txt", "w", encoding="utf-8") as f:
                json.dump(cookies, f)



if __name__ == "__main__":
    g = getCookies()
    del g
