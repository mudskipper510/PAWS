from PIL import Image, ImageEnhance
import json
import random
import os
from tqdm import tqdm as progressBar
import multiprocessing
import concurrent.futures
import argparse

# prompt: write a function using PIL to take a first PNG image with a transparent background, scale it down a certain percentage and paste it on a second PNG image and return the result.
def stackAndScaleImage(objectImage, backgroundImage, scalePercent, position, randSat, randVal):
  """
  Takes a first PNG image, scales it down a certain percentage and pastes it on a second PNG image.

  Args:
  objectImage: PIL image of object
  backgroundImage: PIL image of background
  scalePercent: Percentage to scale down the first image. (MAKE FLOAT INSTEAD OF DUMB STUFF)
  position: Tuple of (x, y) coordinates to paste the scaled image.
 
  Returns:
  A PIL Image object with the first image pasted on the second image.
  """

  objectImage = Image.open(objectImage)
  backgroundImage = Image.open(backgroundImage)

  # Scale down the first image
  width, height = objectImage.size                     # extract the width and height of object
  newWidth = int(width * scalePercent)            # create a new width for object based on the scalePercent and makes it an int
  newHeight = int(height * scalePercent)          # create a new height for object based on the scalePercent and makes it an int
  objectScaled = objectImage.resize((newWidth, newHeight)) # use the resize method of a PIL Image to scale object to the new_width and new_height
 
  #==== Scaled the height to add more variation to the data, also modify the Saturation and the Value
  width, height = objectScaled.size # Reset the width and height variables to be the new width and height of object after scaling
  randomHeightScale = random.uniform(0.8, 1.2) # Choose a random scalePercent between the minimum and maximum values.
  newHeight = int(height * randomHeightScale) # Calculate the newHeight based on the random scalePercent above
  if newHeight > backgroundImage.height:
    newHeight = backgroundImage.height
  objectScaled = objectScaled.resize((width, newHeight)) # Resize the image just like above
  valEnhancer = ImageEnhance.Color(objectScaled)
  objectValScaled = valEnhancer.enhance(randVal+1.0) # Add 1 here because 1.0 = the original image and + increases val while - decreases val
  satEnhancer = ImageEnhance.Brightness(objectValScaled) # feed back val image to increase sat
  objectFullScaled = satEnhancer.enhance(randSat+1.0) # Same reason why we add 1
  #====

  backgroundImage.paste(objectFullScaled, position, objectFullScaled) # Paste the scaled image (object_scaled) on the second image without scaling the second image. (second parameter makes it so that the pixels with no value meant to be clear stay clear and aren't black)

  return (backgroundImage, width, newHeight) # Return the final stacked image

