import contextlib
import io
import shutil
import time
from mmseg.apis import MMSegInferencer



class CVEdgeService:
    def __init__(self, config=None, checkpoint=None, mode=0):

        configs = [
            '/home/bert/github/5G_CARS_1/Computer_vision/configs/deeplabv3plus_r50-d8_4xb2-40k_cityscapes-512x1024.py',
            '/home/bert/github/5G_CARS_1/Computer_vision/configs/deeplabv3plus_r18-d8_4xb2-80k_cityscapes-512x1024.py',
            '/home/bert/github/5G_CARS_1/Computer_vision/configs/deeplabv3plus_r101-d8_4xb2-amp-80k_cityscapes-512x1024.py',
            '/home/bert/github/5G_CARS_1/Computer_vision/configs/deeplabv3plus_r101-d16-mg124_4xb2-80k_cityscapes-512x1024.py'
        ]
        checkpoints = [
            '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/deeplabv3plus_r50-d8_512x1024_40k_cityscapes_20200605_094610-d222ffcd.pth',
            '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/deeplabv3plus_r18-d8_512x1024_80k_cityscapes_20201226_080942-cff257fe.pth',
            '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/deeplabv3plus_r101-d8_fp16_512x1024_80k_cityscapes_20200717_230920-f1104f4b.pth',
            '/home/bert/github/5G_CARS_1/Computer_vision/checkpoints/deeplabv3plus_r101-d16-mg124_512x1024_40k_cityscapes_20200908_005644-cf9ce186.pth'
        ]

        config = configs[mode]
        checkpoint = checkpoints[mode]
        with contextlib.redirect_stdout(io.StringIO()):
            self.inferencer = MMSegInferencer(model=config, weights=checkpoint, device='cuda:0')

    def perform_inference(self, img, out_dir='results', show=False):
        with contextlib.redirect_stdout(io.StringIO()):
            self.inferencer(img, out_dir=out_dir, show=show)

if __name__ == "__main__":
    edge_service = CVEdgeService(mode=3)
    start_time = time.time()
    image_path = '/home/bert/github/5G_CARS_1/Airsim/images/image_7.png'
    edge_service.perform_inference(image_path, out_dir='tmp')
    print(f"Execution time: {time.time() - start_time}")
    import matplotlib.pyplot as plt
    image = plt.imread('/home/bert/github/5G_CARS_1/tmp/vis/image_7.png')
    plt.imshow(image)
    plt.axis('off')
    plt.show()
    shutil.rmtree('/home/bert/github/5G_CARS_1/tmp')
