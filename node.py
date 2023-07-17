#!/usr/bin/env python3
import sys, os, socket
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse 
from urllib import request



from block import *
import crypto
from transaction import *
from chain import *
from wallet import *
import requests
import random

from subprocess import PIPE, Popen

import time
import types

HOST = socket.gethostname()

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

port = 3141
CWD = os.getcwd()
    
    


#for now, only works when blockchain is small(it always will be nobody will use this)
def getChainUpToDate(chain: Chain):
    global port
    
    chain.initChain()
    
    nodes = []
    with open("nodeinfo/nodes", "r") as toRead:
        nodes = json.loads(toRead.read())
    
    
    
    #find first available node
    for node in nodes:
        downloadFromNode(chain, node)
                    
def downloadFromNode(chain: Chain, node):
    
    #not going to add to chain unless all blocks are verified
    tempAdditions = []
    
    
    result = ""    
    try:
        result = requests.get(f"http://{node}:{port}/test", timeout=1)
    except:
        return False
    
    #viable node
    if result == "alive":
        maxHeight = -1
        try:
            maxHeight = int(requests.get(f"http://{node}:{port}/getheight", timeout=1))
        except:
            return False
        
        #go on to next node
        if maxHeight == -1:
            return False
        else:
            #download everything
            blockHeight = chain.height + 1
            while blockHeight <= maxHeight:
                request = f"http://{node}:{port}/block?height={blockHeight}"
                newBlock = None
                try:
                    newBlock = requests.get(request, timeout=5)
                except:
                    return False
                
                if not chain.verifyBlock(block):
                    return False
                else:
                    tempAdditions.append(block)
                    
    #made it to the end
    
    for block in tempAdditions:
        chain.addBlock(block)
        
    chain.writeChainInfo()
                
                
                
                    
                
            
        
    
    
    






