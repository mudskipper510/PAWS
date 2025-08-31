import websockets
import asyncio
from PIL import Image
import cv2
import numpy as np
import json
import time

async def client():
  url = "ws://localhost:8080"
  async with websockets.connect(url, max_size=None) as websocket:
    while True:
      try:
        recvBytes: bytes = await websocket.recv()
        pingBackPackage:dict = {"time": time.time(), "statusCode": 0}
        await websocket.send(json.dumps(pingBackPackage))
        # Converting from a byte array to an image and effectively back to a byte array is not needed but easier to understand
        decodedImage: Image = Image.frombytes("RGB", (640,360), recvBytes)
        cvImage = np.array(decodedImage)
        cvImageBGR = cv2.cvtColor(cvImage, cv2.COLOR_RGB2BGR)

        cv2.imshow("Live Stream", cvImageBGR)
        if cv2.waitKey(1) == ord('q'):
          break
      except websockets.ConnectionClosedOK:
        print("Server closed connection normally.")
        break
      except Exception as e:
        print(f"Error while receiving data: {e}")
        break
    cv2.destroyAllWindows()

if __name__ == "__main__":
  asyncio.run(client())