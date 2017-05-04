import Z80
import numpy as np
# from gym.envs.classic_control import rendering


xscale = 1
yscale = 1

SCREEN_WIDTH=256*xscale; SCREEN_HEIGHT=192*yscale
CENTER_X=SCREEN_WIDTH/2; CENTER_Y=SCREEN_HEIGHT/2

sat = 238
norm = 128

black = (0, 0, 0)
blue = (0, 0, norm)
red = (norm, 0, 0)
magenta = (norm, 0, norm)
green = (0, norm, 0)
cyan = (0, norm, norm)
yellow = (norm, norm, 0)
white = (norm, norm, norm)

brightColors = [(0,0,0),(0,0,sat),(sat,0,0),(sat,0,sat),(0,sat,0),(0,sat,sat),(sat,sat,0),(sat,sat,sat),
black,blue,red,magenta,green,cyan,yellow,white]


borderWidth = 20   # absolute, not relative to pixelScale
pixelScale = 1    # scales pixels in main screen, not border

nPixelsWide = 256
nPixelsHigh = 192
nCharsWide  = 32
nCharsHigh  = 24

firstAttr = (nPixelsHigh*nCharsWide)
lastAttr  = firstAttr + (nCharsHigh*nCharsWide)

first = -1
FIRST = -1
last = range((nPixelsHigh+nCharsHigh)*nCharsWide)
next = range((nPixelsHigh+nCharsHigh)*nCharsWide)


buf_start = 16384
buf_end = 22527
buf_length = buf_end - buf_start + 1
attr_start = 22528
attr_end = 23295
nameCount = 1

# don't crop anything by default
right_crop = 0
left_crop = nPixelsWide
up_crop = 0
down_crop = nPixelsHigh

class VideoArray:
    def __init__(self):
        self.image_array = np.empty((192, 256, 3), dtype=np.uint8)

    def set_pixel(self, y, x, rgb):
        self.image_array[x, y] = rgb

    def get_image(self):
        return self.image_array


def init(crop=None):
    global video_array, viewer, right_crop, left_crop, up_crop, down_crop
    #viewer = rendering.SimpleImageViewer()
    video_array = VideoArray()
    if crop:
        # (right, left, up, down)
        right_crop = crop[0]
        left_crop = nPixelsWide - crop[1]
        up_crop = crop[2]
        down_crop = nPixelsHigh - crop[3]

        assert crop[0] + crop[1] <= nPixelsWide and 0 <= crop[0] <= nPixelsWide and 0 <= crop[1] <= nPixelsWide
        assert crop[2] + crop[3] <= nPixelsHigh and 0 <= crop[0] <= nPixelsHigh and 0 <= crop[1] <= nPixelsHigh
    return


def fill_screen_map():
    global Z80, video_array
    mem = Z80.mem

    for addr in xrange(buf_start, buf_end + 1):
        y = ((addr & 0x00e0) >> 2) + ((addr&0x0700) >> 8) +((addr&0x1800) >> 5)
        sx = (addr & 0x1f) << 3

        attr = mem[ 22528 + (addr&0x1f) + ((y>>3)*32)]
        bright = ((attr>>3) & 0x08)
        ink = ((attr   ) & 0x07) | bright
        pap = ((attr>>3) & 0x07) | bright

        byte = mem[addr]

        if (1 << 7) & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])
        sx += 1
        if (1 << 6) & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])
        sx += 1
        if (1 << 5) & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])
        sx += 1
        if (1 << 4) & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])
        sx += 1
        if (1 << 3) & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])
        sx += 1
        if (1 << 2) & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])
        sx += 1
        if (1 << 1) & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])
        sx += 1
        if 1 & byte: color = ink
        else: color = pap
        video_array.set_pixel(sx, y, brightColors[color])


def get_frame_as_array():
    global video_array
    fill_screen_map()
    return video_array.get_image()[up_crop:down_crop, right_crop:left_crop, :]

def update(mode='human'):
    # global viewer
    img = get_frame_as_array()
    if mode == 'rgb_array':
        return img
    # elif mode == 'human':
    #     from gym.envs.classic_control import rendering
    #     viewer.imshow(img)

# def close():
#     global viewer
#     viewer.close()