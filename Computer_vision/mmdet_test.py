from mmdet.apis import DetInferencer

# Initialize the DetInferencer
#config = '/home/bert/github/5G_CARS_1/Computer_vision/configs/mask-rcnn_r50_fpn_1x_cityscapes.py'
config = '/home/bert/github/5G_CARS_1/Computer_vision/configs/faster-rcnn_r50_fpn_1x_cityscapes.py'
#checkpoint = '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/mask_rcnn_r50_fpn_1x_cityscapes_20201211_133733-d2858245.pth'
checkpoint = '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/faster_rcnn_r50_fpn_1x_cityscapes_20200502-829424c0.pth'

#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/demo.jpg'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_shadowCar.png'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_PhysXCar__0_1713713051640143400.png'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_manhole_fence.png'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_parkedCar.png'
img = '/home/bert/github/5G_CARS_1/Computer_vision/images/1_Pp9PK0albIXz1bO4n-hj_A.png'
dir = '/home/bert/github/5G_CARS_1/Computer_vision/images/'

inferencer = DetInferencer(model=config, weights=checkpoint, device='cuda:0')

# Perform inference
#inferencer(img, show=True)
inferencer(dir, out_dir='/home/bert/github/5G_CARS_1/Computer_vision/outputs/', no_save_pred=True)