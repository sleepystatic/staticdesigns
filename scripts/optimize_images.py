"""Make WebP copies of site images in static/images. Needs Pillow; run with -h to see the modes."""
import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / 'image-sources'
IMAGES = ROOT / 'static' / 'images'
SCREENSHOT_WIDTHS = (720, 1200)
PHONE_RATIO = 9 / 19.5
PHONE_MAX_WIDTH = 720


def load(path):
    im = Image.open(path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        if im.getchannel('A').getextrema()[0] < 255:
            return im
    return im.convert('RGB')


def crop_to(im, ratio):
    # Templates reserve a fixed-shape box; keep the top of the page, which is what visitors see first.
    if im.width / im.height < ratio:
        return im.crop((0, 0, im.width, round(im.width / ratio)))
    if im.width / im.height > ratio:
        width = round(im.height * ratio)
        left = (im.width - width) // 2
        return im.crop((left, 0, left + width, im.height))
    return im


def save(im, path, quality):
    im.save(path, 'WEBP', quality=quality, method=6)
    print(f'{path.name}: {im.width}x{im.height}, {path.stat().st_size / 1024:.0f} KB')


def screenshot(path, out):
    im = crop_to(load(path), 2)
    if im.width < max(SCREENSHOT_WIDTHS):
        raise SystemExit(f'{path.name} is {im.width}px wide; screenshots need to be at least {max(SCREENSHOT_WIDTHS)}px wide.')
    for width in SCREENSHOT_WIDTHS:
        save(im.resize((width, width // 2), Image.LANCZOS), out / f'{path.stem}-{width}.webp', 80)


def mobile(path, out):
    im = crop_to(load(path), PHONE_RATIO)
    width = min(im.width, PHONE_MAX_WIDTH)
    save(im.resize((width, round(width / PHONE_RATIO)), Image.LANCZOS), out / f'{path.stem}.webp', 85)


def logo(path, height, out):
    im = load(path)
    height = min(height, im.height)
    width = round(im.width * height / im.height)
    save(im.resize((width, height), Image.LANCZOS), out / f'{path.stem}.webp', 90)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make WebP copies of site images.')
    parser.add_argument('kind', choices=['all', 'screenshot', 'mobile', 'logo'],
                        help='all = every *-preview (desktop) and *-mobile (phone) image in image-sources/')
    parser.add_argument('files', nargs='*', type=Path)
    parser.add_argument('--height', type=int, default=96, help='logo height in pixels (default 96)')
    parser.add_argument('--out', type=Path, help='output folder (default static/images, or static/images/logos for logos)')
    args = parser.parse_args()
    out = args.out or (IMAGES / 'logos' if args.kind == 'logo' else IMAGES)
    out.mkdir(parents=True, exist_ok=True)
    if args.kind == 'all':
        for file in sorted(SOURCES.glob('*-preview.*')):
            screenshot(file, out)
        for file in sorted(SOURCES.glob('*-mobile.*')):
            mobile(file, out)
    elif not args.files:
        parser.error('list at least one image file')
    else:
        for file in args.files:
            if args.kind == 'screenshot':
                screenshot(file, out)
            elif args.kind == 'mobile':
                mobile(file, out)
            else:
                logo(file, args.height, out)
