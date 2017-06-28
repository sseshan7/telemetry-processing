# telemetry-Processing

To run the telemetry viewer, make sure you have `npm` at least version 3.3.6 and `node` at least version 5.0.0
To run the telemetry viewer, do the following:
1. Clone this repo
2. `cd` into the repo
3. `cd nasa_mct`
4. `npm install`
5. `npm start`
6. Open a browser tab and go to `localhost:2008`

This repo will contain the Desktop side code to process, visualize, and log telemetry.
Requirements:

1. Read to and write from a serial port
2. Plot incoming sensor data in real time
3. Store data in a structured, and easy-to-parse format for post-facto reading and plotting.
4. Animate a model in 3D according to incoming sensor inputs.


#### Dependencies:
* Python 3.3+
* [Asyncio and websockets](https://websockets.readthedocs.io/en/stable/index.html)
