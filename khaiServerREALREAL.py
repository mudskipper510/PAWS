import websockets
import asyncio
import time
from PIL import Image
import json
from io import BytesIO
import base64
import numpy as np
import depthai as dai

async def WSHandler(websocket):
    await websocket.send("Server connected")
    # Create pipeline
    pipeline = dai.Pipeline()
    cam = pipeline.create(dai.node.ColorCamera)
    cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
    cam.setPreviewSize(640, 360)
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName("rgb")
    cam.preview.link(xout.input)
    print(len(dai.Device.getAllAvailableDevices()))
    with dai.Device(pipeline, maxUsbSpeed=dai.UsbSpeed.HIGH) as device:
        while True:
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            try:
                frame:np.ndarray = qRgb.get().getFrame()
                # recvMess:str = await websocket.recv()
                theTime:float = time.gmtime()

                imageBytesIO = BytesIO()
                Image.fromarray(frame).save(imageBytesIO, format='PNG')
                imageBytes = imageBytesIO.getvalue()
                base64EncodedImage = base64.b64encode(imageBytes).decode('utf-8')

                constructedJSON:dict = {"time": f"{theTime.tm_min}:{theTime.tm_sec}", "image": base64EncodedImage}

                await websocket.send(json.dumps(constructedJSON))
                await asyncio.sleep(0.07)
                print("sent image")
            except websockets.ConnectionClosedOK:
                print("Client closed connection normally.")
                break
            except Exception as e:
                print(f"Error while receiving data: {e}")
                break

async def main():
    async with websockets.serve(WSHandler, "localhost", 8080, max_size=None):
        await asyncio.Future() # run forever

if __name__ == "__main__":
    asyncio.run(main())