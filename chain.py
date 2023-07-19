from crypto import *
from transaction import Transaction
from wallet import Wallet
import time
import json
import os



#updatedlevel:
# 0 -> nothing
# 1 -> head info updated
# 2 -> on the most recent block
class Chain:
    
    def __init__(self, name="main"):
        self.updatedLevel = False
        self.height = -1
        self.chainName = name
        
    def initChain(self):
        
        if not os.path.isdir("blockchain"):
            os.mkdir("blockchain")
            
        if not os.path.isdir("blockchain/batches"):
            os.mkdir("blockchain/batches")
        
        if not os.path.isdir("blockchain/accounts"):
            os.mkdir("blockchain/accounts")
            
        if not os.path.isfile("blockchain/chaininfo.dat"):
            self.writeChainInfo()
            
    def dumpChain(self) -> None:
        batch = 0
        while os.path.isfile(f"blockchain/batches/{batch}.dat"):
            os.remove(f"blockchain/batches/{batch}.dat")
            batch += 1
            
        for file in os.listdir("blockchain/accounts"):
            os.remove(f"blockchain/accounts/{file}")
            
        if os.path.isfile("blockchain/chaininfo.dat"):
            os.remove("blockchain/chaininfo.dat")
        

            
        
        
    def writeChainInfo(self):
        with open("blockchain/chaininfo.dat", "w") as file:
            file.write(json.dumps(self.__dict__))
        

            
            
    def addBlock(self, block):
        if not isinstance(block, dict):
            block = block.__dict__

        assert (block["height"] - self.height) == 1
            
        self.height += 1
        
        blockAlreadyInChain = (self.readBlock(block["height"]) != None)
        
        if blockAlreadyInChain:
            return False
        
        assert self.verifyBlock(block)
        
        #new file every 100 blocks
        file = f"blockchain/batches/{block['height']//100}.dat"
        
        if not os.path.isfile(file):
            with open(file, "w") as toWrite:
                toWrite.write(json.dumps([block]))
        else:
            chunk = None
            with open(file, "r") as toRead:
                chunk = json.loads(toRead.read())
                chunk.append(block)
                
            with open(file, "w") as toWrite:
                toWrite.write(json.dumps(chunk))
                
                
        self.writeChainInfo()
        self.fufillVerifiedBlockTransactions(block)
                
        return True
    
    #remove block from top of chain
    def popBlock(self):
        #get batch file
        targetFile = f"blockchain/batches/{self.height//100}.dat"
        
        assert os.path.isfile(targetFile)
        
        chunks = []
        with open(targetFile, "r") as toRead:
            chunks = json.loads(toRead.read())
            
        assert len(chunks) >= 1
            
        #if first block in file
        if len(chunks) == 1:
            #delete file
            os.remove(targetFile)
        else:
            #remove last block
            chunks.pop()
            with open(targetFile, "w") as toWrite:
                toWrite.write(json.dumps(chunks))

            
    
    @staticmethod
    def readBlock(height) -> dict:
        file = f"blockchain/batches/{height//100}.dat"

        
        if not os.path.isfile(file):
            return None
        
        with open(file, "r") as toRead:
            chunk = json.loads(toRead.read())
            
            if len(chunk) <= height%100:
                return None
            
            return chunk[(height%100)]
        
    @staticmethod
    def calculateDifficulty(height) -> int: 
        if height < 144:
            return round(STARTING_DIFFICULTY)
        
        if height % 144 != 0:
            return Chain.readBlock(height-1)["difficulty"]

        baseHeight = height - 144

        baseBlock = Chain.readBlock(baseHeight)
        mostRecent = Chain.readBlock(height-1)

        expectedTimespan = 60 * 60 * 24# one day worth of seconds
        timespan = mostRecent["timestamp"] - baseBlock["timestamp"]



        modifier = expectedTimespan/timespan

        return round(mostRecent["difficulty"] * modifier)
    
    def getInfoFromFile(self):
        with open("blockchain/chaininfo.dat", "r") as file:
            info = json.loads(file.read())
            
            self.height = info["height"]
            self.updatedLevel = 1
            
            
            
    def initAccount(self, address, startNonce, startBalance):
        assert type(startNonce) == int
        assert type(startBalance) == int
        
        account = {
            "nonce" : startNonce, 
            "balance" : startBalance,
            "associated" : []
        }
        
        
        assert os.path.isdir("blockchain/accounts")
        
        #first 4 letters, so maximum of 16**3 files
        filename = f"blockchain/accounts/{address[0:3]}.dat"
        if os.path.isfile(filename):
            alreadyAccounts = {}
            with open(filename, "r") as toRead:
                alreadyAccounts = json.loads(toRead.read())
                
            #if somehow exists
            if alreadyAccounts.get(address, None) != None:
                return
            
            alreadyAccounts[address] = account
            
            with open(filename, "w") as toWrite:
                toWrite(json.dumps(alreadyAccounts))
        else:
            accounts = {}
            accounts[address] = account
            
            with open(filename, "w") as toWrite:
                toWrite.write(json.dumps(accounts))
                                
    
    #will return None if nothing is found
    def getAccountInfo(self, address):
        filename = f"blockchain/accounts/{address[0:3]}.dat"
        
        if os.path.isfile(filename):
            with open(filename, "r") as toRead:
                accounts = json.loads(toRead.read())
                
                return accounts.get(address)
        else:
            return None
        
    def updateAccount(self, address, nonce, balance, associatedBlockHeight=None):
        filename = f"blockchain/accounts/{address[0:3]}.dat"
        
        if self.getAccountInfo(address) == None:
            self.initAccount(address, nonce, balance)
        else:
            accounts = {}
            with open(filename, "r") as toRead:
                accounts = json.loads(toRead.read())
                
                accounts[address]["nonce"] = nonce
                accounts[address]["balance"] = balance
                
                if associatedBlockHeight != None:
                    accounts[address]["associated"].append(associatedBlockHeight)
                
            with open(filename, "w") as toWrite: 
                toWrite.write(json.dumps(accounts))
                
    def modifyBalanceAndNonce(self, address, deltaBalance, nonce=None, associatedBlockHeight=None):
        oldInfo = self.getAccountInfo(address)
        
        if oldInfo == None:
            startNonce = 0
            if nonce != None:
                startNonce = nonce
                
            assert deltaBalance >= 0
            
            self.initAccount(address, startNonce, deltaBalance)
            self.updateAccount(address, startNonce, deltaBalance, associatedBlockHeight=associatedBlockHeight)
        else:
            changedNonce = oldInfo["nonce"]
            if nonce != None:
                assert max(nonce, oldInfo["nonce"]) == nonce
                
                changedNonce = nonce
        
                
            self.updateAccount(address, changedNonce, oldInfo["balance"]+deltaBalance, associatedBlockHeight=associatedBlockHeight)
                    
                
        return True

    def verifyIncomingTransaction(self, transaction):   
        try:
            try:
                transaction = transaction.__dict__
            except:
                if not isinstance(transaction, dict):
                    return False
                
                
            json.loads(json.dumps(transaction), object_hook=Transaction)
        except:
            return False
        
        senderInfo = self.getAccountInfo(transaction["sender"])
        balance = senderInfo["balance"]
        total = Transaction.calculateTotal(transaction)
        
        for output in transaction["outputs"]:
            if output["amount"] < 0:
                return False
        
        if total > balance:
            return False
        elif Wallet.verifyTransactionSignature(transaction):
            return False
        
        
        return True
    
    
    def fufillVerifiedBlockTransactions(self, block):
        assert isinstance(block, dict)
        
        for transac in block["transactions"]:
            if transac["sender"] == COINBASE:
                for output in transac["outputs"]:
                    self.modifyBalanceAndNonce(output["reciever"], output["amount"], nonce=transac["nonce"], associatedBlockHeight=block["height"])
            else:
                totalAmount = Transaction.calculateTotal(transac)
                self.modifyBalanceAndNonce(transac["sender"], -totalAmount, nonce=transac["nonce"], associatedBlockHeight=block["height"])
                for output in transac["outputs"]:
                    assert output["amount"] >= 0
                    self.modifyBalanceAndNonce(output["reciver"], output["amount"], associatedBlockHeight=block["height"])
                
    
    
    def verifyBlock(self, block):
        if block["height"] == 0:
            return True
        
        try:
            block = block.__dict__
        except:
            if not isinstance(block, dict):
                return False

        lastBlock = self.readBlock(block["height"]-1)
    

        #test to see if hash is valid
        headerInfo = bytes(str(block["timestamp"]) + json.dumps(block["transactions"]) + lastBlock["header"], "utf-8").hex()
        intendedHeader = hashHeader(headerInfo, block["nonce"])
        difficulty = self.calculateDifficulty(block["height"])
        
        #if block has invalid difficulty
        if block["difficulty"] != difficulty:
            return False
        
        #lying about header
        if intendedHeader != block["header"]:
            return False
        
        #check to see proof of work
        if not headerHashAndCheck(headerInfo, block["nonce"], difficulty):
            return False
        
        #check timeframe, cant be before previous block
        if block["timestamp"] < lastBlock["timestamp"]:
            return False
        
        #now on to transactions
        
        #check coinbase transaction
        #filtering other transactions
        coinbaseTransactions = list(filter(lambda transac: transac["sender"] == COINBASE, block["transactions"]))
        if len(coinbaseTransactions) != 1:
            return False
        
        coinbaseTransac = coinbaseTransactions[0]

        #can go anywhere, but must be reward amount
        if Transaction.calculateTotal(coinbaseTransac) != REWARD:
            return False
        
        #verify transac signature
        if not Wallet.verifyTransactionSignature(coinbaseTransac, coinbaseException=block["miner"]):
            return False
        
        
        #run through transactions
        for transac in block["transactions"]:
            if transac["sender"] == COINBASE:
                continue 
            
            if not self.verifyIncomingTransaction(transac):
                return False
            
        return True
    
            
        
        
        
        
        
        
        
            
        
    
    
            
            
            
            
        
                
                
        
        