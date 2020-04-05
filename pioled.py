from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,width,height), outline=0, fill=0)
padding = -2
top = padding
bottom = height-padding
x = 0
font = ImageFont.load_default()



def set_text_lines(lines):
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    for i, line in enumerate(lines):
        draw.text((x, top + i * 8), line, font=font, fill=225)

    # Display image.
    disp.image(image)
    disp.display()
