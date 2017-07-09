# telemetry-Processing

To run the telemetry viewer, make sure you have `npm` at least version 3.3.6 and `node` at least version 5.0.0
- You can get these by first installing `nvm`, Node Version Manager.
To run the telemetry viewer, do the following:
1. Clone this repo
2. `cd` into the repo
3. `cd nasa_mct`
4. `npm install`
5. `npm start`
6. Open a browser tab and go to `localhost:2008`

This repo will contain the Desktop side code to process, visualize, and log telemetry.

#### Python Dependencies:
*It is recommended you use `virtualenv` when running and developing the python code inside `serial_reader/`*
* Python 3.5+
  * If you're on ubuntu, you can follow: <https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get> to install
  * If you're on mac, install `pyenv` using `brew` just like this link says: <https://news.ycombinator.com/item?id=13244866>
    and then install the appropriate version of python using `pyenv`.
  * If you're on windows, install from <https://www.python.org/downloads/release/python-361/>
* [Asyncio and websockets](https://websockets.readthedocs.io/en/stable/index.html)
* [pyserial](http://pyserial.readthedocs.io/en/latest/pyserial.html)
* [pyserial-asyncio](http://pyserial-asyncio.readthedocs.io/en/latest/shortintro.html)

Requirements:

1. Read to and write from a serial port
2. Plot incoming sensor data in real time
3. Store data in a structured, and easy-to-parse format for post-facto reading and plotting.
4. Animate a model in 3D according to incoming sensor inputs.
