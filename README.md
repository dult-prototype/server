## Server for DULT

This is a simulation of an unwanted location tracking accessory in the form of a GATT Server.
The server has a service named "Non owner service" which helps in identifying it as an unwanted tracker.

### Install

```
pip install dbus-python multiprocessing playsound  
```
- Install the latest version of ```bluez``` following the steps from [here](https://www.makeuseof.com/install-bluez-latest-version-on-ubuntu/)

### Run


```python3 app.py```

### Reference
1. https://github.com/Douglas6/cputemp