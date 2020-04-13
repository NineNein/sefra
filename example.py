import os
#os.environ["PATH"] += os.pathsep + r"C:\Software\Anaconda3\Lib\site-packages\epics\clibs\win64"

import sefra
import time
import random
import sefra
import threading
import random
import time

class example_channel(sefra.epics.device):

    def __init__(self, parent, channel):
        super(example_channel, self).__init__("CH" + str(channel), parent=parent)
        self.channel = channel

        self.freq = 0
        

    @sefra.epics.pv_set(type="float")
    def set_frequency(self, value):
        print("Set Frequency: ", self.name, self.channel, value)
        self.freq = value

    @sefra.epics.pv_get(type="float")
    def get_frequency(self):
        print("get freq")
        return random.randint(1,40)


    @sefra.epics.pv_get(type="float", count=50)
    def get_spectrum(self):
        print("get_spectrum")
        ret = [random.randint(1,40) for i in range(50)]
        #ret = random.randint(1,40)
        return ret

    @sefra.epics.pv_set(type="int")
    def set_stream(self, value):
        print("set_stream ", self.channel, value)
        if value == 0: #Stop Stream
            self.stream_run = False
        else: #Start Stream
            self.stream_run = True
            self.tid = threading.Thread(target=self.run_stream)
            self.tid.start()

    def run_stream(self):
        print("Start Stream")
        while self.stream_run:
            time.sleep(0.5)
            ret = [random.randint(1,40) for i in range(50)]
            #ret = random.randint(1,40)
            self.get_spectrum.set(ret)

            ret = random.randint(1,40)
            self.get_frequency.set(ret)

        print("Stop Stream")

    @sefra.epics.pv_get(type="float", thread = True)
    def long_get(self):
        print("get long freq")
        time.sleep(4)
        return self.freq

    @sefra.epics.pv_set(type="float", return_type = "string")
    def calc(self, value):
        print("calc")
        #time.sleep(3)

        
        print("In CAlc getfreq pv: ", self.get_frequency.pv_name())
        ret = random.randint(1,40)
        print(ret)
        self.get_frequency.set(ret)

        #ret = 1#self.get_frequency()
        return "test" + str(value * 10) + str(ret)

    @sefra.epics.pv_set(type="float", return_type = "string", thread = True)
    def long_calc(self, value):
        print("calc")
        time.sleep(2)
        return "test " + str(value * 10)

class example_device(sefra.epics.device):
    def __init__(self, name, server=False):
        super(example_device, self).__init__(name, server=server)

        self.channels = {}
        self.channels[0] = example_channel(self, 0)
        self.channels[1] = example_channel(self, 1)
        self.channels[2] = example_channel(self, 2)

    def channel(self, number):
        return self.channels.get(number, None)

    @sefra.epics.pv_get(type="string")
    def idn(self):
        return "example device"





if __name__ == "__main__":

    ed = example_device("example", server=True)
    ed.start()



