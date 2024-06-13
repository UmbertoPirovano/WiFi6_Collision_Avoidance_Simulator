import contextlib
import io
import os
import shutil
import time
import airsim
from mmseg.apis import MMSegInferencer
import numpy as np

from EdgeService.RoI_optimized import RoI



class CVEdgeService:
    def __init__(self, config=None, checkpoint=None, mode=0, out_dir='results', roi_ratio=[5,20,40,40], decision_params={'slowdown_coeff': [1,1,0.55,0.17], 'normal_threshold': 5, 'emergency_threshold': [5,5,80]}):
        
        self.out_dir = out_dir        
        self.roi = RoI(img_size=(576,1024), ratios=roi_ratio)
        self.slowdown_coeff = decision_params['slowdown_coeff']
        self.normal_threshold = decision_params['normal_threshold']
        self.emergency_threshold = decision_params['emergency_threshold']

        mode_dict = {
            'medium': 0,
            'super_light': 1,
            'heavy': 2,
            'light': 3
        }
        if isinstance(mode, str):
            mode = mode_dict[mode]

        configs = [
            'mmsegmentation/configs/deeplabv3plus/deeplabv3plus_r50-d8_4xb2-40k_cityscapes-512x1024.py',
            'mmsegmentation/configs/deeplabv3plus/deeplabv3plus_r18-d8_4xb2-80k_cityscapes-512x1024.py',
            'mmsegmentation/configs/deeplabv3plus/deeplabv3plus_r101-d8_4xb2-amp-80k_cityscapes-512x1024.py',
            'mmsegmentation/configs/deeplabv3plus/deeplabv3plus_r101-d16-mg124_4xb2-80k_cityscapes-512x1024.py'
        ]
        checkpoints = [
            'app/EdgeService/checkpoints/deeplabv3plus_r50-d8_512x1024_40k_cityscapes_20200605_094610-d222ffcd.pth',
            'app/EdgeService/checkpoints/deeplabv3plus_r18-d8_512x1024_80k_cityscapes_20201226_080942-cff257fe.pth',
            'app/EdgeService/checkpoints/deeplabv3plus_r101-d8_fp16_512x1024_80k_cityscapes_20200717_230920-f1104f4b.pth',
            'app/EdgeService/checkpoints/deeplabv3plus_r101-d16-mg124_512x1024_40k_cityscapes_20200908_005644-cf9ce186.pth'
        ]

        config = configs[mode]
        checkpoint = checkpoints[mode]
        with contextlib.redirect_stdout(io.StringIO()):
            self.inferencer = MMSegInferencer(model=config, weights=checkpoint, device=None)

    def perform_inference(self, img, show_result=False):
        print(f"EDGE: Performing inference on {img}")
        with contextlib.redirect_stdout(io.StringIO()):
            self.inferencer(img, out_dir=self.out_dir, show=show_result)

    def perform_detection(self, processed_dir, steering=0):
        print(f"EDGE: Performing detection")
        # Get the path to the last png added to processed_dir
        mask_files = sorted(os.listdir(os.path.join(processed_dir, 'pred')))
        view_files = sorted(os.listdir(os.path.join(processed_dir, 'vis')))
        mask_path = os.path.join(processed_dir, 'pred', mask_files[-1])
        vis_path = os.path.join(processed_dir, 'vis', view_files[-1])
        print(f"Mask path: {mask_path}")

        # EDGE SERVICE
        detected = self.roi.detect_in_roi(mask_path, vis_path, steering=0)
        return detected


    def perform_decision(self, detected):
        print(f"EDGE: Computing decision")
        # detected: list of dictionaries
        # detected[i]: dictionary of detected objects in subarea i. Each value represents the percentage of area covered by the object
        target_throttle = 0.5        
        slowdown_coeff = [coeff * target_throttle for coeff in self.slowdown_coeff]
        slowdown_factors = np.zeros(len(slowdown_coeff))

        action = airsim.CarControls()
        for i, counter in enumerate(detected):
            if counter:
                occupied_area = sum(counter.values())
                if (i+1) <= 3 and occupied_area > self.emergency_threshold[i]:
                    action.throttle = 0
                    action.brake = 1
                    print(f"Obstacle detected in subarea {i + 1}! Emergency stop!.")
                    return action
                if occupied_area > self.normal_threshold:
                    slowdown_factors[i] = occupied_area / 100 * slowdown_coeff[i]                    
                
                # TODO: Provide a weight for each object type
                if 13 in counter.keys():
                    slowdown_factors[i] *= 2.40
                elif 2 in counter.keys():
                    slowdown_factors[i] *= 0.5        

        new_throttle = target_throttle - sum(slowdown_factors)
        if new_throttle < 0: new_throttle = 0
        action.throttle = new_throttle
        print(f"Throttle set to: {action.throttle}")
        return action

if __name__ == "__main__":
    edge_service = CVEdgeService(mode='light', out_dir='tmp')
    start_time = time.time()
    image_path = '/home/bert/github/5G_CARS_1/Airsim/images/image_7.png'
    edge_service.perform_inference(image_path)
    detected = edge_service.perform_detection('tmp', steering=0)
    print(detected)
    print(f"Execution time: {time.time() - start_time}")
    import matplotlib.pyplot as plt
    image = plt.imread('/home/bert/github/5G_CARS_1/tmp/vis/image_7.png')
    plt.imshow(image)
    plt.axis('off')
    plt.show()
    shutil.rmtree('/home/bert/github/5G_CARS_1/tmp')
