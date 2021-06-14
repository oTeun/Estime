import requests
import socket
import ssl
from time import time, sleep


class AuthenticationError(Exception):
    pass


class SeccurityQuestionsNotFound(Exception):
    pass


class NameChangeNotAllowed(Exception):
    pass


def readConfig():
    with open("config.txt", "r") as f:
        lines = f.read().splitlines()  # read content of config.txt
        f.close()  # close file
    config = {}
    for line in lines:
        try:
            if "#" not in line:
                config[line.split(": ")[0]] = line.split(": ")[1]
        except Exception:
            pass
    if config != {}:
        return config
    else:
        return None  # return None if content of file was empty or incorrect


def readAccounts(maxAccs):
    with open('accounts.txt', 'r') as f:
        lines = f.read().splitlines()  # read contents of the accounts file
        f.close()  # close the accounts file
    return lines[:maxAccs]  # return accounts limited to the max amount of accounts given


def fetchDroptime(name):
    r = requests.get('https://api.teun.lol/droptime/' + name)
    r_json = r.json()  # parse the json from the response
    dropTime = r_json['UNIX']
    return dropTime


def sleep_until(timestamp):
    try:
        sleep(timestamp - time())  # sleep until target timestamp
    except Exception:
        pass


class MojangAccount:
    def __init__(self, email, password, wantedName, sq):
        self.email = email
        self.password = password
        self.wantedName = wantedName
        self.sq = sq
        self.valid = False
        self.bearer = None
        self.authHeaders = {}
        self.nameChangeAllowed = True
        self.payload = b""

    def authenticate(self):
        payload = {
            "username": self.email,
            "password": self.password,
            "requestUser": True
        }

        r = requests.post("https://authserver.mojang.com/authenticate", json=payload)

        if r.status_code == 200:  # check if account is valid
            self.bearer = "Bearer " + r.json()["accessToken"]
            self.authHeaders = {"Authorization": self.bearer}
            self.valid = True
        else:
            self.valid = False
            raise AuthenticationError

        r = requests.get("https://api.mojang.com/user/security/location", headers=self.authHeaders)

        if r.status_code != 204:  # check if security questions are needed
            r = requests.get("https://api.mojang.com/user/security/challenges",
                             headers=self.authHeaders)  # fetch list of securty questions
            if r.json():
                if not self.sq:
                    self.valid = False
                    raise SeccurityQuestionsNotFound

                payload = [
                    {"id": r.json()[0]["answer"]["id"], "answer": self.sq[0]},
                    {"id": r.json()[1]["answer"]["id"], "answer": self.sq[1]},
                    {"id": r.json()[2]["answer"]["id"], "answer": self.sq[2]}]

                requests.post("https://api.mojang.com/user/security/location",
                              headers=self.authHeaders, json=payload)

            r = requests.get("https://api.minecraftservices.com/minecraft/profile/namechange",
                             headers=self.authHeaders)

        try:
            if not r.json()["nameChangeAllowed"]:  # check if account can namechange
                self.valid = False
                raise NameChangeNotAllowed
        except Exception:
            pass

    def create_payload(self):
        payload = "\r\n".join((f"PUT /minecraft/profile/name/{self.wantedName} HTTP/1.1",
                               "Host: api.minecraftservices.com",
                               "Content-Type: application/json",
                               f"Authorization: {self.bearer}",
                               "\r\n"))
        self.payload = bytes(payload, "utf-8")


class SocketConnection:
    def __init__(self, payload, data):
        self.payload = payload
        self.data = data
        self.sock = None
        self.response = {}
        self.status_code = None
        self.full_resp = ""

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname="api.minecraftservices.com")
        sock.connect(("api.minecraftservices.com", 443))
        self.sock = sock

    def send(self):
        self.sock.send(self.payload)

    def close(self):
        self.sock.close()

    def receive(self):
        self.full_resp = self.sock.recv(4096).decode("utf-8")
        self.status_code = self.full_resp[9:12]