# prompt: write a function called combine_images which uses the stack_scaled_images function defined above and scale object to a random value between some minimum percentage and some maximum percentage of the size of background.  The position for object to be pasted onto background is randomly selected within the bounds of background
# SCALE PERCENTAGE IS HOW MUH OF THE FRAME YOU WANT TO TAKE UP NOT HOW MUCH YOU WANT TO SCALE THE OBJECT IMAGE DOWN
def selectScaleAndCreateYoloLabels(objectPath, backgroundPath, minSizePercent, maxSizePercent, objectClassStr, CLASSES, minSatPercentMod, maxSatPercentMod, minValPercentMod, maxValPercentMod):
  """
  Combines two images by pasting a scaled version of an object onto a background.

  SCALES BASED ON WIDTH

  Args:
    objectPath: Path to the object image.
    backgroundPath: Path to the background image.
    minSizePercent: Minimum percentage to scale down object's WIDTH.
    maxSizePercent: Maximum percentage to scale down object's WIDTH.

  Returns:
    A PIL Image object with the combined images.
  """

  object = Image.open(objectPath) # Open the first image as object
  background = Image.open(backgroundPath) # Open the second image as background

  objectWidth, objectHeight = object.size # Extract the width and height of object as objectWidth and objectHeight
  backgroundWidth, backgroundHeight = background.size # Extract the width and height of background as backgroundWidth and backgroundHeight

  # Choose a random scalePercent between the minimum and maximum values provided as parameters
  # NEVER ABOVE 1.0(?)
  scalePercent = random.uniform(minSizePercent, maxSizePercent)

  # as background's width before applying this random scale percent (should really be same as shortest side?)
  # baseScale = backgroundWidth / objectWidth # The baseScale is the ratio of how big background's width is compared to object's width (ONLY WITH MEASUREMENTS)
  baseScale = backgroundWidth/objectWidth if backgroundWidth <= backgroundHeight else backgroundHeight/objectHeight # scale based on shortest side of background
  """
  print({
    "backgroundWidth": backgroundWidth,
    "object.width": object.width,
    "objectWidth": objectWidth,
    "baseScale": baseScale,
    "scalePercent": scalePercent,
    "baseScale * scalePercent": baseScale * scalePercent,
    "object.width * scalePercent/100": object.width * scalePercent/100,
    "object.height * scalePercent/100": object.height * scalePercent/100,
  })
  """

  scalePercent = baseScale * scalePercent # fix the scalePercent to include the baseScale between the 2 images and be proportional

  # Choose a random position for object in background
  widthOfObjectAfterScaling = int(object.width * scalePercent)   # predict width of object after scaling so you can choose a random width in bounds of background
  heightOfObjectAfterScaling = int(object.height * scalePercent) # predict height of object after scaling so you can choose a random height in bounds of background
  x = random.randint(0, backgroundWidth - widthOfObjectAfterScaling)     # select random x position for object in background

  # ERROR IS HERE: The error is because background isn't tall enough to fit object even after scaling so the randint is trying to selced from 0 to a negative number
  y = random.randint(0, backgroundHeight - heightOfObjectAfterScaling)   # select random y position for object in background

  # Determine Sat and Val values
  randSat = random.uniform(minSatPercentMod, maxSatPercentMod)
  randVal = random.uniform(minValPercentMod, maxValPercentMod)

  combinedImage, finalWidth, finalHeight = stackAndScaleImage(objectPath, backgroundPath, scalePercent, (x, y), randSat, randVal) # Use the stack_scaled_images function to combine the two images

  # Save the paste_parameters as a json object
  debugParameters = {
    "width_background": backgroundWidth,
    "height_background": backgroundHeight,
    "paste_x": x,
    "paste_y": y,
    "paste_width": finalWidth,
    "paste_height": finalHeight,
  }

  # https://docs.cogniflow.ai/en/article/how-to-create-a-dataset-for-object-detection-using-the-yolo-labeling-format-1tahk19/
  # YOLO labeling parameters
  pasteParametersYolo = {
    "objectClassNum": CLASSES[objectClassStr],
    "x_center": (x + finalWidth/2.0) / backgroundWidth, # calculate what percentage of the width of background the center of scaled object will be
    "y_center": (y + finalHeight/2.0) / backgroundHeight, # calculate what percentage of the height of background the center of scaled object will be
    "width": finalWidth / backgroundWidth, # calculate what percentage of the width of background does scaled object take
    "height": finalHeight / backgroundHeight, # calculate what percentage of the height of background does scaled object take
  }

  return (combinedImage, debugParameters, pasteParametersYolo) # return the PIL image object after stacking, the parameters used for pasting, and the parameters used for pasting in a YOLO suitable notation


# prompt: write a function which uses the combine_images_james function defined above to randomly select an object from directory1 and combine it from a random background from directory2
def combineRandomImages(directory1, directory2, minSizePercent, maxSizePercent, CLASSES, minSatPercentMod, maxSatPercentMod, minValPercentMod, maxValPercentMod):
  """
  Combines two random images from the two directories using the combine_images_james function.

  Args:
    directory1: Path to the first directory.
    directory2: Path to the second directory.
    minSizePercent: Minimum percentage to scale down the first image.
    maxSizePercent: Maximum percentage to scale down the first image.

  Returns:
    A PIL Image object with the combined images.
  """

  # Get all files in directories. If one isn't an image it could break
  objectFiles = os.listdir(directory1) # Get a list of all files in the first directory
  backgroundFiles = os.listdir(directory2) # Get a list of all files in the second directory

  imageChosen = random.choice(objectFiles)
  objectClass = imageChosen.split("_")[0]

  # Choose random images
  objectPath = os.path.join(directory1, imageChosen) # Choose a random file from the first directory
  backgroundPath = os.path.join(directory2, random.choice(backgroundFiles)) # Choose a random file from the second directory

  # Use the combine_images_james_xy function to combine the two images.
  combinedImage, debugParameters, pasteParametersYolo = selectScaleAndCreateYoloLabels(objectPath, backgroundPath, minSizePercent, maxSizePercent, objectClass, CLASSES, minSatPercentMod, maxSatPercentMod, minValPercentMod, maxValPercentMod)

  # print(pasteParametersYolo)

  return (combinedImage, debugParameters, pasteParametersYolo) # re-return all of the returns from the combine_images_james_xy function

