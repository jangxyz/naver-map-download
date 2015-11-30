#!/usr/bin/env python

import sys, os, time, random
import urllib, urllib2, urlparse
from PIL import Image

U = '''http://onetile%d.map.naver.net/hd/135/0/0/%d/%d/%d/bl_vc_bg/ol_vc_an'''

#size = 13
#x_start, x_end = (6733, 6769)
#y_start, y_end = (5969, 6029)

size = 12
x_start, x_end = (3403, 3417)
y_start, y_end = (3005, 3031)


xs = range(x_start, x_end +1)
ys = range(y_end, y_start +1, -1)

IMG_ROOT_DIR = 'images'

def get_url(size, x, y):
    tile_subdomain = ((x % 4) + (y % 4)) % 4 + 1
    url = U % (tile_subdomain, size, x, y)
    return url

def get_filename(size, x, y):
    return 'hd-135-%d-%d-%d.png' % (size,x,y)
    #return 'hd-135-%d-%d.png' % (x,y)

def get_filedir(size, xs, ys, mkdir=False):
    download_id = '%d-x%d-%d-y%d-%d' % (size, xs[0], xs[-1], ys[0], ys[-1])
    download_dir = os.path.join(IMG_ROOT_DIR, download_id)
    if mkdir and not os.path.exists(download_dir):
        os.mkdir(download_dir)
    return download_dir


#
# generators
#

def generating_xy(xs, ys):
    for x in xs:
        for y in ys:
            yield (x,y)

def generating_urls(size, xs, ys):
    for (x,y) in generating_xy(xs, ys):
        u = get_url(size, x, y)
        yield u,x,y


def download_all(size, xs, ys, skip_index=0):
    download_dir = get_filedir(size, xs, ys, mkdir=True)
    max_index = len(xs) * len(ys)
    for i,(u,x,y) in enumerate(generating_urls(size, xs, ys)):
        if i < skip_index:
            continue
        print '[%d/%d]' % (i+1, max_index), u,
        #print
        img_filename = get_filename(size,x,y)
        img_filepath = os.path.join(download_dir, img_filename)
        resp = urllib.urlretrieve(u, img_filepath)
        print resp[1].status
        #
        if i % 10 == 10 - 1:
            time.sleep(random.random())


def stitch(size, xs, ys, tile_size=512):
    x_len = len(xs)
    y_len = len(ys)
    # big result image
    result_img = Image.new("RGB", (tile_size * x_len, tile_size * y_len), "white")
    # paste each images
    download_dir = get_filedir(size, xs, ys)
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            filename = get_filename(size, x, y)
            filepath = os.path.join(download_dir, filename)
            if not os.path.exists(filepath):
                print 'cannot find path:', filepath
                sys.exit(1)
            print '#%d/%d' % (i*y_len + j + 1, x_len * y_len), filepath
            #print i,j,filepath
            #
            image = Image.open(filepath)
            if tile_size and image.size != (tile_size, tile_size):
                image = image.resize((tile_size, tile_size))
            x_pos = tile_size * i
            y_pos = tile_size * (y_len - j -1)
            result_img.paste(image.copy(), 
                (x_pos, y_pos, x_pos + tile_size, y_pos + tile_size))
    # save result image
    result_filename = 'stitch-size%d-x%d-%d-y%d-%d-tile%d.png' % (size, min(xs), max(xs), min(ys), max(ys), tile_size)
    print 'saving', result_filename, '...'
    result_img.save(result_filename, 'png')
    #
    return result_img


def download_and_stitch(size, xs, ys, tile_size=512):
    #
    print 'Downloading...'
    download_all(size, xs, ys)
    print 'Download complete'
    #
    print 'Stitching...'
    img = stitch(size, xs, ys, tile_size=tile_size)
    print 'Stitch complete.'



#
# main
#

# config
size = 12
x_start, x_end = (3403, 3417)
y_start, y_end = (3005, 3031)
#x_range = range(x_start, x_end +1)
#y_range = range(y_end, y_start -1, -1)

#
size = 11
#x_range = range(1701, 1709 +1)
#y_range = range(1502, 1516 +1)
#

## download
#download_all(size, x_range, y_range)
## stitch
#img = stitch(size, x_range, y_range, tile_size=512)

## download + stitch
#download_and_stitch(size, x_range, y_range, tile_size=512)
#stitch(size, x_range, y_range, tile_size=256)

if __name__ == '__main__':
    tile_size = 512
    if 6 <= len(sys.argv) <= 7:
        dlevel = int(sys.argv[1])
        xs = int(sys.argv[2]), int(sys.argv[3])
        ys = int(sys.argv[4]), int(sys.argv[5])
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        #
        if len(sys.argv) == 7:
            tile_size = int(sys.argv[6])

    elif 3 <= len(sys.argv) <= 4:
        url1 = sys.argv[1]
        url2 = sys.argv[2]
        (_hd, _x135, _x0a, _x0b, dlevel, x1, y1, _rest) = urlparse.urlparse(url1).path.strip('/').split('/', 7)
        (_hd, _x135, _x0a, _x0b, dlevel, x2, y2, _rest) = urlparse.urlparse(url2).path.strip('/').split('/', 7)
        dlevel = int(dlevel)
        xs = map(int, (x1, x2))
        ys = map(int, (y1, y2))
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        #
        if len(sys.argv) == 4:
            tile_size = int(sys.argv[3])

    else:
        print 'Usage: %s DLEVEL X_START X_END Y_START Y_END [TILE_SIZE]'
        print 'Usage: %s NAVER_MAP_URL1 NAVER_MAP_URL2 [TILE_SIZE]'
        sys.exit(0)

    #
    x_range = range(x_min, x_max+1)
    y_range = range(y_min, y_max+1)

    #
    print 'Downloading...'
    download_all(dlevel, x_range, y_range)
    print 'Download complete'

    #
    print 'Stitching...'
    img = stitch(dlevel, x_range, y_range, tile_size=tile_size)
    print 'Stitch complete.'


