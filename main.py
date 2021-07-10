import utils
from colorama import Fore, init
from os import system
from datetime import datetime
import requests
import sys

init()
system("cls")
version = "1.0.1"


def info(msg):
    print(f"{Fore.GREEN}[INFO] >> {Fore.WHITE}{msg}{Fore.RESET}")


def inp(msg):
    print(f"{Fore.GREEN}[INPUT] {Fore.WHITE}{msg}")
    response = input(f"{Fore.GREEN}>> {Fore.WHITE}")
    print()
    return response


def mojang_nc(name, delay):
    print()

    config = utils.readConfig()

    delay = float(delay) / 1000

    accounts = utils.readAccounts(int(config["max accounts (mojang)"]), 'accounts.txt')
    info(f"Loaded {len(accounts)} accounts!")

    try:
        dropTime = utils.fetchDroptime(name)
    except Exception:
        info(f"Was unable to find a droptime for {name}")
        done()
    info(f"Started snipe for {name}, dropping at {datetime.fromtimestamp(dropTime)}!\n")

    utils.sleep_until(dropTime - 50)

    accObjects = []
    for account in accounts:
        combo = account.split(":")
        email, password = combo[0], combo[1]
        sq = combo[2:]
        accObjects.append(utils.MojangAccount(email, password, name, sq))
    accounts = accObjects

    for account in accounts:
        try:
            account.authenticate()

        except utils.AuthenticationError:
            info(f"{Fore.RED}{account.email} was unable to authenticate, it is most likely locked or invalid")

        except utils.SecurityQuestionsNotFound:
            info(f"{Fore.RED}{account.email} needs the answers to security questions, but you did not insert any")
            info("Account format: email:password:answer1:answer2:answer3")

        except utils.NameChangeNotAllowed:
            info(f"{Fore.RED}{account.email} is unable to change its name right now")

        except Exception:
            info(
                f"{Fore.RED}{account.email} encountered an error")

    _done = 0
    for i in range(len(accounts)):
        account = accounts[_done]
        if not account.valid:
            accounts.remove(account)
            _done -= 1
        else:
            info(f"{Fore.GREEN}successfully authenticated {account.email}")
        _done += 1

    if len(accounts) == 0:
        info(f"{Fore.RED}No accounts are left, quitting.")
        done()

    for account in accounts:
        account.create_payload()

    utils.sleep_until(dropTime - 10)

    socks = []
    for account in accounts:
        for i in range(int(config['requests per account (mojang)'])):
            socks.append(utils.SocketConnection(account.payload, {"email": account.email, "password": account.password,
                                                                  "bearer": account.bearer}))

    for sock in socks:
        sock.connect()

    utils.sleep_until(dropTime - delay)

    for sock in socks:
        sock.send()

    for sock in socks:
        sock.receive()

    for sock in socks:
        sock.close()

    print()

    for sock in socks:
        info(f"Received {sock.status_code} @ {datetime.now()}")
        if sock.status_code == "200":
            info(f"{Fore.GREEN}SUCCESS! - Sniped {name} @ {datetime.now()} on {sock.data['email']}")
            r = requests.post("https://api.minecraftservices.com/minecraft/profile/skins",
                              headers={"Authorization": sock.data["bearer"]},
                              json={"variant": "slim", "url": config["skin url"]})
            if r.status_code == 200:
                info(f"{Fore.GREEN}Changed skin")


def microsoft_gc(name, delay):
    print()

    config = utils.readConfig()

    delay = float(delay) / 1000

    accounts = utils.readAccounts(int(config["max accounts (microsoft)"]), 'tokens.txt')
    info(f"Loaded {len(accounts)} accounts!")

    try:
        dropTime = utils.fetchDroptime(name)
    except Exception:
        info(f"Was unable to find a droptime for {name}")

        try:
            dropTime = float(inp("Enter manual droptime in UNIX: "))
        except Exception:
            done()

    info(f"Started snipe for {name}, dropping at {datetime.fromtimestamp(dropTime)}!\n")

    utils.sleep_until(dropTime - 50)

    accObjects = []
    for account in accounts:
        accObjects.append(utils.MicrosoftAccount(account, name))
    accounts = accObjects

    for account in accounts:
        account.create_payload()

    utils.sleep_until(dropTime - 10)

    socks = []
    for account in accounts:
        for i in range(int(config['requests per account (microsoft)'])):
            socks.append(utils.SocketConnection(account.payload, {"bearer": account.bearer}))

    for sock in socks:
        sock.connect()

    utils.sleep_until(dropTime - delay)

    for sock in socks:
        sock.send()

    for sock in socks:
        sock.receive()

    for sock in socks:
        sock.close()

    print()

    for sock in socks:
        info(f"Received {sock.status_code} @ {datetime.now()}")
        if sock.status_code == "200":
            info(f"{Fore.GREEN}SUCCESS! - Sniped {name} @ {datetime.now()}")
            info(f"{Fore.GREEN}{sock.data['bearer']}")
            r = requests.post("https://api.minecraftservices.com/minecraft/profile/skins",
                              headers={"Authorization": sock.data["bearer"]},
                              json={"variant": "slim", "url": config["skin url"]})
            if r.status_code == 200:
                info(f"{Fore.GREEN}Changed skin")


def main():
    print(
        f"{Fore.GREEN} ______	 _   _				\n|  ____|   | | (_)			   \n| |__   ___| |_ _ _ __ ___   ___ \n|  __| / __| __| | '_ ` _ \ / _ \ \n| |____\__ \ |_| | | | | | |  __/\n|______|___/\__|_|_| |_| |_|\___|")
    print("Developed by Teun | discord.gg/98ZMYfD9HJ")
    print(f"Version: v{version}")

    options = []

    if len(sys.argv) > 1:
        try:
            options = sys.argv[1:]
        except Exception:
            pass

    if len(options) == 3:

        if options[0].lower() in ["1", "mojang", "mojang_nc", "mojang namechange sniper"]:
            mojang_nc(options[1], options[2])

        elif options[0].lower() in ["2", "gc", "giftcode", "giftcard", "giftcode sniper"]:
            microsoft_gc(options[1], options[2])

        else:
            info("""Your arguments were incorrect.
Please enter like this: main.py (sniper option) (wanted name) (delay)
Examples:
- main.py mojang coolName 45
- main.py gc coolName 55
- main.py""")
            done()

    elif len(options) != 0:
        info("""Your arguments were incorrect.
Please enter like this: main.py (sniper option) (wanted name) (delay)
Examples:
- main.py mojang coolName 45
- main.py gc coolName 55
- main.py""")
        done()

    print("""
1. Mojang namechange sniper
2. Giftcode sniper
3. Microsoft namechange sniper
    """)

    option = inp("Option")

    try:
        option = int(option)
    except Exception:
        info("Please input the number of the option you want to choose!")
        done()

    name = inp("Name to snipe")
    delay = inp("Delay offset in milliseconds")

    if option == 1:
        mojang_nc(name, delay)
    elif option == 2:
        microsoft_gc(name, delay)
    elif option == 3:
        info("Coming soon!")
        done()


def done():
    print()
    info('Press enter to exit')
    input()
    quit()


if __name__ == "__main__":
    main()
