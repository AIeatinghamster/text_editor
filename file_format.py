import struct

MAGIC = b"untx"
VERSION = 1
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
class Object:
    def __init__(self, obj_id: int, position: tuple, size: tuple, obj_type: int ,z_index: int):
        self.obj_id = obj_id
        self.position = position
        self.size = size
        self.obj_type = obj_type
        self.z_index = z_index
    def pack(self):
        data = bytearray()
        data += struct.pack("<I", self.obj_id)
        data += struct.pack("<ff", *self.position)
        data += struct.pack("<ff", *self.size)
        data += struct.pack("<I", self.z_index)
        return data
    def unpack(data, offset):
        obj_id = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        position = struct.unpack_from("<ff", data, offset)
        offset += 8
        size = struct.unpack_from("<ff", data, offset)
        offset += 8
        obj_type = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        z_index = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        return Object(obj_id, position, size, obj_type, z_index), offset
class TextObject(Object):
    def __init__(self, obj_id: int, position: tuple, size: tuple, obj_type: int, z_index: int, text: str, style_runs: list):
        super().__init__(obj_id, position, size, obj_type, z_index)
        self.text = text
        self.style_runs = style_runs

    def pack(self):
        data = super().pack()
        text_bytes = self.text.encode("utf-8")
        data += struct.pack("<I", len(text_bytes))
        data += text_bytes
        packed_style_runs = bytearray()
        for run in self.style_runs:
            packed_style_runs += pack_style_run(run)
        data+= struct.pack("<I", len(self.style_runs))
        data += packed_style_runs
        return data
    def unpack(data, offset):
        obj, offset = Object.unpack(data, offset)
        text_length = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        text_bytes = data[offset:offset + text_length]
        text = text_bytes.decode("utf-8")
        offset += text_length
        style_runs = []
        num_style_runs = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        for _ in range(num_style_runs):
            run, offset = unpack_style_run(data, offset)
            style_runs.append(run)
        
        return TextObject(obj.obj_id, obj.position, obj.size, obj.obj_type, obj.z_index, text, style_runs), offset

objects = [TextObject(1, (10.0, 20.0), (200.0, 100.0), 1, 0, "Hello, world!", [(0, 5, (0, 12.0, (255, 0, 0, 255), True, False, (True, (0, 0, 0, 255)), (False, (0, 0, 0, 255))))])]

def pack_object(obj: Object):
    return obj.pack()
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
class Page:
    def __init__(self, horizontal: int, objects: list, text: str, style_runs: list):
        self.horizontal=horizontal
        self.objects=objects
        self.text=text
        self.style_runs=style_runs
    def pack(self):
        data=bytearray()
        data+=struct.pack("<I", self.horizontal)
        
        text_bytes = self.text.encode("utf-8")
        #data += struct.pack("<I", 1+len(self.objects)+len(text_bytes)+len(self.style_runs))
        data += struct.pack("<I", len(text_bytes))
        data += text_bytes
    
        data += struct.pack("<I", len(self.style_runs))
        for run in self.style_runs:
            data += pack_style_run(run)
        data += struct.pack("<I", len(objects))
        if len(self.objects) > 0:
            for obj in self.objects:
                data += struct.pack("<I", obj.obj_type)
                data += pack_object(obj)
        return data
    def unpack(data, offset):
        horizontal=struct.unpack_from(
            "<I",
            data,
            offset
        )[0]
        offset+=4
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
        object_count = struct.unpack_from(
            "<I",
            data,
            offset
        )[0]
        objs=[]
        if object_count > 0:
            for _ in range(object_count):
                obj_type = struct.unpack_from(
                    "<I",
                    data,
                    offset
                )[0]
                offset += 4
                if obj_type == 1:
                    obj, offset = TextObject.unpack(data, offset)
                    obj.obj_type = obj_type
                else:
                    obj, offset = Object.unpack(data, offset)
                    obj.obj_type = obj_type
                objs.append(obj)
        return Page(horizontal, objs, text, style_runs)

        


def write_file(filename, font_registry, pages=None):

    data = bytearray()

    data += MAGIC

    data += struct.pack("<H", VERSION)

    data += struct.pack("<I", len(font_registry))

    for font_id, font_name in font_registry.items():
        data += pack_font(font_id, font_name)
    data+=struct.pack("<I", len(pages))
    for page in pages:
        data+=page.pack()
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
        (7, 5, (1, 33.0, (0, 255, 0, 255), False, True, (False, (0, 0, 0, 255)), (True, (255, 0, 0, 255)))),
        (13, 4, (2, 10.0, (0, 0, 255, 255), True, True, (True, (255, 255, 0, 255)), (True, (0, 255, 255, 255))))
]
pages=[Page(0, objects, test_text, test_style_runs), Page(0, objects, test_text, test_style_runs)]
if __name__=="__main__":
    write_file("test.untx", test_font_registry, pages=pages)
