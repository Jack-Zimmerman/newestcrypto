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

from subprocess import PIPE, Popen, CREATE_NEW_CONSOLE

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
    chain.getInfoFromFile()
    
    if not os.path.isfile("nodeinfo/nodes.dat"):
        with open("nodeinfo/nodes.dat", "w") as toWrite:
            toWrite.write('["192.168.68.79"]')
            
    nodes = ["192.168.68.79"]
    with open("nodeinfo/nodes.dat", "r") as toRead:
        nodes += json.loads(toRead.read())
    
    if "192.168.68.79" not in nodes:
        nodes.append("192.168.68.79")
    
    
    #find first available node
    for node in nodes:
        val = downloadFromNode(chain, node)
        if val == True:
            return
                    
def downloadFromNode(chain: Chain, node):
    result = ""    
    try:
        result = requests.get(f"http://{node}:{port}/test", timeout=1).text
    except:
        return 1
    
    #viable node
    if result == "alive":
        maxHeight = -1
        try:
            maxHeight = int(requests.get(f"http://{node}:{port}/getheight", timeout=1).text)
        except Exception as e:
            return 2


        requests.get(f"http://{node}:{port}/registerfuturenode")
        
        #go on to next node
        if maxHeight == -1:
            return 3
        else:
            #download everything
            
            if maxHeight <= chain.height:
                return 3.5
            
            while chain.height != maxHeight:
                blockChunk = min(maxHeight-chain.height, 100)
                request = f"http://{node}:{port}/multiblock?start={chain.height+1}&end={chain.height+blockChunk}"
                newBlocks = None
                try:
                    newBlocks = json.loads(urllib.parse.unquote(requests.get(request, timeout=1).text))
                except:
                    return 4
                
                for newBlock in newBlocks:
                    if not chain.verifyBlock(newBlock):
                        #remove blocks
                        for x in range(maxHeight-chain.height):
                            chain.popBlock()
                        return 5
                    else:
                        print(f"Downloaded Block {newBlock['height']}")
                        chain.addBlock(newBlock)

    else:
        return 6
                    
    #made it to the end
        
    chain.writeChainInfo()

    return True
                
                
                
                    
                
            
        
    
    
    






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
    
    global started
    started = False
    
    
     
    def do_GET(self) -> None:
        global transactionsPool
        global chain
        global started

        
        
        chain.getInfoFromFile()
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        if not started:
            self.startNode(localCall=True)

        total = self.path.split("?")
        
        
        self.queries = dict()
        if len(total) == 1:
            self.path = total[0]
        else:
            self.path = total[0]
            self.queries = dict(urllib.parse.parse_qsl(total[1]))
        
        #try and add this requester to node list
        if self.path != "/test":
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
            case "/registerfuturenode":
                self.registernode(future=True)
            case "/test":
                self.respond("alive")
            case "/getheight":
                self.respond(str(chain.height))
            case "/minersuccess":
                self.minerSuccess()
            case _:
                self.respond("unknown")
                
    def startNode(self, localCall=False):
        global nodes
        global transactionsPool
        global chain
        global nodes
        global miner
        global wallet
        global port
        global started
        

        if started ==True:
            return
        
        #only can be called by local
        if self.address_string() != "127.0.0.1" and not localCall:
            return
        
        
        #nodes are initalized from file
        if not os.path.isdir("nodeinfo"):
            os.mkdir("nodeinfo")
                
        if not os.path.isfile("nodeinfo/nodes.dat"):
            base = ["192.168.68.79"]
            with open("nodeinfo/nodes.dat", "w") as toWrite:
                toWrite.write(json.dumps(base))
        
        with open("nodeinfo/nodes.dat", "r") as toRead:
            nodes = json.loads(toRead.read())


        started = True
        for node in nodes:
            try:
                requests.get(f"http://{node}:{port}/registernode", timeout=1)
            except:
                pass
            
        
        #ask other nodes for transactions that have been missed
        transactionsPool = self.askForTransactions()
        chain = Chain()
        chain.initChain()
        chain.getInfoFromFile()
        
        #wallet name sent in, download from file or create new one
        wallet = Wallet(sys.argv[1])
        wallet.initWallet()
        
        #we're on genesis
        oldBlock = None
        if chain.height == -1:
            oldBlock = crypto.GENESIS_BASIS
        else:
            oldBlock = Chain.readBlock(chain.height)
            
        
        self.startMining(oldBlock)     


        self.respond("started")
    
    def startMining(self, oldBlock):
        global miner
        global port
        global transactionsPool
        global wallet
        global block
        
        if miner != None:
            miner.kill()
            
        
        block = Block(wallet.public, oldBlock)
        
        for transac in transactionsPool:
            block.addTransaction(transac)
        
        block.complete(wallet)
        
        requestArray = (f"python mine.py {block.headerInfo} {block.difficulty} {port}").split(" ")
        
        
        miner = Popen(requestArray, creationflags=CREATE_NEW_CONSOLE)
        
        
    #cant be access out of the host computer, localhost request only
    def minerSuccess(self):
        global miner
        global block
        global chain
        
        
        if block == None:
            return
        
        if self.address_string() != "127.0.0.1":
            self.respond("THIS ISNT LOCALHOST, ACCESS DENIED")
            return
        
        miner = None
        
        
        nonce = int(self.queries["nonce"])
        
        #if its a turd, start over
        if not headerHashAndCheck(block.headerInfo, nonce, block.difficulty):
            self.startMining(Chain.readBlock(chain.height))
            return
            
        block.solidify(nonce)
        
        broadcastBlock = block.__dict__
        block = None
        
        assert chain.verifyBlock(broadcastBlock)
        
        chain.addBlock(broadcastBlock)
        
        self.broadcastBlock(broadcastBlock)
        
        #start it all over again bruh
        
        self.startMining(broadcastBlock)
                        
        
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
        global chain
        start = int(self.queries["start"])
        end = int(self.queries["end"])
        
        
        #is end past current knowledge of chain
        if end > chain.height:
            self.respond("None")
            
            
        
        blocks = []
        
        for height in range(start, end+1):
            block = Chain.readBlock(height)
            
            assert block != None
        
            blocks.append(Chain.readBlock(height))
            
        self.respond(json.dumps(blocks))
        
    def newtransaction(self):
        global transactionsPool
        global chain
        
        transaction = urllib.parse.unquote(self.queries["transaction"])
        
        if chain.verifyIncomingTransaction(transaction) == True:
            transactionsPool.append(transaction)
            self.respond("accepted")
        else:
            self.respond("rejected")
            
    
    def getBackUpToSpeed(self, nodeIP, finalHeight):
        global chain
        
        request = f"http://{nodeIP}:3141/multiblock?start={chain.height+1}&end={finalHeight}"
        
        
        result = None
        try:
            result = json.loads(urllib.parse.unquote(requests.get(request, timeout=1).text))
        except:
            #failed ask
            return False
        
        #get as close to up to date as possible
        for relHeight, newBlock in enumerate(result):
            if chain.verifyBlock(newBlock) == True:
                chain.addBlock(newBlock)
            else:
                if relHeight != 0:
                    self.startMining(result[relHeight])
                return False
            
        return True
                
                
            
    
    def newblock(self):
        global chain
        global miner
        global started
 
        
        introducedBlock = json.loads(urllib.parse.unquote(self.queries["block"]))
        
        #if ahead of schedule
        if introducedBlock["height"] - chain.height > 1:
            #give it a chance by asking that node for more info
            print("Tried to get back up to speed, success: " + str(self.getBackUpToSpeed(self.address_string(), introducedBlock["height"]-1)))


        if introducedBlock["height"] <= chain.height:
            #request that other node try to get up to speed
            self.respond(f"adjust:{chain.height}")
        
        if chain.verifyBlock(introducedBlock) == True:
            #kill local miner
            if miner != None:
                miner.kill()
            
            #verify, add locally, reflect in payments
            chain.addBlock(introducedBlock)
            
            self.broadcastBlock(introducedBlock, exclusions=[self.address_string()])
            
            #broadcast to other nodes, but not the one that just sent it
            
            self.startMining(Chain.readBlock(chain.height))
            
            #start process of mining
            
            
            self.respond("accepted")
        else:
            self.respond("rejected")
            
        
            
            
    def testNode(self):
        global port
        
        url = f"http://{self.address_string()}:{port}/test"
        
        
        try:
            result = requests.get(url, timeout=1).text
        except:
            return "not_alive"
        
        
        return result
    
    

    def registernode(self, future=False):
        global nodes
        global port
        
        if nodes == None:
            if not os.path.isfile("nodeinfo/nodes.dat"):
                nodes = ["192.168.68.79"]
                nodes.append(self.address_string())
                with open("nodeinfo/nodes.dat", "w") as toWrite:
                    toWrite.write(json.dumps(nodes))
            else:
                with open("nodeinfo/nodes.dat", "r") as toRead:
                    nodes = json.loads(toRead.read())
        else:
            with open("nodeinfo/nodes.dat", "r") as toRead:
                nodes.append(self.address_string())
                nodes = json.loads(toRead.read())
                
        
        nodeIP = self.address_string()
        
        #not adding ourselfs lmao
        if nodeIP == "127.0.0.1":
            return 
        
        #testing to see if node is alive
        
        response = "alive"
        if future != False:
            response = self.testNode()
        
        
        #if isnt running correct node program, dont register
        if response != "alive": 
            return
        else:
            #if unique add, else dont
            if not nodeIP in nodes:
                nodes.append(nodeIP)
                
                with open("nodeinfo/nodes.dat", "w") as toWrite:
                    toWrite.write(json.dumps(nodes))
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
                result = json.loads(urllib.parse.unquote(requests.get(request, timeout=1).text))
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
                result = requests.get(requestString, timeout=1).text
                
                if result.startswith("adjust"):
                    neededHeight = int(result.split(":")[1])
                    
                    self.getBackUpToSpeed(node, neededHeight)
                    
                print(f"Block height {introducedBlock['height']} {result} by node at {node} ")
            except:
                return
            
            

chain = Chain()
chain.dumpChain()
chain.initChain()


getChainUpToDate(chain)


        
            

        
#server = ThreadingSimpleServer(("0.0.0.0", PORT), NodeHTTP)

    
    
def run(server_class=HTTPServer, handler_class=NodeHTTP, port=3141, CWD=None, HOST=None):
    server_address = ("0.0.0.0", port)
    
    server  = server_class(server_address, handler_class)
    
    print("Serving HTTP traffic from", CWD, "on", HOST, "using port", port)


    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server per users request.")
        sys.exit()
            

    
run(CWD=CWD, HOST=HOST)
    
    
    
