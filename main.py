import utils
from colorama import Fore, init
from os import system


init()
system('cls')


def info(msg):
	print(f"{Fore.GREEN}[INFO] >> {Fore.WHITE}{msg}")


def inp(msg):
	print(f"{Fore.GREEN}[INPUT] {Fore.WHITE}{msg}")
	response = input(f"{Fore.GREEN}>> {Fore.WHITE}")
	print()
	return response


def main():
	print (f"{Fore.GREEN} ______     _   _                \n|  ____|   | | (_)               \n| |__   ___| |_ _ _ __ ___   ___ \n|  __| / __| __| | '_ ` _ \ / _ \ \n| |____\__ \ |_| | | | | | |  __/\n|______|___/\__|_|_| |_| |_|\___|")
	print("""
1. Mojang namechange sniper
2. Giftcode sniper
3. Microsoft namechange sniper
""")
	option = inp('option')
	try:
		option = int(option)
	except Exception:
		info('Please input the number of the option you want to choose!')
		quit()
	if option == 1:
		mojang_nc()
	elif option == 2:
		info('Coming soon!')
		quit()
	elif option == 3:
		info('Coming soon!')
		quit()


if __name__ == "__main__":
	main()
