import io
from PIL import Image

def average_color(bytelike):
    img = Image.open(io.BytesIO(bytelike))
    img = img.resize((150, 150))
    img = img.split()[0]
    width, height = img.size

    r_total = 0
    g_total = 0
    b_total = 0

    count = 0
    for x in range(width):
        for y in range(height):
            r, g, b, a = img.getpixel((x,y))
            r_total += r
            g_total += g
            b_total += b
            count += 1
    
    r,g,b = (r_total//count, g_total//count, b_total//count)
    hex_str = f'{r:02x}{g:02x}{b:02x}'

    return int(hex_str, 16)

def old_bar(current, min, max, bar_length = 25, chars = ['█', ' ']):
    if max == min:
        return chars[0] * bar_length
    fill_length = int((current - min) / (max - min) * bar_length)
    return chars[0] * fill_length + chars[1] * (bar_length - fill_length)