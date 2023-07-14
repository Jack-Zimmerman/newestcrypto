import ecdsa 
from transaction import *
from crypto import *
import json
import os

class Wallet:
    def __init__(self, name):
        self.private = None
        self.public = None
        self.nonce = 0
        self.name = name
        
    def initWallet(self):
        #check to see if wallet already exists
        if not os.path.isdir("wallets"):
            os.mkdir("wallets")
            
        filename = f"wallets/{self.name}.dat"
        
        if not os.path.isfile(filename):
            self.private = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
            public = self.private.get_verifying_key()
            self.public = public.to_string("compressed").hex()
            self.private = self.private.to_string().hex()
            
            with open(filename, "w") as toWrite:
                toWrite.write(json.dumps(self.__dict__))
                
        else: 
            with open(filename, "r") as toRead:
                info = json.loads(toRead.read())
                
                self.private = info["private"]
                self.public = info["public"]
                self.nonce = info["nonce"]
        
    def signTransaction(self, transac):
        if isinstance(transac, Transaction):
            transac = transac.__dict__
        else:
            assert isinstance(transac, dict)
            
        #signing key pulled from hex
        sKey = ecdsa.SigningKey.from_string(bytes.fromhex(self.private), curve=ecdsa.SECP256k1)
        
        signatureInfo = json.dumps(transac["outputs"]) + str(transac["timestamp"]) + str(transac["nonce"])
        
        signature = sKey.sign(bytes(signatureInfo, "utf-8")).hex()
        
        transac["hash"] = computeHash(signatureInfo)
        transac["signature"] = signature
        
    
    def takeNonce(self):
        filename = f"wallets/{self.name}.dat"
        nonce = None
        with open(filename, "r") as toRead:   
            nonce = json.loads(toRead.read())["nonce"]
            
        self.nonce = max(self.nonce, nonce+1)
        
        with open(filename, "w") as toWrite:
            toWrite.write(json.dumps(self.__dict__))
        
        
    @staticmethod
    def verifyTransactionSignature(transac, coinbaseException=None):
        if isinstance(transac, Transaction):
            transac = transac.__dict__
        else:
            assert isinstance(transac, dict)
            
        public = transac["sender"]
        
        if coinbaseException != None:
            public = coinbaseException
        
            
 
        vKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(public), curve=ecdsa.SECP256k1)
        signatureInfo = json.dumps(transac["outputs"]) + str(transac["timestamp"]) + str(transac["nonce"])
        
        #verification returns error if false
        try:
            vKey.verify(bytes.fromhex(transac["signature"]), bytes(signatureInfo, "utf-8"))
        except:
            return False
        
        return True
        

