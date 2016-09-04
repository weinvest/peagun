from thrift.Thrift import TType
from TypeSpec import TypeSpec


class TypeDispatcher(object):
    def __init__(self, prefix):
        self.__prefix = prefix

    def __unknown(self, typeSpec, *vargst, **vargdic):
        print('TypeDispatcher can not find handle for %s' % typeSpec.getTypeName())

    def dispatch(self, spec, *vargst, **vargdic):
        if spec is None or not isinstance(spec, TypeSpec):
            raise TypeError('first argument of TypeDispatcher.dispatch should be a TypeSpec')
        else:
            handle = getattr(self, '%s%s' % (self.__prefix, spec.getTypeName()), self.__unknown)
            return handle(spec, *vargst, **vargdic)



