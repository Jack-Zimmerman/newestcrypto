from block import *
from crypto import hashHeader
from transaction import *
from chain import *
from wallet import *
import random

import time
import types


pastBlock = types.SimpleNamespace()
pastBlock.height = -1
pastBlock.header = "0"
pastBlock.difficulty = STARTING_DIFFICULTY

pastBlock = pastBlock.__dict__


lol = Chain()
lol.dumpChain()
lol.initChain()


wallet = Wallet("JZ")
wallet.initWallet()


block = None
for x in range(100):
    block = Block(wallet.public, pastBlock)
    block.complete(wallet)
    
    
    nonce = 0
    while not Block.tryNonce(block, nonce):
        nonce += 1
        
    block.solidify(nonce)
    
    lol.addBlock(block)
    pastBlock = block.__dict__
    



    
    




