import ProtoParser
import MessageSpec
import exceptions

try:
    m = MessageSpec.MessageSpecDict()
    p = ProtoParser.ProtoParser()
    p.parse(r'/home/shgli/src/webquant/gate/proto/thrift',m)
except exceptions.SyntaxError,e:
    print e.message

