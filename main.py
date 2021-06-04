import utils
from colorama import Fore, init
from os import system
from datetime import datetime


init()
system("cls")


def info(msg):
	print(f"{Fore.GREEN}[INFO] >> {Fore.WHITE}{msg}{Fore.RESET}")


def inp(msg):
	print(f"{Fore.GREEN}[INPUT] {Fore.WHITE}{msg}")
	response = input(f"{Fore.GREEN}>> {Fore.WHITE}")
	print()
	return response


def mojang_nc():

	config = utils.readConfig()

	name = inp("Name to snipe")
	delay = float(inp("Delay offset in milliseconds")) / 1000

	accounts = utils.readAccounts(int(config["max accounts (mojang)"]))
	info("Loaded " + str(len(accounts)) + " accounts!")

	try:
		dropTime = utils.fetchDroptime(name)
	except Exception:
		info("Was unable to find a droptime for " + name)
		quit()
	info("Started snipe for " + name + ", dropping at " + str(datetime.fromtimestamp(dropTime)) + "!\n")

	utils.sleep_until(dropTime - 50)

	accObjects = []
	for account in accounts:
		email, password = account.split(":")[0], account.split(":")[1]
		sq = account.split(":")[2:]
		accObjects.append(utils.MojangAccount(email, password, name, sq))
	accounts = accObjects

	for account in accounts:
		account.authenticate()

	done = 0
	for i in range(len(accounts)):
		account = accounts[done]
		if not account.valid:
			if account.error == 1:
				info(Fore.RED + account.email + " was unable to authenticate, it is most likely locked or invalid")
			elif account.error == 2:
				info(Fore.RED + account.email + " needs the answers to security questions, but you did not insert any")
				info("Account format: email:password:answer1:answer2:answer3")
			elif account.error == 3:
				info(Fore.RED + account.email + " is unable to change its name right now")
			else:
				info(Fore.RED + account.email + " encountered an error (code " + account.error + "), it possibly somehow didnt authenticate")
			accounts.remove(account)
			done -= 1
		else:
			info(Fore.GREEN + "successfully authenticated " + account.email)
		done += 1


	for account in accounts:
		account.create_payload()

	utils.sleep_until(dropTime - 10)

	socks = []
	for account in accounts:
		for i in range(2):
			socks.append(utils.SocketConnection(account.payload, {"email": account.email, "password": account.password, "bearer": account.bearer}))

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
		info("Received " + str(sock.status_code) + " @ " + str(datetime.now()))
		if sock.status_code == "200":
			info(Fore.GREEN + "SUCCESS! - Sniped " + name + " @ " + str(datetime.now()) + " on " + sock.data["email"])
            r = requests.post("https://api.minecraftservices.com/minecraft/profile/skins", headers={"Authorization": sock.data["bearer"]}, json={"variant": "slim", "url": config["skin url"]})
            if r.status_code == 200:
                info(Fore.GREEN + "Changed skin")


def main():
	print (f"{Fore.GREEN} ______     _   _                \n|  ____|   | | (_)               \n| |__   ___| |_ _ _ __ ___   ___ \n|  __| / __| __| | '_ ` _ \ / _ \ \n| |____\__ \ |_| | | | | | |  __/\n|______|___/\__|_|_| |_| |_|\___|")
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
		quit()
	if option == 1:
		mojang_nc()
	elif option == 2:
		info("Coming soon!")
		quit()
	elif option == 3:
		info("Coming soon!")
		quit()


if __name__ == "__main__":
	main()