class NodeHTTP(SimpleHTTPRequestHandler): 
    global port
    port = 3141
    
    global transactionsPool
    transactionsPool = None
    
    global block 
    block = None
    
    global chain
    chain = None
    
    global nodes
    nodes = None

    global miner
    miner = None 
    
    global wallet 
    wallet = None
    
    
     
    def do_GET(self) -> None:
        global transactionsPool
        global chain

        chain.getInfoFromFile()
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        

        total = self.path.split("?")
        
        
        self.queries = dict()
        if len(total) == 1:
            self.path = total[0]
        else:
            self.path = total[0]
            self.queries = dict(urllib.parse.parse_qsl(total[1]))
        
        #try and add this requester to node list
        self.registernode()
        
        match self.path:
            case "/startnode":
                self.startNode()
            case "/block":
                self.getBlock()
            case "/multiblock":
                self.multiblock()
            case "/newtransaction":
                self.newtransaction()
            case "/newblock":
                self.newblock()
            case "/sharetransactions":
                self.shareTransactions()
            case "/registernode":
                self.registernode()
            case "/test":
                self.respond("alive")
            case "/getheight":
                self.respond(chain.height)
            case "/minersuccess":
                self.minerSuccess()
            case _:
                self.respond("unknown")
                
    def startNode(self):
        global nodes
        global transactionsPool
        global chain
        global nodes
        global miner
        global wallet
        
        
        #only can be called by local
        if self.address_string() != "127.0.0.1":
            return
        
        
        #nodes are initalized from file
        if not os.path.isdir("nodeinfo"):
                os.mkdir("nodeinfo")
                
        if not os.path.isfile("nodes"):
            base = []
            with open("nodeinfo/nodes", "w") as toWrite:
                toWrite.write(json.dumps(base))
        
        with open("nodeinfo/nodes", "r") as toRead:
            nodes = list(set(json.loads(toRead.read())))
            
        
        #ask other nodes for transactions that have been missed
        transactionsPool = self.askForTransactions()
        chain = Chain()
        chain.initChain()
        
        #wallet name sent in, download from file or create new one
        wallet = Wallet(urllib.parse.unquote(self.queries["wallet"]))
        wallet.initWallet()
        
        #we're on genesis
        if chain.height == -1:
            oldBlock = crypto.GENESIS_BASIS
            
            self.startMining(oldBlock)
        else:
            oldBlock = Chain.readBlock(chain.height)
            
            self.startMining(oldBlock)     
        
        self.respond("started!")
    
    def startMining(self, oldBlock):
        global miner
        global port
        global transactionsPool
        global wallet
        global block
        
        block = Block(wallet.public, oldBlock)
        
        for transac in set(transactionsPool):
            block.addTransaction(transac)
        
        block.complete(wallet)
        
        requestString = f"start python mine.py {block.headerInfo} {block.difficulty} {port}"
        miner = Popen(requestString, shell=True)
        
        
    #cant be access out of the host computer, localhost request only
    def minerSuccess(self):
        global miner
        global block
        global chain
        
        if self.address_string() != "127.0.0.1":
            self.respond("THIS ISNT LOCALHOST, ACCESS DENIED")
            return
        
        miner = None
        
        nonce = int(self.queries["nonce"])
        block.solidify(nonce)
        
        block = block.__dict__
        
        assert chain.verifyBlock(block)
        chain.addBlock(block)
        
        self.broadcastBlock(block)
        
        #start it all over again bruh
        
        self.startMining(block)
        
        
                
                
        
    def respond(self, response):
        assert isinstance(response, str)
        
        response = urllib.parse.quote(response)

        self.wfile.write(bytes(response, "utf-8"))
                
    
    def getBlock(self):
        height = int(self.queries["height"]) 
        
        result = Chain.readBlock(height)
        
        if result == None:
            self.respond("None")
        else:
            self.respond(json.dumps(result))
                
        
    
    #start and end inclusive
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
        global transactionsPool
        
        transaction = urllib.parse.unquote(self.queries["transaction"])
        
        if self.chain.verifyIncomingTransaction(transaction) == True:
            transactionsPool.append(transaction)
            self.respond("accepted")
        else:
            self.respond("rejected")
            
    
    def newblock(self):
        global chain
        global miner
        
        introducedBlock = urllib.parse.unquote(self.queries["block"])
        
        
        if chain.verifyBlock(introducedBlock) == True:
            #kill local miner
            miner.kill()
            
            #verify, add locally
            chain.fufillVerifiedBlockTransactions(introducedBlock)
            chain.addBlock(introducedBlock)
            
            #broadcast to other nodes, but not the one that just sent it
            self.broadcastBlock(introducedBlock, exclusions=[self.address_string()])
            
            #start process of mining
            self.startMining()
            
            self.respond("accepted")
        else:
            self.respond("rejected")
            
            
    def testNode(self):
        global PORT
        
        url = f"http://{self.address_string()}:{PORT}/test"
        
        
        try:
            result = requests.get(url, timeout=1).text
        except:
            return "not_alive"
        
        
        return result
    
    

    def registernode(self):
        global nodes
        global port
        
        
        nodeIP = self.address_string()
        
        #not adding ourselfs lmao
        if nodeIP == "127.0.0.1":
            return 
        
        #testing to see if node is alive
        
        response = self.testNode()
        
        #if isnt running correct node program, dont register
        if response != "alive":
            self.respond("nope")
            return
        else:
            #if unique add, else dont
            if not nodeIP in nodes:
                nodes.add(nodeIP)
                
                with open("nodeinfo/nodes", "w") as toWrite:
                    toWrite.write(json.dumps(self.nodes))
            else:
                return 
            
    def shareTransactions(self):
        global transactionsPool
        
        self.respond(json.dumps(transactionsPool))
        
    def askForTransactions(self):
        global port
        global nodes
        global chain
        
        #ongoing is all known verified transactions
        ongoing = []
        
        for node in nodes:
            request = f"http://{node}:{port}/sharetransactions"
            
            result = []
            try:
                result = requests.get(request, timeout=1).json()
            except:
                pass
            
            #too large dude
            if len(result) > 100:
                continue
            
            allVerified = True
            for transac in result:
                #if duplicate
                if result.count(transac) != 1:
                    allVerified = False
                    break
                
                if chain.verifyIncomingTransaction(transac) == False:
                    allVerified = False
                    break
                
            #strive for longest list
            if allVerified:
                if len(result) > len(ongoing):
                    ongoing = result
                
        return ongoing
    
        
                    
                
    def broadcastBlock(self, introducedBlock, exclusions=[]):
        #make it url safe
        stringBlock = urllib.parse.quote(json.dumps(introducedBlock))
        
        for node in nodes:
            if node in exclusions:
                continue
            
            requestString = f"http://{node}:{port}/newblock?block={stringBlock}"
            
            try:
                requests.get(requestString, timeout=5)
                print(f"Block height {introducedBlock['height']} accepted by node at {node} ")
            except:
                return
            
            

chain = Chain()
chain.dumpChain()

getChainUpToDate(chain)


        
            

        
#server = ThreadingSimpleServer(("0.0.0.0", PORT), NodeHTTP)

    
    
def run(server_class=ThreadingSimpleServer, handler_class=NodeHTTP, port=3141, CWD=None, HOST=None):
    server_address = ("0.0.0.0", port)
    
    server  = server_class(server_address, handler_class)
    
    print("Serving HTTP traffic from", CWD, "on", HOST, "using port", port)


    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server per users request.")
        sys.exit()
            

    
run(CWD=CWD, HOST=HOST)
    
    
    
