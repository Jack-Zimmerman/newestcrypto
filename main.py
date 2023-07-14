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

block = Block(wallet.public, pastBlock)
block.complete(wallet)


nonce = 0
while not Block.tryNonce(block, nonce):
    nonce += 1
    
block.solidify(nonce)

block = block.__dict__

lol.addBlock(block)

lol.fufillVerifiedBlockTransactions(block)

newBlock = Block(wallet.public, block)
newBlock.complete(wallet)

nonce = 0
while not Block.tryNonce(newBlock, nonce):
    nonce += 1
    
newBlock.solidify(nonce)

newBlock = newBlock.__dict__
print(lol.verifyBlock(newBlock))

lol.addBlock(newBlock)

lol.fufillVerifiedBlockTransactions(newBlock)




    
    




