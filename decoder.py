import struct


MAGIC = b"untx"


def unpack_color(data, offset):
    r, g, b, a = struct.unpack_from(
        "<BBBB",
        data,
        offset
    )

    offset += 4

    return (r, g, b, a), offset


def unpack_font(data, offset):
    font_id = struct.unpack_from(
        "<I",
        data,
        offset
    )[0]

    offset += 4
    name_length = struct.unpack_from(
        "<I",
        data,
        offset
    )[0]

    offset += 4

    name_bytes = data[
        offset:offset + name_length
    ]

    offset += name_length

    font_name = name_bytes.decode("utf-8")

    return font_id, font_name, offset


def unpack_style_run(data, offset):
    start, length = struct.unpack_from(
        "<II",
        data,
        offset
    )
    offset += 8

    font_id, size, bold, italic = struct.unpack_from(
        "<If??",
        data,
        offset
    )
    offset += struct.calcsize("<If??")

    text_color, offset = unpack_color(
        data,
        offset
    )

    underline_enabled = struct.unpack_from(
        "<?",
        data,
        offset
    )[0]
    offset += 1

    underline_color, offset = unpack_color(
        data,
        offset
    )

    crossed_enabled = struct.unpack_from(
        "<?",
        data,
        offset
    )[0]
    offset += 1

    crossed_color, offset = unpack_color(
        data,
        offset
    )

    style = {
        "font_id": font_id,
        "size": size,
        "text_color": text_color,
        "bold": bold,
        "italic": italic,
        "underlined": {
            "enabled": underline_enabled,
            "color": underline_color
        },
        "crossed": {
            "enabled": crossed_enabled,
            "color": crossed_color
        }
    }

    run = {
        "start": start,
        "length": length,
        "style": style
    }

    return run, offset


def read_file(filename):
    with open(filename, "rb") as f:
        data = f.read()

    offset = 0


    magic = data[offset:offset + 4]
    offset += 4

    if magic != MAGIC:
        raise ValueError("Not a valid UNTX file")


    version = struct.unpack_from(
        "<H",
        data,
        offset
    )[0]

    offset += 2

    if version != 1:
        raise ValueError(
            f"Unsupported UNTX version: {version}"
        )

    
    font_count = struct.unpack_from(
        "<I",
        data,
        offset
    )[0]

    offset += 4

    font_registry = {}

    for _ in range(font_count):
        font_id, font_name, offset = unpack_font(
            data,
            offset
        )

        font_registry[font_id] = font_name


    text_byte_length = struct.unpack_from(
        "<I",
        data,
        offset
    )[0]

    offset += 4

    text_bytes = data[
        offset:offset + text_byte_length
    ]

    offset += text_byte_length

    text = text_bytes.decode("utf-8")


    run_count = struct.unpack_from(
        "<I",
        data,
        offset
    )[0]

    offset += 4

    style_runs = []

    for _ in range(run_count):
        run, offset = unpack_style_run(
            data,
            offset
        )

        style_runs.append(run)

    return {
        "version": version,
        "fonts": font_registry,
        "text": text,
        "style_runs": style_runs
    }
if __name__=="__main__":
    print(read_file("test.untx"))
