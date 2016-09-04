#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
from twisted.internet import reactor
from MessageHandler import Factory
from PeagunCmd import Peagun
from PeaView import PeaView

def runCommandLine(pea):
    pea.cmdloop()
    reactor.callFromThread(reactor.stop)

def generateProto(protoPathList):
    #generate py source
    for p in protoPathList:
        files = os.listdir(p)
        for f in files:
            stem,ext = os.path.splitext(f)
            if ext == '.thrift':
                subprocess.call(['thrift','-gen','py','-o',metaPath,os.path.join(p,f)],stdout=sys.stdout,stderr=sys.stderr)

if __name__ == '__main__':
    scriptPath,peagunName = os.path.split(os.path.abspath(sys.argv[0]))
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(scriptPath)),'pyquant'))
    print scriptPath

    parser = argparse.ArgumentParser(prog=peagunName
        ,description = " may in two mode: client and server,it' very useful when building prototype or testing.")
    modeGroup = parser.add_mutually_exclusive_group(required=True)
    modeGroup.add_argument('-l','--listen',dest='isClient',action='store_false',help='server mode')
    modeGroup.add_argument('-c','--connect',dest='isClient',action='store_true',help='client mode')

    parser.add_argument('-H','--host',default='localhost')
    parser.add_argument('-P','--port',type=int,required=True)

    parser.add_argument('-p','--plugin'
                        ,help='path(wildcard) to the plugin files which will be used as messages handle.')
    parser.add_argument('-r','--protos'
                        ,required=True
                        ,action='append'
                        ,help='directory list which containing protocol files'
    )
    parser.add_argument('-d','--daemon',type=bool,default=False)
    args = parser.parse_args()

    metaPath = '/tmp'
    generateProto(args.protos)
    sys.path.append(metaPath + '/gen-py')
    if args.daemon:
        pea = PeaView(args.protos,metaPath,Factory.createMessageHandle(args.plugin))
        if args.isClient:
            pea.connectionManager.connect(args.host,args.port)
        else:
            from twisted.internet.endpoints import serverFromString
            serverFromString(reactor,'tcp:interface=%s:port=%d' % (args.host,args.port)).listen(pea.connectionManager)
    else:
        pea = Peagun(args.protos,metaPath,Factory.createMessageHandle(args.plugin))
        if args.isClient:
            pea.cmdqueue.append('connect %s %d' % (args.host,args.port))
        else:
            pea.cmdqueue.append('listen tcp:interface=%s:port=%d' % (args.host,args.port))

        reactor.callInThread(runCommandLine,pea)
    reactor.run()
