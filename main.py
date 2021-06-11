import time

import requests

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = "YOUR TOKEN"


class SpotiLink:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "authorization": TOKEN,
            "content-type": "application/json"
        }
        self.spotify_accounts = self.parse_accounts()
        self.progress = 0
        self.account_amount = len(self.spotify_accounts)
        for email, password in self.spotify_accounts:
            self.login_and_link(email, password)
            time.sleep(1)
        self.set_all_visible()

    @staticmethod
    def parse_accounts():
        with open("accounts.txt", "r") as f:
            accounts = [line.strip() for line in f.readlines()]
        return [(account.split(':')[0], account.split(':')[1]) for account in accounts]

    @staticmethod
    def get_web():
        opts = webdriver.ChromeOptions()
        opts.add_experimental_option('detach', True)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
        return driver

    def login_and_link(self, email, password):
        try:
            discord_auth = self.get_discord_auth()
            self.progress += 1
        except KeyError:
            return print(f"Couldn't get the auth URL, did you enter a correct token? "
                         f"{self.progress}/{self.account_amount}")
        driver = self.get_web()
        driver.get(discord_auth)
        try:
            username_field = driver.find_element_by_name("username")
            username_field.clear()
            username_field.send_keys(email)

            password_field = driver.find_element_by_name("password")
            password_field.clear()
            password_field.send_keys(password)

            driver.find_element_by_id("login-button").send_keys(Keys.ENTER)
            driver.find_element_by_id("auth-accept").send_keys(Keys.ENTER)
        except NoSuchElementException:
            print(f"Couldn't link spotify account: {email}:{password}")
        driver.close()

    def get_discord_auth(self):
        r = requests.get("https://discord.com/api/v9/connections/spotify/authorize", headers=self.headers).json()
        return r["url"]

    def set_all_visible(self):
        connections = requests.get("https://discord.com/api/v9/users/@me/connections", headers=self.headers)
        if not connections.ok:
            return print("Couldn't get your connections, did you enter a correct token?")
        connections = connections.json()
        self.headers["content-type"] = "application/json"
        for connection in connections:
            if connection["type"] == "spotify" and connection["visibility"] == 0:
                d = {
                    "visibility": 1
                }
                r = requests.patch(f"https://discord.com/api/v9/users/@me/connections/spotify/{connection['id']}",
                                   json=d, headers=self.headers)
                if r.ok:
                    print(f"Successfully made a Spotify visible on your account!:"
                          f"\nName - {connection['name']}"
                          f"\nID - {connection['id']}")


SpotiLink(TOKEN)
