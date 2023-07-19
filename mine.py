from crypto import *
import time
import requests
import sys


def mine(headerInfo, difficulty, returnPort):
    start = time.time()
    checkpoint = time.time()
    nonce = 0
    while not headerHashAndCheck(headerInfo, nonce, difficulty):
        print(nonce)
        nonce += 1
        
        if nonce % 100000 == 0:
            print("")
            print("-"*100)
            print("Current Hashrate:", str(round(100000//(time.time()-checkpoint))))
            print("Average Hashrate:", str(round(nonce//(time.time()-start))))
            print("Started", str(round((time.time()-start)/60,2)),  "minutes ago")
            checkpoint = time.time()
            
    #if it gets to this point, it must have been successful
    
    request = f"http://localhost:{returnPort}/minersuccess?nonce={nonce}"
    
    print(request)
    
    requests.get(request)
    


sys.stdout.flush()
print("Miner version 1.0 - Jack Zimmerman - 7/16/2023")
print("-"*50)
print("Data recieved: " + sys.argv[1][0:10] + "...")
print("Difficulty: " + sys.argv[2])
print("Return Port: " + sys.argv[3])
mine(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    
    