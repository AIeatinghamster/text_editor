import struct


MAGIC = b"untx"
VERSION = 1


def pack_color(color):
    r, g, b, a = color
    return struct.pack("<BBBB", r, g, b, a)


def pack_style_run(run):
    start, length, style = run

    (
        font_id,
        size,
        text_color,
        bold,
        italic,
        underlined,
        crossed
    ) = style

    underline_enabled, underline_color = underlined
    crossed_enabled, crossed_color = crossed

    data = bytearray()

    data += struct.pack(
        "<II",
        start,
        length
    )

    data += struct.pack(
        "<If??",
        font_id,
        size,
        bold,
        italic
    )

    data += pack_color(text_color)

    data += struct.pack(
        "<?",
        underline_enabled
    )

    data += pack_color(underline_color)

    data += struct.pack(
        "<?",
        crossed_enabled
    )

    data += pack_color(crossed_color)

    return data


def pack_font(font_id, font_name):
    font_name_bytes = font_name.encode("utf-8")

    data = bytearray()

    data += struct.pack("<I", font_id)
    data += struct.pack("<I", len(font_name_bytes))
    data += font_name_bytes

    return data


def write_file(filename, text, font_registry, style_runs):

    data = bytearray()

    data += MAGIC

    data += struct.pack("<H", VERSION)

    data += struct.pack("<I", len(font_registry))

    for font_id, font_name in font_registry.items():
        data += pack_font(font_id, font_name)

    text_bytes = text.encode("utf-8")

    data += struct.pack("<I", len(text_bytes))
    data += text_bytes

    data += struct.pack("<I", len(style_runs))

    for run in style_runs:
        data += pack_style_run(run)

    with open(filename, "wb") as f:
        f.write(data)
test_text="Hello, world! This is a test of the text editor. Let's see how it handles different styles and fonts."
test_font_registry = {
    0: "Arial",
    1: "Times New Roman",
    2: "Courier New"
}
test_style_runs = [
    (0, 5, (0, 12.0, (255, 0, 0, 255), True, False, (True, (0, 0, 0, 255)), (False, (0, 0, 0, 255)))),
        (7, 5, (1, 14.0, (0, 255, 0, 255), False, True, (False, (0, 0, 0, 255)), (True, (255, 0, 0, 255)))),
        (13, 4, (2, 10.0, (0, 0, 255, 255), True, True, (True, (255, 255, 0, 255)), (True, (0, 255, 255, 255))))
]
if __name__=="__main__":
    write_file("test.untx", test_text, test_font_registry, test_style_runs)
