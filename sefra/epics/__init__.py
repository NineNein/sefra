from functools import wraps
import functools
import os
import pcaspy
from pcaspy import SimpleServer, Driver
os.environ['PYEPICS_LIBCA'] = os.path.join(os.path.dirname(pcaspy.__file__), "ca.dll")
# os.environ["PATH"] += os.pathsep + r"C:\Program Files\Python36\Lib\site-packages\epics\clibs\win64"
import epics 
import threading
import time


# os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '5000000000'  # This allocates lots of memory....
# MAX_SIZE = int(5000000000/8)



"""
Errors Problems and Stuff:
1. When server is freshly startet and a set function is called which returns a value, the value is 0. Maybe Solved?
2. If function called with return Value, .VAL value should set to None, incase of failure the return value wont be the old one
3. There might be some memory leaks due to saving data in the decorator classes...on should prob. save all in the class which has decorated functions
4. Long get is implemented as set but without arguments...
5. There are sections in this code which duplicates especialy when generating pv names but not only -> make it nicer
6. There are also some structural issues which can maybe make simpler, however there seems nothing which need the change of the interface
7. Missing some underlines e.g. driver  to avoid overwriting from the user side by mistage
8. There is a huge memory consumption when starting a EPCIS server ??? I do not why caused by EPICS_CA_MAX_ARRAY_BYTES
9. long get has some issues if returning an array...
"""

"""
Construct which automatic generate a client and server class
such the user needs only to write one class for a device

it just handle simple device, channel structure with single arugment function 

functions with arguments and with None as return Value, will return the last seted value
function without argument will return their return value

How to make the EPICS server? How to find all possible functions?
The server has to check if function exists?

There should be a possiblity to add custom function e.g. when one has to wait for an event
e.g. counter

"""

#https://stackoverflow.com/questions/5910703/how-to-get-all-methods-of-a-python-class-with-given-decorator
#https://stackoverflow.com/questions/48533781/python-register-class-methods-with-a-decorator-and-inheritance




class expose_function_handler:
    
    """
        This class is similar to functools.partial. 
        But it returns a callable class insteat of a function.
        Such that there can be exta function e.g. pv_name() etc.


        f: is the descriptor class instance of the decorator
        instance: is the instance of the class which has a decorated member function

    """

    def __init__(self, f, instance):
        self.instance = instance
        self.func = f

    def pv_name(me):
        """
            return the PV name of the decorated function
        """
        self = me.instance
        
        pv_name = self.name.upper() + ":" + str(me.func.f.__name__).upper()
        parent_name = self.name
        parent = self.parent
        while parent is not None:
            pv_name = parent.name.upper() + ":" + pv_name
            parent_name = parent.name
            parent = parent.parent

        return pv_name

    def set(me, value):
        self = me.instance
        if not self.server:
            print("Function only for server side")
            return

        pv_name = me.pv_name()

        while self.parent is not None:
            self = self.parent

        self.driver.setParam(pv_name, value)
        self.driver.updatePVs()

        

    def get(self):

        """
            execute a get() on the PV of the decorate function. e.g. get the last set value if it is a set function
        """

        if self.instance.server: #to avoid loops
            return None

        pv_name = self.pv_name()
        return epics.PV(pv_name).get()

    def add_callback(self, function):

        if self.instance.server: #to avoid loops
            return None

        """
            adds a callback to the pv of the decorated functions.
        """

        if "__pvs" not in self.func.__dict__:  #I guess there was a dict.function for that...
            self.func.__dict__["__pvs"] = {}
            pn = self.pv_name()

        self.func.__dict__["__pvs"][pn] = epics.PV(pn)
        self.func.__dict__["__pvs"][pn].add_callback(function)

    def __call__(self, *args, **kwargs):
        ret = self.func(*((self.instance,)+args), **kwargs)
        return ret

class expose_function:

    """
        Decorator descriptor class which handles the selection between server and client call
        This decorator assumes that it was combined with the tagable decorator
    """

    def __init__(self, f):
        self.f = f

    def __call__(me, self, *args, **kwargs):
        if not self.server:
            pv_name = self.name.upper() + ":" + str(me.f.__name__).upper()
            local_pv_name = pv_name
            parent_name = self.name
            parent = self.parent
            while parent is not None:
                pv_name = parent.name.upper() + ":" + pv_name
                parent_name = parent.name
                parent = parent.parent
            busy_name = parent_name.upper() + ":BUSY"

            pv = epics.PV(pv_name)
            if self.func_info[local_pv_name]["args"]["writeable"]:
                if self.func_info[local_pv_name]["args"].get("zero_args", False):
                    pv.put(0)
                else:
                    pv.put(*args)

            if self.func_info[local_pv_name]["args"].get("return_type", None) is not None:
                if self.func_info[local_pv_name]["args"].get("thread", False):
                    while epics.PV(busy_name).get() == 1:
                        time.sleep(0.02)

                return epics.PV(pv_name + ".VAL").get()

            return pv.get()
        else:
            return me.f(self, *args)

    def __get__(self, instance, owner=None):
        return expose_function_handler(self, instance)


