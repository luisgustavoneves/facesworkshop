from PIL import Image
from glob import glob


imgs = glob('imgs/*.jpg')
i1 = Image.open(imgs[0])

i2 = Image.open(imgs[1])
i0 = Image.blend(i1,i2,1./2)

for i, img_path in enumerate(imgs[2:]):
    img = Image.open(img_path)
    i0 = Image.blend(i0,img,1./(i+3))


i0.show()
