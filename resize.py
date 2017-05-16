import os
import PIL.Image as PIL

def shrink(img_path, max_img_file_size, new_width=0, new_height=0):
    # send a photo here because it is too large for twitter and
    # this file will try to make smaller and smaller until twitter is happy
    img = PIL.open(img_path)
    orig_width = float(img.size[0])
    orig_height = float(img.size[1])

    if not new_width or not new_height:
        # just running it through Pillow can shrink the size!
        new_width = orig_width
        new_height = orig_height

    resize_ratio = new_width/orig_width
    new_height = resize_ratio * orig_height
    new_img_file_name = "%s_%s_%s.%s" % (img_file_name.split('.')[0], str(int(new_width)), str(int(new_height)), img_file_name.split('.')[1])

    img.resize((int(orig_width), int(orig_height)), PIL.ANTIALIAS)
    img.save(new_img_file_name, quality=90)

    file_size = os.path.getsize(new_img_file_name)
    if file_size > max_img_file_size:
        # keep shrinking by 100px until we get until max_file_size
        os.remove(base_path + new_img_file_name)  # clean up
        return resize(img_path, (new_width-50, new_height-50), quality=90)

    return new_image