# def expose_function(f):
#     @functools.wraps(f)
#     def wrapper(self, *args):
#         if not self.server:
#             pv_name = self.name.upper() + ":" + str(f.__name__).upper()
#             local_pv_name = pv_name
#             parent_name = self.name
#             parent = self.parent
#             while parent is not None:
#                 pv_name = parent.name.upper() + ":" + pv_name
#                 parent_name = parent.name
#                 parent = parent.parent
#             busy_name = parent_name.upper() + ":BUSY"

#             pv = epics.PV(pv_name)
#             if self.func_info[local_pv_name]["args"]["writeable"]:
#                 pv.put(*args)

#             if self.func_info[local_pv_name]["args"].get("return_type", None) is not None:
#                 if self.func_info[local_pv_name]["args"].get("thread", False):
#                     while epics.PV(busy_name).get() == 1:
#                         time.sleep(0.02)

#                 return epics.PV(pv_name + ".VAL").get()

#             return pv.get()
#         else:
#             return f(self, *args)
#     return wrapper


class TaggableType(type):
    """
        This class is needed to have a working tag decorator whith which one can 
        register member functions with arguments
    """
    
    def __init__(cls, name, bases, attrs):
        cls._tagged = []
        for name, method in attrs.items():
            if isinstance(method, property):
                method = method.fget
            if hasattr(method, 'tagged'):
                cls._tagged.append({
                    "name" : name,
                    "args" : method.tagged
                    })

def tag(*args, **kwargs): 
    """
        Tag decorator to register member functions of a class
    """
    def inner_tag(f):
        if isinstance(f, property):
            f.fget.tagged = kwargs #Instead of True decorator arguments...
        else:
            f.tagged = kwargs
        return f
    
    return inner_tag 


#There is a need of a type identification, e.g. Integer, Float, String, Array, Binary, ....
#If one can specifiy that, then one could also introduce bounds
#but the bounds should have a std but can be also be alterd during runtime

def pv_get(*args, **kwargs):
    """
        This decorator combines the tag an the expose function decorator and set some arguments
        according to the get in the name.
        This decorator should be used for function which returns a value and have no arguments.
    """
    def inner(func):
        return tag(readable = True, writeable = False,**kwargs)(expose_function(func))

    #All this is for long get, thread = True, its implemented as pv_set with extra paprameter zero args
    if kwargs.get("thread", False):
        if "type" in kwargs:
            kwargs["return_type"] = kwargs["type"]

        if "count" in kwargs:
            kwargs["return_count"] = kwargs["count"]

        kwargs["zero_args"] = True
            

    def thread_inner(func):
        return tag(readable = False, writeable = True,**kwargs)(expose_function(func))

    if kwargs.get("thread", False):
        return thread_inner
    else:
        return inner

def pv_set(*args, **kwargs):
    """
        This decorator combines the tag an the expose function decorator and set some arguments
        according to the set in the name.
        This decorator should be used for function which has arguments, if a return_type arguement is supplied,
        the function can also have a return value.
    """
    def inner(func):
        return tag(readable = False, writeable = True,**kwargs)(expose_function(func))
    return inner



# Maybe with argument, one should support mutltiple argument function
# Every Server will have a busy pv
# If a pv is called while busy it will put in quque 
# every PV will return an ID and if pv busy < id then the Pv was  not executet other it was executed <- no need since server handle not multiple request at same time


