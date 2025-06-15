from moviepy import VideoFileClip, clips_array, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

# full video: 576x1024 30fps
# top clip: 576x394
# bottom clip: 576x630


def create_caption(text):
    font = ImageFont.truetype("font.otf", size = 45)
    colour = (0,0,0)
    bg_colour = (255,255,255)
    radius = 10

    # calculate text boundaries
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    text_size = draw.textbbox((0, 0), text, font = font)
    width = text_size[2] - text_size[0] + 50
    height = text_size[3] - text_size[1] + 50
    max_width = 400

    lines = []
    words = text.split()
    current_line = ""

    widest_line = 0
    # print(words)

    counter = 0
    for word in words:

        if current_line == "":
            current_line += word
        else:
            current_line = current_line + " " + word

        # get width of line
        bbox = draw.textbbox((0,0), current_line, font = font)
        width = bbox[2] - bbox[0]

        if width > widest_line:
            widest_line = width

        if width > max_width:
            lines.append(current_line)
            current_line = ""
        if counter == len(words) - 1 and not current_line == "":
            lines.append(current_line)

        counter += 1

    # print(lines)


    img = Image.new("RGBA", (widest_line + 50, height*len(lines)), (0, 0, 0, 0)) # base for caption
    draw = ImageDraw.Draw(img)


    y = 25
    i = 0
    for line in lines:

        line_width = draw.textlength(line, font = font)

        # center
        x = (widest_line - line_width + 50) // 2

        if i > 0 and line_width < old_width:
            draw.rounded_rectangle((x - 15, y - 5, line_width + x + 15, y + 10), 0, fill = bg_colour) # connector
            draw.rounded_rectangle((x - 15, y - 5, line_width + x + 15, y + 55), radius, fill = bg_colour)
        else:
            draw.rounded_rectangle((x - 15, y - 5, line_width + x + 15, y + 55), radius, fill = bg_colour)


        draw.text((x,y), line, font = font, fill = colour)

        old_width = line_width

        y += 60
        i += 1

    caption_path = "caption.png"
    img.save(caption_path)
    return caption_path


def composite(video, text, length, output):

    # length limits
    bottom_duration = VideoFileClip(video + ".mp4").duration
    if length > 20 and bottom_duration > 20:
        length = 20

    if length > bottom_duration:
        length = bottom_duration

    top_clip = VideoFileClip("guy.mp4").subclipped(0, length)
    bottom_clip = VideoFileClip(video + ".mp4").subclipped(0, length)

    # resize vid
    (w,h) = bottom_clip.size

    # landscape or portrait (based on resolution)
    if w >= 1.09375 * h or w == h:
        bottom_resize = bottom_clip.resized(height = 630)
        # print("using landscape mode")
    else:
        bottom_resize = bottom_clip.resized(width = 576)
        # print("using portrait mode")

    (w,h) = bottom_resize.size
    bottom_resize = bottom_resize.cropped(width = 576, height = 630, x_center = w/2, y_center = h/2)
    bottom_resize = bottom_resize.without_audio()

    composite = clips_array([[top_clip],[bottom_resize]])

    # add caption
    caption_path = create_caption(text)
    caption = ImageClip(caption_path).with_duration(length).with_position(("center", 350))

    final = CompositeVideoClip([composite, caption])

    final.write_videofile(output + ".mp4")


# composite("B:/videos/the funny/hamster", "klja sdhsal", 1, "skibidi")

file = input("bottom video file name: ")
text = input("caption text: ")
length = int(input("video length (seconds): "))
output = input("output name: ")

composite(file, text, length, output)


