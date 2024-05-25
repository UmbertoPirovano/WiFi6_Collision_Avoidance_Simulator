import contextlib
import io
from mmseg.apis import MMSegInferencer



class CVEdgeService:
    def __init__(self, config=None, checkpoint=None):

        configs = [
            '/home/bert/github/5G_CARS_1/Computer_vision/configs/deeplabv3plus_r50-d8_4xb2-40k_cityscapes-512x1024.py',
            '/home/bert/github/5G_CARS_1/Computer_vision/configs/deeplabv3plus_r18-d8_4xb2-80k_cityscapes-512x1024.py'
        ]
        checkpoints = [
            '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/deeplabv3plus_r50-d8_512x1024_40k_cityscapes_20200605_094610-d222ffcd.pth',
            '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/deeplabv3plus_r18-d8_512x1024_80k_cityscapes_20201226_080942-cff257fe.pth'
        ]

        config = configs[1]
        checkpoint = checkpoints[1]
        with contextlib.redirect_stdout(io.StringIO()):
            self.inferencer = MMSegInferencer(model=config, weights=checkpoint, device='cuda:0')

    def perform_inference(self, img, out_dir):
        with contextlib.redirect_stdout(io.StringIO()):
            self.inferencer(img, out_dir=out_dir)