class epics_server(Driver):
    def __init__(self, infos, name):
        super(epics_server, self).__init__()
        self.infos = infos
        self.name = name

        self.pvs = {}
        for pv in infos:
            self.pvs[pv["name"]] = {"args" : pv["args"], "func" : pv["func"]}

        self.param_set_values = {}

        self.tid = None

    
    def read(self, reason):
        if reason in self.pvs:
            readable = self.pvs[reason]["args"].get("readable", False)
            if readable:
                value = self.pvs[reason]["func"]()
            else:
                value = self.getParam(reason)
        else:
            value = self.getParam(reason)
        return value


    def __run_write(self, reason, value):
        self.setParam(self.name.upper() + ':BUSY', 1)
        self.updatePVs()

        if self.pvs[reason]["args"].get("zero_args", False):
            ret = self.pvs[reason]["func"]()
        else:
            ret = self.pvs[reason]["func"](value)
        
        if ret is not None and self.pvs[reason]["args"].get("return_type", False):
            self.setParam(reason + ".VAL", ret)

        self.setParam(self.name.upper() + ':BUSY', 0)
        self.updatePVs()

    def write(self, reason, value):
        status = True
        if reason in self.pvs:
            writeable = self.pvs[reason]["args"].get("writeable", False)
            if writeable:
                if self.pvs[reason]["args"].get("thread", False):
                    self.tid = threading.Thread(target=self.__run_write,args=(reason, value))
                    self.tid.start()
                else:
                    self.__run_write(reason, value)

            else:
                status = False
        else:
            status = False
        # store the values
        if status:
            self.setParam(reason, value)
        return status



class device(metaclass=TaggableType):
    def __init__(self, name, parent=None, server=False):
        self.name = name
        self.parent = parent
        if parent is not None:
            self.server = parent.server
            parent.childs.append(self)
        else:
            self.server = server

        self.childs = []
        self.func_info = self.__func_info()

        self.driver = 0

    def _start(self):
        if not self.server or self.parent is not None:
            return

        prefix = ""
        pvdb = {
            self.name.upper() + ":BUSY" : {"type" : "int", "prec" : 1}
        }
        infos = self._info()
        for pv in infos:
            prec = pv["args"].get("prec", 5)
            
            
            pvdb[pv["name"]] = {
                'prec' : prec,
            }

            pvtype = pv["args"].get("type", None)
            if pvtype is not None:
                pvdb[pv["name"]]["type"] = pvtype

            if "scan" in pv["args"]:
                pvdb[pv["name"]]["scan"] = pv["args"]["scan"]

            if "count" in pv["args"]:
                pvdb[pv["name"]]["count"] = pv["args"]["count"]

            return_type = pv["args"].get("return_type", None)
            if return_type is not None:
                return_prec = pv["args"].get("return_prec", 5)
                pvdb[pv["name"] + ".VAL"] = {
                    'prec' : return_prec,
                    'type' : return_type
                }

                if "return_count" in pv["args"]:
                    pvdb[pv["name"] + ".VAL"]["count"] = pv["args"]["return_count"]

        server = SimpleServer()
        server.createPV(prefix, pvdb)
        self.driver = epics_server(infos, self.name)    

        # process CA transactions
        while True:
            server.process(0.2) #Is this the max time the server wait for a return?



    def loop(self):
        while True:
            time.sleep(1)

    def __func_info(self):
        tags = {}
        for t in type(self).__mro__:
            if hasattr(t, '_tagged'):
                names = [self.name.upper() + ":" + data["name"].upper() for data in list(t._tagged)]
                funcs = [getattr(self, data["name"]) for data in list(t._tagged)]
                args = [data["args"] for data in list(t._tagged)]

                for name, arg, func in zip(names, args, funcs):
                    tags[name] = {"args" : arg, "func" : func}

        return tags

    def _info(self):
        tags = []

        for child in self.childs:
            data = []
            for d in child._info():
                d["name"] = self.name.upper() + ":" + d["name"].upper()
                data.append(d)
            tags.extend(data)

        # Support multiple inheritance out of the box
        for t in type(self).__mro__:
            if hasattr(t, '_tagged'):
                names = [self.name.upper() + ":" + data["name"].upper() for data in list(t._tagged)]
                funcs = [getattr(self, data["name"]) for data in list(t._tagged)]
                args = [data["args"] for data in list(t._tagged)]

                data = [{"name" : name, "args" : arg, "func" : func} for name, arg, func in zip(names, args, funcs)]

                tags.extend(data)
        return tags

    def pv_names(self):
        tags = []

        for child in self.childs:
            data = []
            for d in child.pv_names():
                d = self.name.upper() + ":" + d.upper()
                data.append(d)
            tags.extend(data)

        # Support multiple inheritance out of the box
        for t in type(self).__mro__:
            if hasattr(t, '_tagged'):
                names = [self.name.upper() + ":" + data["name"].upper() for data in list(t._tagged)]
                data = [name for name in names]
                tags.extend(data)

        if self.parent is None:
            tags.append(self.name.upper() + ":BUSY")

        return tags
