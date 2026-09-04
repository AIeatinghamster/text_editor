import sys
import math

from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
    QLinearGradient,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
)




class HueRing(QWidget):

    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(280, 280)

        self.hue = 0


    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        cx = self.width() / 2
        cy = self.height() / 2

        radius = min(
            self.width(),
            self.height()
        ) / 2 - 15

        ring_width = 30

        pen = QPen()
        pen.setWidth(int(ring_width))

        for hue in range(360):

            color = QColor.fromHsv(
                hue,
                255,
                255
            )

            pen.setColor(color)
            painter.setPen(pen)

            start_angle = (90-hue) * 16
            span_angle = -16

            painter.drawArc(
                int(
                    cx - radius + ring_width / 2
                ),
                int(
                    cy - radius + ring_width / 2
                ),
                int(
                    (radius - ring_width / 2) * 2
                ),
                int(
                    (radius - ring_width / 2) * 2
                ),
                start_angle,
                span_angle
            )

        angle = math.radians(
            self.hue - 90
        )

        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius

        painter.setPen(
            QPen(
                Qt.GlobalColor.white,
                3
            )
        )

        painter.setBrush(
            QBrush(
                Qt.BrushStyle.NoBrush
            )
        )

        painter.drawEllipse(
            QPointF(x, y),
            8,
            8
        )

        painter.setPen(
            QPen(
                Qt.GlobalColor.black,
                1
            )
        )

        painter.drawEllipse(
            QPointF(x, y),
            10,
            10
        )


    def mousePressEvent(self, event):

        self.select_hue(
            event.position()
        )


    def mouseMoveEvent(self, event):

        if event.buttons() & Qt.MouseButton.LeftButton:

            self.select_hue(
                event.position()
            )


    def select_hue(self, pos):

        cx = self.width() / 2
        cy = self.height() / 2

        dx = pos.x() - cx
        dy = pos.y() - cy

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        radius = min(
            self.width(),
            self.height()
        ) / 2 - 15

        if not (
            radius - 20
            <
            distance
            <
            radius + 20
        ):
            return

        angle = math.degrees(
            math.atan2(dy, dx)
        )

        hue = int(
            (angle + 90) % 360
        )

        self.hue = hue

        self.update()

        self.colorChanged.emit(
            QColor.fromHsv(
                self.hue,
                255,
                255
            )
        )


class SVSquare(QWidget):

    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setMinimumSize(
            220,
            220
        )

        self.hue = 0
        self.saturation = 255
        self.value = 255


    def set_hue(self, hue):

        self.hue = hue

        self.update()


    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        w = self.width()
        h = self.height()

        
        hue_color = QColor.fromHsv(
            self.hue,
            255,
            255
        )

        horizontal = QLinearGradient(
            0,
            0,
            w,
            0
        )

        horizontal.setColorAt(
            0,
            QColor(255, 255, 255)
        )

        horizontal.setColorAt(
            1,
            hue_color
        )

        painter.fillRect(
            0,
            0,
            w,
            h,
            horizontal
        )

     

        vertical = QLinearGradient(
            0,
            0,
            0,
            h
        )

        vertical.setColorAt(
            0,
            QColor(0, 0, 0, 0)
        )

        vertical.setColorAt(
            1,
            QColor(0, 0, 0, 255)
        )

        painter.fillRect(
            0,
            0,
            w,
            h,
            vertical
        )

       

        x = (
            self.saturation / 255
        ) * w

        y = (
            1 - self.value / 255
        ) * h

        painter.setBrush(
            QBrush(
                Qt.BrushStyle.NoBrush
            )
        )

        painter.setPen(
            QPen(
                Qt.GlobalColor.black,
                2
            )
        )

        painter.drawEllipse(
            QPointF(x, y),
            8,
            8
        )

        painter.setPen(
            QPen(
                Qt.GlobalColor.white,
                2
            )
        )

        painter.drawEllipse(
            QPointF(x, y),
            5,
            5
        )


    def mousePressEvent(self, event):

        self.select_color(
            event.position()
        )


    def mouseMoveEvent(self, event):

        if event.buttons() & Qt.MouseButton.LeftButton:

            self.select_color(
                event.position()
            )


    def select_color(self, pos):

        x = max(
            0,
            min(
                self.width(),
                pos.x()
            )
        )

        y = max(
            0,
            min(
                self.height(),
                pos.y()
            )
        )

        self.saturation = int(
            (x / self.width()) * 255
        )

        self.value = int(
            (1 - y / self.height()) * 255
        )

        self.update()

        color = QColor.fromHsv(
            self.hue,
            self.saturation,
            self.value
        )

        self.colorChanged.emit(color)




