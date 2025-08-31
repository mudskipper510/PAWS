from rembg import remove, new_session
from PIL import Image
import matplotlib.pyplot as plt
import time

input_path1 = "D:\Photo Backup\Adrien's iPhone\Recents\IMG_8430.JPG" # cat on wood
input_path2 = "D:\Photo Backup\Adrien's iPhone\Recents\IMG_8385.JPG" # fencing sophia
input_path3 = "D:\Photo Backup\Adrien's iPhone\Recents\IMG_6819_1.JPG" # skirt me
input_path4 = "D:\Photo Backup\Adrien's iPhone\Recents\IMG_8413.JPG" # on floor with cat
input_path5 = "D:\Photo Backup\Adrien's iPhone\Recents\IMG_7991.PNG" # bae sophia at lake
# input_path6 = "D:\Photo Backup\Adrien's iPhone\Recents\IMG_8298.JPG" # leg shot

input1 = Image.open(input_path1)
input2 = Image.open(input_path2)
input3 = Image.open(input_path3)
input4 = Image.open(input_path4)
input5 = Image.open(input_path5)
# input6 = Image.open(input_path6)

startTime = time.time()

session = new_session("birefnet-general", ["CUDAExecutionProvider"]) # USE THIS ONE. HAVE TRIED ALL OTHERS

output1 = remove(input1, post_process_mask=True, session=session)
output2 = remove(input2, post_process_mask=True, session=session)
output3 = remove(input3, post_process_mask=True, session=session)
output4 = remove(input4, post_process_mask=True, session=session)
output5 = remove(input5, post_process_mask=True, session=session)
# output6 = remove(input6, post_process_mask=True, session=session)

endTime = time.time()
print(f"Took {endTime-startTime} seconds for 5 images")

fig, axs = plt.subplots(nrows=2, ncols=5, figsize=(25, 10)) # Adjust figsize as needed
fig.patch.set_facecolor('cyan')
axs[0, 0].imshow(input1.rotate(-90))  # Top-left (row 0, column 0)
axs[0, 1].imshow(input2.rotate(-90))  # Next to it
axs[0, 2].imshow(input3.rotate(-90))
axs[0, 3].imshow(input4.rotate(-90))
axs[0, 4].imshow(input5)
# axs[0, 5].imshow(input6.rotate(180)) # Top-right

axs[1, 0].imshow(output1)  # Bottom-left (row 1, column 0)
axs[1, 1].imshow(output2)
axs[1, 2].imshow(output3)
axs[1, 3].imshow(output4)
axs[1, 4].imshow(output5)
# axs[1, 5].imshow(output6) # Bottom-right

# output1.save("D:\output1.png")
# output2.save("D:\output2.png")
# output3.save("D:\output3.png")
# output4.save("D:\output4.png")
# output5.save("D:\output5.png")

# Hide axes for a cleaner look
for ax_row in axs:
    for ax in ax_row:
        ax.axis('off')
        ax.set_facecolor("cyan")

plt.subplots_adjust(wspace=0.05, hspace=0.05) # Adjust spacing between subplots
plt.show()
