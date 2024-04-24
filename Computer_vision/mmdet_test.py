from mmdet.apis import DetInferencer
import time

# Initialize the DetInferencer
#config = '/home/bert/github/5G_CARS_1/Computer_vision/configs/mask-rcnn_r50_fpn_1x_cityscapes.py'
config = '/home/bert/github/5G_CARS_1/Computer_vision/configs/faster-rcnn_r50_fpn_1x_cityscapes.py'
#checkpoint = '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/mask_rcnn_r50_fpn_1x_cityscapes_20201211_133733-d2858245.pth'
checkpoint = '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/faster_rcnn_r50_fpn_1x_cityscapes_20200502-829424c0.pth'

img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_PhysXCar__0_1713713052532274500.png'
dir = '/home/bert/github/5G_CARS_1/Airsim/images'

inferencer = DetInferencer(model=config, weights=checkpoint, device='cuda:0')

start_time = time.time()
# Perform inference
#inferencer(img, show=True)
inferencer(dir, out_dir='/home/bert/github/5G_CARS_1/Computer_vision/mmdet_outputs/', no_save_pred=True)

end_time = time.time()
execution_time = end_time - start_time
print("Execution time:", execution_time, "seconds")