class AlphaSlider(QSlider):

    def __init__(self, parent=None):

        super().__init__(
            Qt.Orientation.Horizontal,
            parent
        )

        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(255)



class ColorPicker(QDialog):

    def __init__(
        self,
        initial_color=QColor(
            255,
            0,
            0,
            255
        ),
        parent=None
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "Choose Color"
        )

        self.resize(
            520,
            550
        )

        self.current_color = QColor(
            initial_color
        )

        self.selected_color = QColor(
            initial_color
        )

        

        layout = QVBoxLayout(self)

        

        controls = QHBoxLayout()

        self.hue_ring = HueRing()
        self.sv_square = SVSquare()

        controls.addWidget(
            self.hue_ring
        )

        controls.addWidget(
            self.sv_square
        )

        layout.addLayout(
            controls
        )

        

        layout.addWidget(
            QLabel("Alpha")
        )

        self.alpha_slider = AlphaSlider()

        self.alpha_slider.setValue(
            initial_color.alpha()
        )

        layout.addWidget(
            self.alpha_slider
        )

        

        layout.addWidget(
            QLabel("Preview")
        )

        self.preview = QLabel()

        self.preview.setMinimumHeight(
            60
        )

        layout.addWidget(
            self.preview
        )

        

        buttons = QHBoxLayout()

        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")

        ok.clicked.connect(
            self.accept
        )

        cancel.clicked.connect(
            self.reject
        )

        buttons.addWidget(ok)
        buttons.addWidget(cancel)

        layout.addLayout(buttons)

        
        self.hue_ring.colorChanged.connect(
            self.hue_changed
        )

        self.sv_square.colorChanged.connect(
            self.sv_changed
        )

        self.alpha_slider.valueChanged.connect(
            self.alpha_changed
        )

        

        hue = initial_color.hue()

        if hue < 0:
            hue = 0

        saturation = initial_color.saturation()
        value = initial_color.value()

        self.hue_ring.hue = hue

        self.sv_square.hue = hue
        self.sv_square.saturation = saturation
        self.sv_square.value = value

        self.hue_ring.update()
        self.sv_square.update()

        self.update_preview()


    

    def hue_changed(self, color):

        hue = color.hue()

        if hue < 0:
            hue = 0

        self.hue_ring.hue = hue

        self.sv_square.set_hue(
            hue
        )

        self.update_color()


    

    def sv_changed(self, color):

        self.update_color()


   

    def alpha_changed(self, alpha):

        self.current_color.setAlpha(
            alpha
        )

        self.update_preview()




    def update_color(self):

        self.current_color = QColor.fromHsv(
            self.sv_square.hue,
            self.sv_square.saturation,
            self.sv_square.value,
            self.alpha_slider.value()
        )

        self.update_preview()


    

    def update_preview(self):

        c = self.current_color

        width = max(
            self.preview.width(),
            1
        )

        height = max(
            self.preview.height(),
            1
        )

        pixmap = QPixmap(
            width,
            height
        )

        pixmap.fill(
            Qt.GlobalColor.white
        )

        painter = QPainter(
            pixmap
        )

        size = 10

        for y in range(
            0,
            height,
            size
        ):

            for x in range(
                0,
                width,
                size
            ):

                if (
                    (x // size + y // size)
                    % 2
                    == 0
                ):
                    checker = QColor(
                        230,
                        230,
                        230
                    )
                else:
                    checker = QColor(
                        255,
                        255,
                        255
                    )

                painter.fillRect(
                    x,
                    y,
                    size,
                    size,
                    checker
                )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QBrush(c)
        )

        painter.drawRect(
            0,
            0,
            width,
            height
        )

        painter.end()

        self.preview.setPixmap(
            pixmap
        )


   
    def accept(self):

        self.selected_color = QColor(
            self.current_color
        )

        super().accept()


    
    def get_color(self):

        return QColor(
            self.selected_color
        )




if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    picker = ColorPicker(
        QColor(
            255,
            0,
            0,
            128
        )
    )

    if picker.exec():

        color = picker.get_color()

        print(
            "RGBA:",
            color.red(),
            color.green(),
            color.blue(),
            color.alpha()
        )

    sys.exit(
        app.exec()
    )