# def makeImage(testOrTrain="test", numImages=10, minSizePercent=.05, maxSizePercent=.8, i=-1):
def makeImage(args):
  (testOrTrain, minSizePercent, maxSizePercent, CLASSES, i, minSatPercentMod, maxSatPercentMod, minValPercentMod, maxValPercentMod) = args
  if i == -1:
    raise ValueError("Invalid i Value")
  # Combine the images from directory1 (game object) with images from directory2 (backgrounds).
  combinedImage, debugParameters, pasteParametersYolo = combineRandomImages("./objectImages", "./VOCdevkit/backingImages/"+testOrTrain, minSizePercent, maxSizePercent, CLASSES, minSatPercentMod, maxSatPercentMod, minValPercentMod, maxValPercentMod)
  # Figure out a file name based on the current iteration and type of dataset
  baseFilename = f"{testOrTrain}_{i:0{6}d}" # Max 100000 file names
  # Save the image to the specified folder based on type of data set and use the above created filename
  combinedImage.save('./ultralytics/Dataset/images/'+testOrTrain+'/'+baseFilename+'.png')

  # Open/create a text file with the same name as the image and add the paste_parameters_yolo to it
  with open('./ultralytics/Dataset/labels/'+testOrTrain+'/'+baseFilename+'.txt', "w") as f:
    yoloData = pasteParametersYolo
    f.write(f"{yoloData['objectClassNum']} {round(yoloData['x_center'],6)} {round(yoloData['y_center'],6)} {round(yoloData['width'],6)} {round(yoloData['height'],6)}") # write data and round it to the correct decimal places (first digit in string is the class)


# Main function that ties together all of the other functions to make it work
# def makeData(testOrTrain="test", numImages=10, minSizePercent=.05, maxSizePercent=.8):
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--classes", type=str)
  parser.add_argument("--testOrTrain", default="test", type=str)
  parser.add_argument("--numImages", default=2, type=int)
  parser.add_argument("--minSizePercent", default=.2, type=float)
  parser.add_argument("--maxSizePercent", default=.8, type=float)
  parser.add_argument("--minSatPercentMod", default=-.2, type=float)
  parser.add_argument("--maxSatPercentMod", default=.2, type=float)
  parser.add_argument("--minValPercentMod", default=-.15, type=float)
  parser.add_argument("--maxValPercentMod", default=.15, type=float)

  inputArgs = parser.parse_args()

  CLASSES = json.loads(inputArgs.classes.replace("'", '"'))
  testOrTrain = inputArgs.testOrTrain
  numImages = inputArgs.numImages
  minSizePercent = inputArgs.minSizePercent
  maxSizePercent = inputArgs.maxSizePercent
  minSatPercentMod = inputArgs.minSatPercentMod
  maxSatPercentMod = inputArgs.maxSatPercentMod
  minValPercentMod = inputArgs.minValPercentMod
  maxValPercentMod = inputArgs.maxValPercentMod

  testOrTrain = testOrTrain.lower()

  args = tuple([(testOrTrain, minSizePercent, maxSizePercent, CLASSES, i, minSatPercentMod, maxSatPercentMod, minValPercentMod, maxValPercentMod) for i in range(numImages)]) # creates a tuple of tuple
  
  with concurrent.futures.ProcessPoolExecutor() as executor:
    executor.map(makeImage, args)