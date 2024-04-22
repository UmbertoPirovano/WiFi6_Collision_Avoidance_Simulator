from mmseg.apis import MMSegInferencer

# Initialize the SegInferencer
config = '/home/bert/github/5G_CARS_1/Computer_vision/configs/deeplabv3plus_r50-d8_4xb2-40k_cityscapes-512x1024.py'
checkpoint = '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/deeplabv3plus_r50-d8_512x1024_40k_cityscapes_20200605_094610-d222ffcd.pth'

#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/demo.jpg'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_shadowCar.png'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_PhysXCar__0_1713713051640143400.png'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_manhole_fence.png'
#img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_parkedCar.png'
img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_PhysXCar__0_1713713051640143400.png'
dir = '/home/bert/github/5G_CARS_1/Computer_vision/images/'

inferencer = MMSegInferencer(model=config, weights=checkpoint, device='cuda:0')

# Perform inference
#inferencer(img, show=True)
inferencer(dir, out_dir='/home/bert/github/5G_CARS_1/Computer_vision/seg_outputs/')