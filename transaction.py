from crypto import *
import time


class Transaction:
    
    def __init__(self, sender, nonce, note=""):
        self.sender = sender
        self.timestamp = round(time.time())
        self.outputs = []
        self.nonce = nonce
        self.signature = ""
        self.note = ""
    
    def addOutput(self, reciever, amount) -> None:
        output = {
            "reciever" : reciever, 
            "amount" : amount
        }
        
        assert type(amount) == int
        
        if output not in self.outputs:
            self.outputs.append(output)
     
    @staticmethod       
    def calculateTotal(transaction) -> int:
        if not isinstance(transaction, dict):
            transaction = transaction.__dict__
            
        total = 0
        
        for output in transaction["outputs"]:
            total += output["amount"]
            
        return total
    
    