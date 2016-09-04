
class WSignal(object):
    def __init__(self):
        self.__observers = []

    def connect(self,f):
        self.__observers.append(f)

    def disconnect(self,f):
        self.__observers.remove(f)

    def __call__(self,*vargst, **vargdic):
        map(lambda f : f(*vargst, **vargdic),self.__observers)
