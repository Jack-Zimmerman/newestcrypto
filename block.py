from crypto import * 
from transaction import *
from chain import *
import time
import json


class Block:
    def __init__(self, miner, pastBlock):
        assert pastBlock != None
            
        self.miner = miner
        self.tempPast = pastBlock
        self.height = self.tempPast["height"] + 1  #1 million subdivisions, 1 coin
        
        
        self.difficulty = pastBlock["difficulty"]
        if self.height != 0 and self.height % 144 == 0:
            self.difficulty = Chain.calculateDifficulty(self.height)
            
        self.difficulty = round(self.difficulty)
            
        self.version = 0.1
        self.nonce = None
        self.transactions = []
        
    def addTransaction(self, transaction):
        #try and verify transaction -> need to be done
        
        if isinstance(transaction, Transaction):
            transaction = transaction.__dict__
        else:
            assert isinstance(transaction, dict)
            
        self.transactions.append(transaction)
        
    def complete(self,wallet) -> None:  
        self.timestamp = round(time.time())
        
        self.addCoinbase(wallet)
        
        self.headerInfo = str(self.timestamp) + json.dumps(self.transactions) + self.tempPast["header"]
        
    def solidify(self,nonce) -> None:
        self.header = hashHeader(self.headerInfo, nonce)
        self.nonce = nonce
        
        del self.headerInfo
        del self.tempPast
        
        return True
    

    def addCoinbase(self, wallet):
        transac = Transaction(COINBASE, wallet.takeNonce())
        transac.addOutput(wallet.public, REWARD)
        
        wallet.signTransaction(transac)
        
        self.transactions.append(transac.__dict__)
        
        
    @staticmethod
    def tryNonce(block, nonce):
        try:
            block = block.__dict__
        except:
            assert isinstance(block, dict)
            
        return headerHashAndCheck(block["headerInfo"], nonce, block["difficulty"])
   
    
    

        
    
        