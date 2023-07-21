from hashlib import sha256


def computeHash(input:str) -> str:
    return sha256(input.encode('utf-8')).hexdigest()


def computeDoubleHash(input:str) -> str:
    return computeHash(computeHash(input))

def hashHeader(headerInfo, nonce) -> str:
    headerVal = int(headerInfo, 16)
    
    newVal = headerVal + nonce
    
    return computeDoubleHash(str(newVal))


def headerHashAndCheck(headerInfo, nonce, difficulty, test=False):
    target = (2**256 - 1)//difficulty
    
    headerVal = int(headerInfo, 16)
    
    newVal = headerVal + nonce
    
    intValProof = int(computeDoubleHash(str(newVal)), 16)
    
    
    return intValProof < target






#vars


#coin has 1 mil subdivisions
COIN = 1000 * 1000

#coinbase address
COINBASE = "0"*64

REWARD = 100*COIN
    
#10 MEGAHASHES
KILOHASH = 1000
MEGAHASH = KILOHASH*KILOHASH
STARTING_DIFFICULTY = KILOHASH*10


GENESIS_BASIS = {
    "header" : "0"*64,
    "difficulty" : round(STARTING_DIFFICULTY),
    "height" : -1
}
    
