from hashlib import sha256


def computeHash(input:str) -> str:
    return sha256(input.encode('utf-8')).hexdigest()


def computeDoubleHash(input:str) -> str:
    return computeHash(computeHash(input))

def hashHeader(headerInfo, nonce) -> str:
    headerArr = bytes(headerInfo, "utf-8")
    
    newVal = int.from_bytes(headerArr, "big") + nonce
    
    return computeDoubleHash(str(newVal))


def headerHashAndCheck(headerInfo, nonce, difficulty):
    target = (2**256 - 1)//difficulty
    
    headerArr = bytes(headerInfo, "utf-8")
    
    newVal = int.from_bytes(headerArr, "big") + nonce
    
    intValProof = int(computeDoubleHash(str(newVal)), 16)
    
    return intValProof < target






#vars


#coin has 1 mil subdivisions
COIN = 1000 * 1000

#coinbase address
COINBASE = "0"*64

REWARD = 100*COIN
    
#10 MEGAHASHES
STARTING_DIFFICULTY = 1000 * 1000 * 0.01
    
