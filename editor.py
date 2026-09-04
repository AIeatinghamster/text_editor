import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QToolBar,
    QPushButton,
    QColorDialog,
)

from PyQt6.QtGui import (
    QAction,
    QTextCharFormat,
    QColor,
)

from PyQt6.QtCore import Qt

from file_format import write_file
from color_wheel import ColorPicker


class TextEditor(QMainWindow):

    def __init__(self ,document):
        super().__init__()

        self.setWindowTitle("My Text Editor")
        self.resize(900, 600)

        self.editor = QTextEdit()

        self.editor.setStyleSheet("""
            QTextEdit {
                font-size: 18px;
                color: black;
                background: white;
            }
        """)

        self.setCentralWidget(self.editor)
        self.editor.setPlainText(document["text"])
        self.load_styles(document)
        self.create_toolbar()

    def keyPressEvent(self, event):

        if (
            event.key() == Qt.Key.Key_S
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.save_document()
            event.accept()
            return

        super().keyPressEvent(event)

    def save_document(self):

        document = self.editor.document()

        text = document.toPlainText()

        text_bytes = text.encode("utf-8")

        style_runs = []

        font_registry = {}
        font_to_id = {}

        block = document.begin()

        while block != document.end():

            iterator = block.begin()

            while not iterator.atEnd():

                fragment = iterator.fragment()

                if fragment.isValid():

                    fragment_text = fragment.text()
                    fmt = fragment.charFormat()

                    font = fmt.font()
                    font_name = font.family()

                    if font_name not in font_to_id:
                        font_id = len(font_registry)

                        font_to_id[font_name] = font_id
                        font_registry[font_id] = font_name

                    else:
                        font_id = font_to_id[font_name]

                
                    before_text = text[:fragment.position()]
                    start = len(before_text.encode("utf-8"))

                    length = len(fragment_text.encode("utf-8"))


                    text_color = fmt.foreground().color()

                    underline_color = fmt.underlineColor()

                    if not underline_color.isValid():
                        underline_color = text_color

                    

                    style = (
                        font_id,
                        font.pointSizeF(),
                        (
                            text_color.red(),
                            text_color.green(),
                            text_color.blue(),
                            text_color.alpha()
                        ),
                        font.bold(),
                        font.italic(),

                        (
                            font.underline(),
                            (
                                underline_color.red(),
                                underline_color.green(),
                                underline_color.blue(),
                                underline_color.alpha()
                            )
                        ),

                        (
                            font.strikeOut(),
                            (
                                text_color.red(),
                                text_color.green(),
                                text_color.blue(),
                                text_color.alpha()
                            )
                        )
                    )

                    style_runs.append([
                        start,
                        length,
                        style
                    ])

                iterator += 1

            block = block.next()

        print("TEXT:")
        print(repr(text))

        print("\nFONTS:")
        print(font_registry)

        print("\nSTYLE RUNS:")
        for run in style_runs:
            print(run)

        write_file(
            "test.untx",
            text,
            font_registry,
            style_runs
        )
    def create_toolbar(self):

        toolbar = QToolBar()
        toolbar.setMovable(False)

        self.addToolBar(toolbar)


        bold = QAction("B", self)
        bold.setCheckable(True)
        bold.triggered.connect(self.toggle_bold)

        toolbar.addAction(bold)

        

        italic = QAction("I", self)
        italic.setCheckable(True)
        italic.triggered.connect(self.toggle_italic)

        toolbar.addAction(italic)

        

        underline = QAction("U", self)
        underline.setCheckable(True)
        underline.triggered.connect(self.toggle_underline)

        toolbar.addAction(underline)

       

        strike = QAction("S", self)
        strike.setCheckable(True)
        strike.triggered.connect(self.toggle_strike)

        toolbar.addAction(strike)

        toolbar.addSeparator()

      

        text_color = QPushButton("Text Color")

        text_color.clicked.connect(
            self.choose_text_color
        )

        toolbar.addWidget(text_color)

       

        underline_color = QPushButton(
            "Underline Color"
        )

        underline_color.clicked.connect(
            self.choose_underline_color
        )

        toolbar.addWidget(underline_color)


   
    def apply_format(self, fmt):

        cursor = self.editor.textCursor()

        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)


    def toggle_bold(self):

        cursor = self.editor.textCursor()

        fmt = QTextCharFormat()

        fmt.setFontWeight(
            700
            if cursor.charFormat().fontWeight() != 700
            else 400
        )

        self.apply_format(fmt)


    def toggle_italic(self):

        cursor = self.editor.textCursor()

        fmt = QTextCharFormat()

        fmt.setFontItalic(
            not cursor.charFormat().fontItalic()
        )

        self.apply_format(fmt)


    def toggle_underline(self):

        cursor = self.editor.textCursor()

        fmt = QTextCharFormat()

        fmt.setFontUnderline(
            not cursor.charFormat().fontUnderline()
        )

        self.apply_format(fmt)


    def toggle_strike(self):

        cursor = self.editor.textCursor()

        fmt = QTextCharFormat()

        fmt.setFontStrikeOut(
            not cursor.charFormat().fontStrikeOut()
        )

        self.apply_format(fmt)


    

    def choose_text_color(self):

        color = QColorDialog.getColor(
            QColor("black"),
            self,
            "Text Color"
        )

        if color.isValid():

            fmt = QTextCharFormat()

            fmt.setForeground(color)

            self.apply_format(fmt)


   

    def choose_underline_color(self):

        picker = ColorPicker(
            QColor(255, 0, 0, 128),
            self
        )

        if picker.exec():

            color = picker.get_color()

            fmt = QTextCharFormat()

            fmt.setFontUnderline(True)

            fmt.setUnderlineColor(color)

            self.apply_format(fmt)
    def load_styles(self, document):
        text = document["text"]
        style_runs = document["style_runs"]
        fonts = document["fonts"]

        for run in style_runs:
            start_byte = run["start"]
            length_byte = run["length"]

            start = len(text.encode("utf-8")[:start_byte].decode("utf-8"))
            end = len(
                text.encode("utf-8")[:start_byte + length_byte]
                .decode("utf-8")
            )

            style = run["style"]

            cursor = self.editor.textCursor()

            cursor.setPosition(start)
            cursor.setPosition(
                end,
                cursor.MoveMode.KeepAnchor
            )

            fmt = QTextCharFormat()

            font_id = style["font_id"]
            font_name = fonts[font_id]
            fmt.setForeground(QColor(
                style["text_color"][0],
                style["text_color"][1],
                style["text_color"][2],
                style["text_color"][3]
            ))
            fmt.setFontFamily(font_name)
            fmt.setFontPointSize(style["size"])

            fmt.setFontWeight(
                700 if style["bold"] else 400
            )

            fmt.setFontItalic(style["italic"])

            underline = style["underlined"]

            fmt.setFontUnderline(
                underline["enabled"]
            )

            if underline["enabled"]:
                color = underline["color"]

                fmt.setUnderlineColor(
                    QColor(
                        color[0],
                        color[1],
                        color[2],
                        color[3]
                    )
                )

            crossed = style["crossed"]

            fmt.setFontStrikeOut(
                crossed["enabled"]
            )

            cursor.mergeCharFormat(fmt)
def start_editor(document):
    app = QApplication(sys.argv)

    window = TextEditor(document)
    window.show()

    sys.exit(app.exec())

if __name__=="__main__":
    start_editor({
        "text": "Test text",
        "fonts": {},
        "style_runs": [],
        "version": 1
    })

