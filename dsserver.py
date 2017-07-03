#main entry to the ISSServer
'''

  Copyright (c) 2017, Turku University.
  All rights reserved.
 
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. Neither the name of the Institute nor the names of its contributors
     may be used to endorse or promote products derived from this software
     without specific prior written permission.
 
  THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
  OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
  OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
  SUCH DAMAGE.
 
  This file is part of the IoT Semantic Script Server.
 
  Author: Behailu S. Negash <behneg@utu.fi>
  
'''
import os
import sys
from enum import Enum
from abc import ABCMeta, abstractmethod
import time
from rdfhandler import NameResolver 
#from nrf24 import NRF24
class NetworkInterface:
    __metaclass__=ABCMeta
    @abstractmethod
    def __init__(self,code,name,datarate,confirmed=False):
        pass

    @abstractmethod
    def begin(self): pass

    @abstractmethod
    def start_listening(self): pass

    @abstractmethod
    def message_available(self):pass

    @abstractmethod
    def stop_listening(self): pass

    @abstractmethod
    def send(self, destination, data): pass

    @abstractmethod
    def receive(self):pass

    @abstractmethod
    def reply(self):pass

class NrfInterface(NetworkInterface):
    def __init__(self,code,name,datarate,confirmed=False):
        self.code = code
        self.name = name
        self.datarate = datarate
        self.confirmed = confirmed
        self.pipes = [[0xA2,0xA2,0xA2,0xA2,0xA2],[0x20,0x20,0x20,0x20,0x20]]
        self.source = ''
    def begin(self):
        #begin nrf module and initialize
        print('begun the interface')
        '''self.radio = NRF()
        self.radio.begin(0, 0, 7, 8)
        self.radio.setPayloadSize(32)
        self.radio.setChannel(0x60)
        self.radio.setDataRate(NRF24.BR_250KBPS)
        self.radio.setPALevel(NRF24.PA_MAX)
        self.radio.openWritingPipe(self.pipes[1])
        self.radio.openReadingPipe(self.pipes[0])
        '''
    def start_listening(self):
        print('started listeing')
        #self.radio.startListening()

    def stop_listening(self):
        print('stoped listeing')
        #self.radio.stopListening()

    def message_available(self):
        return True
        #lp = [0]
        #return self.radio.available(lp,False)
        
    def send(self, destination, data):
        print('message sent')
        #send the data, stop listening and write
        #self.radio.write(data)

    def receive(self):
        print('received message')        
        #rcvd = bytearray(self.datarate)
        #self.radio.read(rcvd)
        #return rcvd
        #start listening and if radio.available return the data read
        return [0x00,0x00, 0x53 , 0x61 , 0x6d , 0x70 , 0x6c , 0x65 , 0x57 , 0x65 , 0x61 , 0x72]

    def reply(self,data):
        #self.radio.write(data)
        if(isinstance(data,Response)):
            print(data.responseCode)
            print(data.checksum)
            print(data.remains)
            print(data.body)
        
        

#Network communication handler
class TransportHandler:
    def __init__(self,ifobject):
        self.interface = ifobject


#Custome response code for requests
class ResponseCode(Enum):
    Continue = 100
    OK       = 200
    Created  = 201
    Accepted = 202

    BadRequest = 40
    Forbidden  = 43
    NotFound   = 44
    RequestTimeout    = 48

    #others will be added when needed

''' Request format
    +---------------------------------------------------------------+
    |0      1       2       3       4       5       6       7       |
    |_______________________________________________________________|
0   | Version                      |      Verb     | Accept | Notify|
    |_______________________________________________________________|
1   |                 Payload size (0 for GET)                      |
    |_______________________________________________________________|
2   |                  resource url (l bytes)                       |
    |_______________________________________________________________|
2+l |                           body                                |
n   |_______________________________________________________________|
'''

#requestFormat
class Request:
    def __init__(self,blob):
        self.content = blob
        self.tryBuild()

    def tryBuild(self):
        self.verb = self.getMethod()
        self.version = self.getVersion()
        self.accept = self.getAccept()
        self.subscribe = self.getSubscribe()
        self.bodyLength = self.getLength()
        self.resourceUrl = self.getResourceUrl()
        self.body = self.getBody()
        
    def getVersion(self):
        fstbyte = self.content[0]
        return ((fstbyte & 0xF0) >> 4)

    def getMethod(self):
        fstbyte = self.content[0]
        return ((fstbyte & 0x0C) >> 2)

    def getAccept(self):
        fstbyte = self.content[0]
        return ((fstbyte & 0x02) >> 1)

    def getSubscribe(self):#Same as notify
        fstbyte = self.content[0]
        return (fstbyte & 0x01)
        
    def getLength(self):
        scndbyte = self.content[1]
        return scndbyte

    def getResourceUrl(self):
        if self.bodyLength == 0:
            return (''.join(map(chr,self.content[2:])))
        else:
            tl = len(self.content)
            return (''.join(map(chr,self.content[2:tl-self.bodyLength])))
        
    def getBody(self):
        if self.bodyLength == 0:
                return ''
        else:
            tl = len(self.content)
            return (''.join(map(chr,self.content[tl-self.bodyLength:])))

