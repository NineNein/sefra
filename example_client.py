import example as ex 
import epics
import os
import random


import time
def onChanges(pvname=None, value=None, char_value=None, **kw):
    print('PV Changed! ', pvname, char_value, time.ctime())

if __name__ == "__main__":




    ed = ex.example_device("example")

    ed.channel(0).get_spectrum.add_callback(onChanges)
    ed.channel(0).get_frequency.add_callback(onChanges)
    print("Spec: " ,ed.channel(0).get_spectrum())

    ed.channel(0).set_stream(1)
    time.sleep(5)
    ed.channel(0).set_stream(0)

    time.sleep(1)

    
    cv = random.randint(0,100)
    time.sleep(1)
    print("Calc")
    time.sleep(1)
    f = ed.channel(0).calc(cv)


    # rr = random.randint(0,100)

    # print("radom ", rr )

    # ed.channel(0).set_frequency(rr)
    # f = ed.channel(0).get_frequency()
    # print(f) 


    

    




    # print(ed.channel(0).set_frequency.get())

    # print(ed.pv_names())

    # cv = random.randint(0,100)
    # f = ed.channel(0).calc(cv)
    # print(cv, f)

    # print(ed.channel(0).calc.pv_name())


    # cv = random.randint(0,100)
    # f = ed.channel(1).long_calc(cv)
    # print("Long Run", cv, f)


    # #ed.channel(0).long_get.add_callback(onChanges)

    # print("Long get " ,ed.channel(0).long_get())

    #print(ed.idn())

    # ed.channel(1).set_frequency(random.randint(0,100))
    # ed.channel(0).set_frequency(random.randint(0,100))


    # while True:
    #     time.sleep(1)