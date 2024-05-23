import cv2
import numpy as np
import matplotlib.pyplot as plt

class RoI:
    def __init__(self, mask_path, img_path=None):
        self.img = None
        self.img_mask = None
        self.height = None
        self.width = None
        self.lines = None
        self.mask = None
        self.mask_inv = None

        # Load the image and mask
        self.img_mask = cv2.imread(mask_path)[:,:,0]
        if img_path is not None:
            self.img = cv2.imread(img_path)

        self.height, self.width = self.img_mask.shape[:2]

        # Define lines
        self.lines = [
            (0, self.height, self.width, self.height),
            (0, self.height, int(self.width/2-self.width/32), int(self.height/2)),
            (self.width, self.height, int(self.width/2 + self.width/32), int(self.height/2)),
            (int(self.width/2 + self.width/32), int(self.height/2), int(self.width/2 - self.width/32), int(self.height/2))
        ]

        # Create a mask for the trapezoid
        self.mask = np.zeros_like(self.img_mask[:, :])
        pts = np.array([[0, self.height], 
                        [int(self.width/2-self.width/32), int(self.height/2)], 
                        [int(self.width/2 + self.width/32), int(self.height/2)], 
                        [self.width, self.height]], np.int32)
        cv2.fillPoly(self.mask, [pts], (255))

        # Create the inverse mask
        self.mask_inv = cv2.bitwise_not(self.mask)

    def draw_roi(self, display=True):
        if self.img is None:
            raise Exception("Error: Image not loaded.")
        
        img = self.img.copy()
        # Draw the lines on the image
        for line in self.lines:
            cv2.line(img, (line[0], line[1]), (line[2], line[3]), (0, 255, 0), 2)

        # Dim the area outside the ROI
        img[self.mask_inv == 255] //= 2

        # Convert the image from BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if display:
            plt.imshow(img)
            plt.title('Result')
            plt.axis('off')
            plt.show()
        return img

    def get_pixels_in_roi(self):        
        # Convert the mask to a boolean array
        mask_bool = self.mask == 255
        # Extract the pixels within the region of interest
        pixels_in_roi = self.img_mask[mask_bool]

        return pixels_in_roi
    
    def detect_in_roi(self):
        blacklist = {2: 'building', 3: 'wall', 4: 'fence', 5: 'pole',
                    6: 'traffic light', 7: 'traffic sign', 11: 'person', 12: 'rider',
                    13: 'car', 14: 'truck', 15: 'bus', 16: 'train', 17: 'motorcycle',
                    18: 'bicycle', -1: 'license plate'}
        counter = blacklist.fromkeys(blacklist, 0)
        roi = self.get_pixels_in_roi()
        for i in roi:
            if i in blacklist.keys():
                counter[i] += 1
        # Remove the keys with a value of 0
        counter = {key: value for key, value in counter.items() if value != 0}
        for key, value in counter.items():
            print(f'{blacklist[key]}: {value}') if value != 0 else None
        return counter



# Load the image
img_path = '/home/bert/github/5G_CARS_1/Computer_vision/mmseg_outputs/vis/image_8.png'
mask_path = '/home/bert/github/5G_CARS_1/Computer_vision/mmseg_outputs/pred/00000007_pred.png'
roi = RoI(mask_path,img_path)
roi.detect_in_roi()
roi.draw_roi()



