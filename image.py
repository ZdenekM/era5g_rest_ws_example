import io

import PIL.Image
from PIL.Image import Image


# stolen from https://github.com/robofit/arcor2/blob/master/src/python/arcor2/image.py
def image_to_bytes_io(value: Image, target_format: str = "jpeg", target_mode: None | str = None) -> io.BytesIO:
    output = io.BytesIO()

    if target_mode and value.mode != target_mode:
        rgb_im = value.convert(target_mode)
        rgb_im.save(output, target_format)
    else:
        value.save(output, target_format)
    output.seek(0)
    return output


def image_from_bytes_io(value: io.BytesIO) -> Image:
    value.seek(0)
    return PIL.Image.open(value)
