import time
import json
from PIL import Image
from io import BytesIO
import base64

theTime:float = time.time()

imageBytesIO = BytesIO()
testImage = Image.open("maxresdefault.jpg")
testImage.save(imageBytesIO, format='PNG')
imageBytes = imageBytesIO.getvalue()

base64EncodedImage = base64.b64encode(imageBytes).decode('utf-8')

# base64EncodedImage = ""

constructedJSON:dict = {"timeRecved": theTime, "image": base64EncodedImage}

print(json.dumps(constructedJSON))