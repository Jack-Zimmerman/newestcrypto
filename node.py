#!/usr/bin/env python3
import sys, os, socket
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse 
from urllib import request



from block import *
from crypto import hashHeader
from transaction import *
from chain import *
from wallet import *
import requests
import random

import time
import types

HOST = socket.gethostname()

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

'''
This sets the listening port, default port 8080
'''
PORT = int(sys.argv[1])

'''
This sets the working directory of the HTTPServer, defaults to directory where script is executed.
'''
CWD = os.getcwd()
    
    








    
    






class NodeHTTP(SimpleHTTPRequestHandler):        
    def do_GET(self) -> None:
        self.chain = Chain()
        self.chain.getInfoFromFile()
        
        
        self.transactionsPool = []
        self.nodes = []
        
        self.initNodeInfo()
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        }

        
        total = self.path.split("?")
        
        if len(total) == 1:
            self.path = total[0]
        else:
            self.path = total[0]
            self.queries = dict(urllib.parse.parse_qsl(total[1]))
        
        
        print(self.address_string())
        
        match self.path:
            case "/block":
                self.block()
            case "/multiblock":
                self.multiblock()
            case "/newtransaction":
                self.newtransaction()
            case "/newblock":
                self.newblock()
            case "/registernode":
                self.registernode()
            case "/test":
                self.respond("alive")
            case _:
                self.respond("unknown")
                
    
    def initNodeInfo(self):
        if not os.path.isdir("nodeinfo"):
            os.mkdir("nodeinfo")
            
        if not os.path.isfile("nodes"):
            base = []
            with open("nodeinfo/nodes", "w") as toWrite:
                toWrite.write(json.dumps(base))
        
        with open("nodeinfo/nodes", "r") as toRead:
            self.nodes = json.loads(toRead.read())

            
        
        
        
                
                
        
    def respond(self, response):
        assert isinstance(response, str)
        
        response = urllib.parse.quote(response)

        self.wfile.write(bytes(response, "utf-8"))
                
    
    def block(self):
        height = int(self.queries["height"]) 
        
        result = Chain.readBlock(height)
        
        if result == None:
            self.respond("None")
        else:
            self.respond(json.dumps(result))
                
        
    
    def multiblock(self):
        start = int(self.queries["start"])
        end = int(self.queries["end"])
        
        
        #is end past current knowledge of chain
        if end > self.chain.height:
            self.respond("None")
            
            
        
        blocks = []
        
        for height in range(start, end+1):
            block = Chain.readBlock(height)
            
            assert block != None
        
            blocks.append(Chain.readBlock(height))
            
        self.respond(json.dumps(blocks))
        
    def newtransaction(self):
        transaction = urllib.parse.unquote(self.queries["transaction"])
        
        if self.chain.verifyIncomingTransaction(transaction) == True:
            self.transactionsPool.append(transaction)
            self.respond("accepted")
        else:
            self.respond("rejected")
            
    
    def newblock(self):
        block = urllib.parse.unquote(self.queries["block"])
        
        if self.chain.verifyBlock(block) == True:
            self.chain.fufillVerifiedBlockTransactions(block)
            self.chain.addBlock(block)
            self.respond("accepted")
        else:
            self.respond("rejected")
            
            
    def testNode(self, nodeIP):
        print(self.address_string())
        url = f"http://example.com"
        print(url)
        
        
        result = request.urlopen(url)
        
        
        return result
    
    

    def registernode(self):
        nodeIP = self.address_string()
        
        print(nodeIP)
        
        #testing to see if node is alive
        
        response = self.testNode(nodeIP)
        
        print("hello")
        
        if response != "alive":
            self.respond("nope")
            return
        else:
            self.nodes.append(nodeIP)
            
            with open("nodeinfo/nodes", "w") as toWrite:
                toWrite.write(json.dumps(self.nodes))

            


                
        
        
        
            
        
        
    
            

        
        
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

lol.writeChainInfo()



server = ThreadingSimpleServer((sys.argv[2], PORT), NodeHTTP)
print("Serving HTTP traffic from", CWD, "on", HOST, "using port", PORT)


requests.get("http://192.168.68.64:8080/registernode")
    
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server per users request.")
    sys.exit()
    
    
    
    
