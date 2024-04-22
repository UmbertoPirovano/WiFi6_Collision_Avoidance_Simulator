import cv2

# Load the image
img_path = '/home/bert/github/5G_CARS_1/Computer_vision/seg_outputs/vis/img_PhysXCar__0_1713713046244052800.png'
img = cv2.imread(img_path)

# Define image dimensions
height = img.shape[0]
width = img.shape[1]

# Define lines
lines = [
    (0, height, width, height),
    (0, height, int(width/2-width/32), int(height/2)),
    (width, height, int(width/2 + width/32), int(height/2)),
    (int(width/2 + width/32), int(height/2), int(width/2 - width/32), int(height/2))
]

# Draw the lines on the image
for line in lines:
    cv2.line(img, (line[0], line[1]), (line[2], line[3]), (0, 255, 0), 2)

# Display the result
cv2.imshow('Result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

