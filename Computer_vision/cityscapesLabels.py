import mmcv
import matplotlib.pyplot as plt
import cityscapesscripts.helpers.labels as labels

label_dict = {}
for label in labels.labels:
    label_dict[label.trainId] = label.name
print(label_dict)

blacklist = [2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, -1]
blacklist = {2: 'building', 3: 'wall', 4: 'fence', 5: 'pole',
              6: 'traffic light', 7: 'traffic sign', 11: 'person', 12: 'rider',
                13: 'car', 14: 'truck', 15: 'bus', 16: 'train', 17: 'motorcycle',
                  18: 'bicycle', -1: 'license plate'}
print(f'Blacklist: {[label_dict[i] for i in blacklist if i in label_dict.keys()]}')


map_path = '/home/bert/github/5G_CARS_1/Computer_vision/mmseg_outputs/pred/00000007_pred.png'
map = mmcv.imread(map_path, flag='unchanged')
plt.imshow(map, cmap='gray')
plt.colorbar()
plt.show()
