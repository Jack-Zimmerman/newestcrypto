import sys
from wallet import *

walletName = sys.argv[1]

wallet = Wallet(walletName)
wallet.initWallet()