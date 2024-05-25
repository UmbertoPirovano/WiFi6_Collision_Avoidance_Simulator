import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

class RoI:
    def __init__(self, mask_path, img_path=None, ratios=(10,10,80), steering=0):
        self.img = cv2.imread(img_path) if img_path else None
        self.img_mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

        if self.img_mask is None:
            raise ValueError("Error: Mask image not loaded correctly.")

        self.height, self.width = self.img_mask.shape
        self.ratios = ratios
        self.steering = steering
        
        self.lines = self._calculate_lines()
        print(self.lines)
        self.masks = self._create_trapezoid_masks()

        self.mask = self._create_main_roi_mask()
        self.mask_inv = cv2.bitwise_not(self.mask)

    def _calculate_lines(self):
        # shift is the horizontal shift of the trapezoid, to the left if steering is -1, to the right if steering is 1
        shift = self.width / 4 * self.steering
        if self.steering != 0:
            # The radius of the trapezoid is bigger when the steering is not 0
            radius = self.width / 16
        else:
            # The radius of the trapezoid is smaller when the steering is 0
            radius = self.width / 32        

        lines = [
            # horizontal lines
            (0, self.height, self.width, self.height),
            (int(self.width / 2 + radius + shift), int(self.height / 2), int(self.width / 2 - radius + shift), int(self.height / 2)),
            # vertical lines
            (0, self.height, int(self.width / 2 - radius + shift), int(self.height / 2)),
            (self.width, self.height, int(self.width / 2 + radius + shift), int(self.height / 2))
        ]
        # Define the middle lines based on the height ratio
        for i in range(len(self.ratios) - 1):
            ratio = sum(self.ratios[:i + 1])
            y = self.height / 2 * (1 + ratio / 100)
            x1 = ((y-self.height/2)/(self.height/2))*(radius-self.width/2-shift) + (self.width / 2 - radius + shift)
            x2 = ((y-self.height/2)/(self.height/2))*(-radius+self.width/2-shift) + (self.width / 2 + radius + shift)
            lines.append((int(x1), int(y), int(x2), int(y)))
        # Sort the lines based on the y-coordinate
        return sorted(lines, key=lambda x: (x[1], x[3]), reverse=True)

    def _create_trapezoid_masks(self):
        masks = []
        for i in range(len(self.lines)):
            x1, y1, x2, y2 = self.lines[i]
            if y1 != y2:
                continue
            pts = np.array([[x1, y1], [x2, y2]], np.int32)
            k = i + 1
            while len(pts) < 4 and k < len(self.lines):
                x3, y3, x4, y4 = self.lines[k]
                if y3 == y4:
                    pts = np.concatenate((pts, [[x3, y3], [x4, y4]]), axis=0)
                k += 1
            if len(pts) != 4:
                continue
            # Use the centroid to sort the points in order to properly draw the trapzoid
            centroid = np.mean(pts, axis=0)
            angles = np.arctan2(pts[:, 1] - centroid[1], pts[:, 0] - centroid[0])
            pts = pts[np.argsort(angles)]
            # Create the mask
            mask = np.zeros_like(self.img_mask)
            cv2.fillPoly(mask, [pts], 255)
            #plt.imshow(mask)
            #plt.show()
            masks.append(mask)
        return masks

    def _create_main_roi_mask(self):
        mask = np.zeros_like(self.img_mask)
        for m in self.masks:
            mask = cv2.bitwise_or(mask, m)
        return mask

    def draw_roi(self, display=True):
        if self.img is None:
            raise ValueError("Error: Demo image not loaded.")
        
        img = self.img.copy()
        for line in self.lines:
            cv2.line(img, (line[0], line[1]), (line[2], line[3]), (0, 255, 0), 2)
        
        img[self.mask_inv == 255] //= 2
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if display:
            plt.imshow(img)
            plt.title('Result')
            plt.axis('off')
            plt.show()
        return img

    def get_pixels_in_roi(self):
        pixels_in_roi = []
        for mask in self.masks:
            pixels = self.img_mask[mask == 255]
            pixels_in_roi.append(pixels)
        return pixels_in_roi
    
    def detect_in_roi(self):
        blacklist = {
            2: 'building', 3: 'wall', 4: 'fence', 5: 'pole',
            6: 'traffic light', 7: 'traffic sign', 11: 'person', 12: 'rider',
            13: 'car', 14: 'truck', 15: 'bus', 16: 'train', 17: 'motorcycle',
            18: 'bicycle', -1: 'license plate'
        }
        roi = self.get_pixels_in_roi()
        general_count = []

        for subarea in roi:
            counter = {key: 0 for key in blacklist}
            for pixel in subarea:
                if pixel in blacklist:
                    counter[pixel] += 1
            counter = {key: value for key, value in counter.items() if value > 0}
            general_count.append(counter)

        for i, counter in enumerate(general_count):
            print(f'Subarea {i + 1}:')
            for key, value in counter.items():
                print(f'    {blacklist[key]}: {value}')

        return general_count

# Load the image and mask
img_path = '/home/bert/github/5G_CARS_1/Computer_vision/mmseg_outputs/vis/image_8.png'
mask_path = '/home/bert/github/5G_CARS_1/Computer_vision/mmseg_outputs/pred/00000007_pred.png'
start_time = time.time()
roi = RoI(mask_path, img_path, steering=0)
roi.detect_in_roi()
print(f'Execution time: {time.time() - start_time:.2f} seconds')
roi.draw_roi()

roi = RoI(mask_path, img_path, steering=-1)
roi.detect_in_roi()
roi.draw_roi()

roi = RoI(mask_path, img_path, steering=1)
roi.detect_in_roi()
roi.draw_roi()