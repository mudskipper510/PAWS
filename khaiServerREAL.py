import websockets
import asyncio
import time
from PIL import Image
import json
from io import BytesIO
import base64

async def WSHandler(websocket):
    await websocket.send("Server connected")
    while True:
        try:
            recvMess:str = await websocket.recv()
            theTime:float = time.gmtime()

            imageBytesIO = BytesIO()
            Image.open("maxresdefault.jpg").save(imageBytesIO, format='PNG')
            imageBytes = imageBytesIO.getvalue()
            base64EncodedImage = base64.b64encode(imageBytes).decode('utf-8')

            constructedJSON:dict = {"time": f"{theTime.tm_min}:{theTime.tm_sec}", "image": base64EncodedImage}

            await websocket.send(json.dumps(constructedJSON))
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