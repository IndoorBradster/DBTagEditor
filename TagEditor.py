import os
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout, QLabel, QMainWindow, QGraphicsView, QGraphicsScene, QHBoxLayout
from PyQt5.QtGui import QPalette, QColor, QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal

class CustomTextEditBox(QTextEdit):
    keyEvent = pyqtSignal(str)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.keyEvent.emit('PageUp')
        elif event.key() == Qt.Key_PageDown:
            self.keyEvent.emit('PageDown')
        else:
            super().keyPressEvent(event)

class TextEditor(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window size and title
        self.setWindowTitle("DB Image Tag Editor")
        self.setGeometry(100, 100, 800, 600)

        # Create label to display the image
        self.image_label = QLabel()
        self.image_label.setFixedSize(500, 500)
        self.image_label.setStyleSheet("background-color: black")

        # Create horizontal layout for the window
        self.horizontal_layout = QHBoxLayout()
        self.image_view = QGraphicsView()
        self.image_scene = QGraphicsScene()
        self.image_view.setScene(self.image_scene)
        self.horizontal_layout.addWidget(self.image_view)

        # Set up the UI elements
        self.file_label = QLabel()
        font = self.file_label.font()
        font.setPointSize(14)
        self.file_label.setFont(font)
        self.text_edit = CustomTextEditBox()
        self.text_edit.setFocusPolicy(Qt.StrongFocus)
        font = self.text_edit.font()
        font.setPointSize(14)
        self.text_edit.setFont(font)
        self.text_edit.textChanged.connect(self.text_changed)
        self.text_edit.setFocusPolicy(Qt.StrongFocus)
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_text)

        # Set save button size
        self.save_button.setFixedHeight(100)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.file_label)
        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)


        self.file_pairs = []
        for file_name in os.listdir('.'):
            if file_name.endswith('.txt'):
                # Check if there is a matching .jpg file
                jpg_file = os.path.join('.', file_name.replace('.txt', '.jpg'))
                if os.path.exists(jpg_file):
                    self.file_pairs.append((os.path.join('.', file_name), jpg_file))

        # Find the first text file in the directory and load it into the QTextEdit widget
        self.current_file_path = None

        # Find the first text file in the file_pairs list and load it into the QTextEdit widget
        self.current_file_index = 0
        self.current_file_path = self.file_pairs[self.current_file_index][0]

        if self.current_file_path is not None:
            with open(self.current_file_path, 'r') as f:
                text = f.read()
                self.text_edit.setText(text)
                self.update_file_label()
                self.open_image()

        # Handle key presses from inside the QTextEdit widget
        self.text_edit.keyEvent.connect(self.swapFile)

    # Handle key presses from outside the QTextEdit widget
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.swapFile('PageUp')
        elif event.key() == Qt.Key_PageDown:
            self.swapFile('PageDown')

    # Swap the current file being worked on
    def swapFile(self, keyName):
        if keyName == 'PageUp':
            if self.current_file_index < len(self.file_pairs)-1:
                self.current_file_index += 1
            else:
                self.current_file_index = 0
        elif keyName == 'PageDown':
            if self.current_file_index > 0:
                self.current_file_index -= 1
            else:
                self.current_file_index = len(self.file_pairs)-1
        self.current_file_path = self.file_pairs[self.current_file_index][0]
        
        self.open_file()

    # Update the file label to display the title of the currently open text file
    def update_file_label(self):
        file_name = os.path.basename(self.current_file_path)
        self.file_label.setText(file_name)
        self.file_label_palette = self.file_label.palette()
        self.file_label_palette.setColor(QPalette.WindowText, QColor('black'))
        self.file_label.setPalette(self.file_label_palette)

    # Save the text in the QTextEdit widget back to the file, updating the file label to black
    def save_text(self):
        with open(self.current_file_path, 'w') as f:
            f.write(self.text_edit.toPlainText())
        self.update_file_label()

    # Open the text file and display the image
    def open_file(self):
        with open(self.current_file_path, 'r') as f:
            text = f.read()
            self.text_edit.setText(text)
            self.update_file_label()
            self.open_image()
            self.setFocus()

    # Change the color of the file label to orange when the text is edited
    def text_changed(self):
        self.file_label_palette = self.file_label.palette()
        self.file_label_palette.setColor(QPalette.WindowText, QColor('orange'))
        self.file_label.setPalette(self.file_label_palette)

    # Open the image associated with the text file
    def open_image(self):
        #If the image window has not been created yet, create it
        if not hasattr(self, 'image_window'):
            # Create a new QMainWindow to display the image separately from the text editor
            self.image_window = QMainWindow()
            self.image_view = QGraphicsView()
            self.image_scene = QGraphicsScene()
            self.image_view.setScene(self.image_scene)
            self.image_window.setCentralWidget(self.image_view)
            self.image_window.setStyleSheet("background-color: #303030;")

        # get current position and size of the image window
        pos = self.image_window.saveGeometry()

        # clear the image scene if there is already an image in it
        if self.image_scene.items():
            self.image_scene.clear()

        # Open the image with the same name as the text file
        image_path = self.file_pairs[self.current_file_index][1]

        # set the window title to the image name
        self.image_window.setWindowTitle(os.path.basename(image_path))

        if os.path.exists(image_path):
            # Load the image into a QImage object and add it to the QGraphicsScene
            image = QImage(image_path)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                
                pixmap = pixmap.scaled(self.image_window.width()-50, self.image_window.height()-50, Qt.KeepAspectRatio)
                # adjust scene to be the same size as the image
                self.image_scene.setSceneRect(0, 0, self.image_window.width()-50, self.image_window.height()-50)
                self.image_scene.addPixmap(pixmap)

                # restore the position and size of the image window
                self.image_window.restoreGeometry(pos)

        # Show the image window if it is not already visible
        if not self.image_window.isVisible():
            self.image_window.show()


if __name__ == '__main__':
    app = QApplication([])
    window = TextEditor()
    window.show()
    app.exec_()
