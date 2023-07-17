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

from subprocess import PIPE, Popen

import time
import types

HOST = socket.gethostname()

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

PORT = 8080
CWD = os.getcwd()
    
    








    
    






class NodeHTTP(SimpleHTTPRequestHandler): 
    global value    
    value = 0
    
    global transactionsPool
    transactionsPool = []
    
    global miner
    miner = None
     
    def do_GET(self) -> None:
        global value 
        global transactionsPool

        self.chain = Chain()
        self.chain.getInfoFromFile()
        
        self.nodes = []
        
        self.initNodeInfo()
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        

        total = self.path.split("?")
        
        if len(total) == 1:
            self.path = total[0]
        else:
            self.path = total[0]
            self.queries = dict(urllib.parse.parse_qsl(total[1]))
        
        
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
            case "/minersuccess":
                print(self.address_string())
            case "/startmining":
                print(self.address_string())
                self.startMining()
                self.respond("Started mining lol, but this process is threaded so have fun or something")
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

            
    
    def startMining(self):
        global miner
        miner = Popen("start python mine.py 313638393535333938335b7b2273656e646572223a202230303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030222c202274696d657374616d70223a20313638393535333938332c20226f757470757473223a205b7b227265636965766572223a2022303264613462333039363933376139396465633634303431383936343837303666636434333337303863303535383239643965363138666362313063363231323035222c2022616d6f756e74223a203130303030303030307d5d2c20226e6f6e6365223a203736372c20227369676e6174757265223a20223832306466316161623432336365303233323063303033383133303736313731336330386435633938326530616638356661376233343939363135343831323865663737653765383832623638303935656462363961313335316461396639323566376330623163326535323934303830656237613939336466623163306338222c20226e6f7465223a2022222c202268617368223a202266616339643063396538333337343034313331373830373131386533623835326338306431343463643139363234356533653639373736343665373139376263227d5d30 10000000 8080", shell=True, stdin=PIPE, stderr=PIPE, stdout=PIPE)
        
        
    def minerSuccess(self):
        global miner
        miner = None
        
        #first check to see if block already exists, then go back to doing ur thing
        
        
                
                
        
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
        block = urllib.parse.unquote(self.queries["block"])
        
        if self.chain.verifyBlock(block) == True:
            self.chain.fufillVerifiedBlockTransactions(block)
            self.chain.addBlock(block)
            self.respond("accepted")
        else:
            self.respond("rejected")
            
            
    def testNode(self):
        url = f"http://{self.address_string()}:8080/test"
        
        
        result = requests.get(url, timeout=1).text
        
        
        return result
    
    

    def registernode(self):
        nodeIP = self.address_string()
        
        #testing to see if node is alive
        
        response = self.testNode()
        
        if response != "alive":
            self.respond("nope")
            return
        else:
            self.nodes.append(nodeIP)
            
            with open("nodeinfo/nodes", "w") as toWrite:
                toWrite.write(json.dumps(self.nodes))

        
#server = ThreadingSimpleServer(("0.0.0.0", PORT), NodeHTTP)

    
    
def run(server_class=ThreadingSimpleServer, handler_class=NodeHTTP, port=8080, CWD=None, HOST=None):
    server_address = ("", port)
    
    server  = server_class(server_address, handler_class)
    
    print("Serving HTTP traffic from", CWD, "on", HOST, "using port", PORT)


    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server per users request.")
        sys.exit()
            

    
run(CWD=CWD, HOST=HOST)
    
    
    
