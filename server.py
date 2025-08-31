import time
import websockets
import asyncio
from PIL import Image
import cv2
import numpy as np
import depthai as dai
import json

EVERYTHING_NORMAL = 0
PICTURE_BUTTON_PRESSED = 1

async def WSHandler(websocket):
  # Create pipeline
  pipeline = dai.Pipeline()
  cam = pipeline.create(dai.node.ColorCamera)
  cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
  cam.setPreviewSize(640, 360)
  cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
  xout = pipeline.create(dai.node.XLinkOut)
  xout.setStreamName("rgb")
  cam.preview.link(xout.input)

  # gameState: str = await websocket.recv()

  with dai.Device(pipeline, maxUsbSpeed=dai.UsbSpeed.HIGH) as device:
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
    while True:
      try:
        frame:np.ndarray = qRgb.get().getFrame()
        sendTime:float = time.time()
        await websocket.send(frame.tobytes(), text=False)
        backPing:dict = json.loads(await websocket.recv()) # await a ping back with a code after every frame to see if a picture button was pressed
        
        fps:float = 1/(backPing["time"]-sendTime)
        print(f"fps: {fps}")
        
        # await asyncio.sleep(0.033)
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
  print('Server Started on port 8080!')