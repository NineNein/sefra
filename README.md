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


## ToDo

- Streaming Example
- return callable class to provide funcions:
    - get() last seted value
    - callback, sets a callback function to the epics name
    - name, gets epics name
- build in a flag, such class can be used without sefra importing all the epics stuff, or desing an examle how to disable sefra in total