''' Response format
    +---------------------------------------------------------------+
    |0      1      2       3       4       5       6       7        |
    |_______________________________________________________________|
0   |                   Response Code                               |
    |_______________________________________________________________|
1   |                  Remaining packets                            |
    |_______________________________________________________________|
2   |                   Checksum                                    |
    |_______________________________________________________________|
3   |                  body of response                             | 
n   |_______________________________________________________________|
'''
#response format
class Response:
    def __init__(self,blob,trail):
        self.content = blob
        self.remains = trail
        self.tryBuild()
    def tryBuild(self):
        self.responseCode = self.getCode()
        self.body = self.content[1:]
        self.checksum = self.getChecksum()

    def getCode(self):
        if len(self.content) > 0:
            return self.content[0]
        else:
            return ResponseCode.Forbidden

    def getChecksum(self):
        return '%2x'%(-(sum(c for c in self.body[0])%256) & 0xFF)

    def getRaw(self):
        buff=[self.responseCode,self.remains,self.checksum,self.body]
        return buff
        

#Request handler for dss server
class RequestHandler:
    def __init__(self,version,storePath,rdfpath):
        self.version = version
        self.storePath = storePath
        self.resourceTree()
        self.resolver = NameResolver(rdfpath)#make it configurable
        self.resolver.begin()
    
    def checkVersion(self,request):
        return self.version == request.version
        

    def handleGet(self,request,transport):
        if self.checkVersion(request):
            fpath = self.getResource(request.resourceUrl)            
            if fpath == '':
                blob = [ResponseCode.NotFound,'']
                resp = Response(blob,0)
                transport.interface.reply(resp)
            else:            
                tsz = os.path.getsize(fpath)
                step = transport.interface.datarate
                count = 0
                f = open(fpath,'rb')
                while count < tsz:
                    count+=step
                    buff = f.read(step)
                    if count < tsz:
                        blob = [ResponseCode.Continue,buff]
                        resp = Response(blob,tsz-count)
                        transport.interface.reply(resp)
                    else:
                        blob = [ResponseCode.OK,buff]
                        resp = Response(blob,0)
                        transport.interface.reply(resp)
        else:
            blob = [ResponseCode.BadRequest,'']
            resp = Response(blob,0)
            transport.interface.reply(resp)

    def handlePost(self,request,transport):
        if self.checkVersion():
            found = False
            if not found:
                blob = [ResponseCode.NotFound,'']
                resp = Response(blob,0)
                transport.interface.reply(resp)
        
        else:
            blob = [ResponseCode.BadRequest,'']
            resp = Response(blob,0)
            transport.interface.reply(resp)        

    def handleNotify(self,request,transport):
        if self.checkVersion():
            found = False
            if not found:
                blob = [ResponseCode.NotFound,'']
                resp = Response(blob,0)
                transport.interface.reply(resp)

        else:
            blob = [ResponseCode.BadRequest,'']
            resp = Response(blob,0)
            transport.interface.reply(resp)            

    def resourceTree(self):
        self.resources = os.walk(self.storePath,topdown=True)
    
    def getResource(self,name):
        fpath = ''
        fpath = self.resolver.Resolve(name)
        return self.storePath+fpath          
                    

#sample path /dss/shared/sample

if __name__=="__main__":
    '''
    Here is the flow of events:
        Start listening -> request arrives -> initialize(request)-> pass to requestHandle -> build a response -> reply response
    '''
    #DO INITIALIZATION HERE FIRST
    interface = NrfInterface('NRF','Nrf24',26,False) #Initialize a network interface to use
    interface.begin()
    transport = TransportHandler(interface) # create a shared communication handler
    handle = RequestHandler(0,'dss','iot-lite.rdf') #protocol handler
    
    while True:
        #start listening on the interface of the transport handler
        transport.interface.start_listening()
        if transport.interface.message_available(): # if there is a message
            transport.interface.stop_listening()
            buffr = transport.interface.receive() #get the message and build a request object
            request = Request(buffr) #Get request for 'sample.dsil'
            print(request.resourceUrl)            
            if(request.verb == 0 and request.subscribe == 0): #GET AND FALSE
                handle.handleGet(request,transport)
            elif(request.verb == 1):
                handle.handlePost(request,transport)
            elif(request.verb == 0 and request.subscribe == 1): #GET AND TRUE
                handle.handleNotify(request,transport)
        
        #transport.interface.send('source',response)