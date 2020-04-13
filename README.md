# sefra
Tool to build and call epics server


Every function needs a instance before starting the server, otherwise the PV is not created. E.g.
Do not create channels at arbitary time, do it in the __init__ before starting the server. 
Otherwise the channels are not listed in the the server pv list. There is currently no feature that can update that list.


## Getting started

To get started, open a terminal and navigate to the package directory (this is where the setup.py file lives). Once you're there, type:

```python
python setup.py develop
```

In the following a simple example is provided. A more complex example, with channels is provided in the example.py file.

Server Example, example.py:
```python
import sefra
import time
import random
class example_device(sefra.epics.device): #We have to set the parent class
    def __init__(self, name, server=False):
        super(example_device, self).__init__(name, server=server)

    #Its a get function, this means without argument but with return value, in this case the return
    #value is of type float and its an array which max. count will be 100
    @sefra.epics.pv_get(type="float", count=100)    
    def get_array(self):
        ret = [random.randint(1,40) for i in range(50)]
        return ret

    #Its a set function, this means with an argument and with possible return value, in this case the return
    #value is of type string and the argument of type float. 
    #We expect that this function call is longer than the timeout, thus we use thread=True
    @sefra.epics.pv_set(type="float", return_type = "string", thread = True)
    def long_calculation(self, value):
        time.sleep(2)
        ret = [random.randint(1,40) for i in range(50)]
        self.get_array.set(ret) #This demonstrate how to set a PV value from another function
        return "This is the result: " + str(value * 10)

if __name__ == "__main__":

    ed = example_device("MY:PV:NAME", server=True) #Here we define the prefix of this class and let sefra know that this instance should be a server
    ed.start() #with start we start the server
```

Client Example:
```python
import example as ex 

#This function is used in the callback
def onChanges(pvname=None, value=None, char_value=None, **kw):
    print('PV Changed! ', pvname, char_value, time.ctime())

ed = ex.example_device("MY:PV:NAME") #Here we just put the PV prefix name of the server
print(ed.pv_names()) #We can let us show all PVs available in the server

ret = ed.get_array() #We can call the get array function
print("get_array", ret)
ed.get_array.add_callback(onChanges) #This is a way to add a callback function to a PV

ret = ed.long_calculation(123) #Here we call a long calculation, this is blocking till the result is present
print("long_calculation", ret)

```

## ToDo

- build in a flag, such class can be used without sefra importing all the epics stuff, or desing an examle how to disable sefra in total
- function with  mutltiple arguments