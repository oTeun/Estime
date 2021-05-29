import requests
import socket
import ssl


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
