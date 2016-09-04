
class ParamIsNull(Exception):
    
    def __init__(self, paramName):
        self.message = paramName  + " is null"
  
class TypeMismatch(Exception):
    def __init__(self, paramName, desiredType, readType):
        self.message = 'expected %s for param %s,but gived %s' % desiredType % paramName % readType
 
class InvalidateValue(Exception):
   def __init__(self, paramName, value, l):
      self.message = 'the value for ' + paramName  + ' not in ' + str(l)
      
class ParamChecker(object):
    
    @staticmethod
    def checkNotNull(**argv):
        for (pname, pvalue) in argv.items():
            if pvalue is None:
                raise ParamIsNull(pname)
                
    @staticmethod
    def checkIsInstance(t, **argv):
        for (pname, pvalue) in argv.items():
            if isinstance(pvalue, t):
                raise TypeMismatch(pname, t, type(pvalue))
    
    @staticmethod
    def checkIsIn(l, **argv):
        for (pname, pvalue) in argv.items():
            if pvalue not in l:
                raise InvalidateValue(pname, pvalue, l)
        
    @staticmethod
    def check(expr, exception):
        if not expr:
            raise exception

