from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame,
                           QGraphicsView, QGraphicsScene, QGraphicsItem, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPalette
import random, sys


class ArrayElement(QGraphicsItem):
    def __init__(self, value, index, width, height, parent=None):
        super().__init__(parent)
        self.value = value
        self.index = index
        self.width = width
        self.height = height
        self.color = QColor("#4fc3f7")  # Default color
        self.setAcceptHoverEvents(True)
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(self.color))
        painter.drawRect(0, 0, int(self.width), int(self.height))
        
        # Draw value text
        painter.setPen(QPen(QColor("#e0e0e0")))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, self.width, self.height), Qt.AlignCenter, str(self.value))
        
        # Draw index text
        painter.drawText(QRectF(0, self.height + 2, self.width, 15), Qt.AlignCenter, str(self.index))


class BubbleSort(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bubble Sort Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Color scheme
        self.colors = {
            "background": QColor("#1e1e2f"),
            "default": QColor("#4fc3f7"),
            "comparing": QColor("#fbc02d"),
            "swapped": QColor("#81c784"),
            "sorted": QColor("#1976d2"),
            "text": QColor("#e0e0e0"),
            "button": QColor("#2d2d3f"),
            "button_hover": QColor("#3d3d5f"),
            "button_text": QColor("#e0e0e0"),
            "input_bg": QColor("#2d2d3f"),
            "input_border": QColor("#3d3d5f"),
            "panel_bg": QColor("#252538")
        }
        
        # Initialize variables
        self.array = []
        self.array_size = 15
        self.sorting = False
        self.current_step = 0
        self.steps = []
        self.delay = 500
        self.i = 0
        self.j = 0
        self.swapped = False
        self.iterations = 0
        self.total_iterations = 0
        
        # Setup UI
        self.setup_ui()
        self.apply_dark_theme()
        
        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        
    def apply_dark_theme(self):
        # Set application-wide dark theme
        app = QApplication.instance()
        palette = QPalette()
        
        # Set dark colors for the palette
        palette.setColor(QPalette.Window, self.colors["background"])
        palette.setColor(QPalette.WindowText, self.colors["text"])
        palette.setColor(QPalette.Base, self.colors["input_bg"])
        palette.setColor(QPalette.AlternateBase, self.colors["panel_bg"])
        palette.setColor(QPalette.ToolTipBase, self.colors["background"])
        palette.setColor(QPalette.ToolTipText, self.colors["text"])
        palette.setColor(QPalette.Text, self.colors["text"])
        palette.setColor(QPalette.Button, self.colors["button"])
        palette.setColor(QPalette.ButtonText, self.colors["button_text"])
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor("#4fc3f7"))
        palette.setColor(QPalette.Highlight, QColor("#1976d2"))
        palette.setColor(QPalette.HighlightedText, self.colors["text"])
        
        app.setPalette(palette)
        
        # Set stylesheet for additional styling
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e2f;
                color: #e0e0e0;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #2d2d3f;
                color: #e0e0e0;
                border: 1px solid #3d3d5f;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #3d3d5f;
                border: 2px solid #4fc3f7;
            }
            QPushButton:pressed {
                background-color: #4d4d6f;
            }
            QPushButton:disabled {
                background-color: #1d1d2f;
                color: #808080;
                border: 1px solid #2d2d2f;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12pt;
            }
            QLineEdit, QSpinBox {
                background-color: #2d2d3f;
                color: #e0e0e0;
                border: 1px solid #3d3d5f;
                border-radius: 4px;
                padding: 6px;
                font-size: 12pt;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                height: 0px;
            }
            QGraphicsView {
                background-color: #1e1e2f;
                border: 1px solid #3d3d5f;
                border-radius: 4px;
            }
        """)
        
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Control panel
        control_panel = QFrame()
        control_panel.setFrameShape(QFrame.StyledPanel)
        control_panel.setStyleSheet(f"background-color: {self.colors['panel_bg'].name()}; border-radius: 8px;")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(15, 15, 15, 15)
        
        # Array size input
        size_label = QLabel("Array Size:")
        self.size_input = QSpinBox()
        self.size_input.setRange(5, 100)
        self.size_input.setValue(15)
        self.size_input.valueChanged.connect(self.update_array_size)
        
        # Delay input
        delay_label = QLabel("Delay (ms):")
        self.delay_input = QSpinBox()
        self.delay_input.setRange(100, 5000)
        self.delay_input.setValue(500)
        self.delay_input.setSingleStep(100)
        self.delay_input.valueChanged.connect(self.update_delay)
        
        # Buttons
        self.generate_btn = QPushButton("Generate Array")
        self.generate_btn.clicked.connect(self.generate_array)
        
        self.start_btn = QPushButton("Start Sort")
        self.start_btn.clicked.connect(self.start_sort)
        self.start_btn.setEnabled(False)
        
        # Add controls to layout
        control_layout.addWidget(size_label)
        control_layout.addWidget(self.size_input)
        control_layout.addWidget(delay_label)
        control_layout.addWidget(self.delay_input)
        control_layout.addWidget(self.generate_btn)
        control_layout.addWidget(self.start_btn)
        control_panel.setLayout(control_layout)
        
        # Status panel with steps counter
        status_panel = QFrame()
        status_panel.setFrameShape(QFrame.StyledPanel)
        status_panel.setStyleSheet(f"background-color: {self.colors['panel_bg'].name()}; border-radius: 8px;")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        self.status_label = QLabel("Ready to generate array")
        self.status_label.setStyleSheet(f"color: {self.colors['text'].name()}; font-weight: bold;")
        
        self.steps_counter = QLabel("Steps: 0/0")
        self.steps_counter.setStyleSheet(f"color: {self.colors['text'].name()}; font-weight: bold;")
        
        self.iteration_counter = QLabel("Iteration: 0/0")
        self.iteration_counter.setStyleSheet(f"color: {self.colors['text'].name()}; font-weight: bold;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.iteration_counter)
        status_layout.addWidget(self.steps_counter)
        status_panel.setLayout(status_layout)
        
        # Graphics view for visualization
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(self.colors["background"])
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFrameShape(QFrame.NoFrame)
        
        # Add widgets to main layout
        main_layout.addWidget(control_panel)
        main_layout.addWidget(status_panel)
        main_layout.addWidget(self.view)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def update_array_size(self, value):
        self.array_size = value
        
    def update_delay(self, value):
        self.delay = value
        if self.timer.isActive():
            self.timer.setInterval(self.delay)
            
    def generate_array(self):
        # Clear previous array
        self.array = []
        self.scene.clear()
        
        # Generate new array
        max_value = 100
        if self.array_size > max_value:
            self.array_size = max_value
            self.size_input.setValue(max_value)
            
        self.array = random.sample(range(1, max_value + 1), self.array_size)
        
        # Draw array
        self.draw_array()
        
        # Reset sort state
        self.reset_sort_state()
        
        # Update UI
        self.status_label.setText("Array generated. Ready to sort.")
        self.steps_counter.setText("Steps: 0/0")
        self.start_btn.setEnabled(True)
        
        # Enable all controls
        self.enable_controls(True)
        
    def draw_array(self):
        self.scene.clear()
        
        if not self.array:
            return
            
        # Calculate bar dimensions
        view_width = self.view.width() - 20
        view_height = self.view.height() - 50
        bar_width = view_width / len(self.array)
        max_value = max(self.array)
        
        # Draw bars
        for i, value in enumerate(self.array):
            bar_height = (value / max_value) * view_height
            x = i * bar_width
            y = view_height - bar_height
            
            element = ArrayElement(value, i, bar_width - 2, bar_height)
            element.setPos(x, y)
            
            # Set color based on sort state
            if self.sorting:
                if self.current_step >= len(self.steps) - 1:
                    # Sorting is complete, color all bars green
                    element.color = self.colors["swapped"]
                elif i == self.i:
                    element.color = self.colors["comparing"]
                elif i == self.j:
                    element.color = self.colors["comparing"]
                elif i > len(self.array) - self.i - 1:
                    element.color = self.colors["sorted"]
                else:
                    element.color = self.colors["default"]
            else:
                # Default color when not sorting
                element.color = self.colors["default"]
                
            self.scene.addItem(element)
            
    def reset_sort_state(self):
        self.i = 0
        self.j = 0
        self.swapped = False
        self.sorting = False
        self.current_step = 0
        self.steps = []
        self.iterations = 0
        self.total_iterations = 0
        
        # Prepare steps for visualization
        if self.array:
            self.prepare_sort_steps()
            self.steps_counter.setText(f"Steps: 0/{len(self.steps)}")
            self.iteration_counter.setText(f"Iteration: 0/{self.total_iterations}")
            
    def prepare_sort_steps(self):
        self.steps = []
        n = len(self.array)
        arr_copy = self.array.copy()
        
        # Calculate total iterations
        self.total_iterations = 0
        for i in range(n):
            self.total_iterations += 1
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                self.steps.append((i, j, arr_copy.copy()))
                if arr_copy[j] > arr_copy[j + 1]:
                    arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                    swapped = True
                    self.steps.append((i, j, arr_copy.copy()))
            if not swapped:
                break
                
        # Add final step
        self.steps.append((n, 0, arr_copy.copy()))
            
    def reset(self):
        self.timer.stop()
        self.reset_sort_state()
        self.draw_array()
        self.status_label.setText("Sort reset. Ready to sort.")
        self.start_btn.setEnabled(True)
        
        # Enable all controls
        self.enable_controls(True)
        
    def enable_controls(self, enable):
        """Enable or disable all controls based on sort state"""
        self.size_input.setEnabled(enable)
        self.delay_input.setEnabled(enable)
        self.generate_btn.setEnabled(enable)
        self.start_btn.setEnabled(enable)
        
    def next_step(self):
        if not self.array or self.current_step >= len(self.steps):
            return
            
        # Get current step
        i, j, arr = self.steps[self.current_step]
        self.i = i
        self.j = j
        self.array = arr.copy()
        
        # Update iteration counter
        self.iteration_counter.setText(f"Iteration: {i+1}/{self.total_iterations}")
        
        # Update status
        if i < len(self.array):
            self.status_label.setText(f"Comparing elements at indices {j} and {j+1}")
        else:
            self.status_label.setText("Sorting complete!")
            self.timer.stop()
            
            # Enable controls when sorting is complete
            self.enable_controls(True)
            
        # Update steps counter
        self.steps_counter.setText(f"Steps: {self.current_step + 1}/{len(self.steps)}")
            
        # Draw updated array
        self.draw_array()
        
        # Move to next step
        self.current_step += 1
        
        # If not in step-by-step mode, continue with timer
        if self.timer.isActive():
            if self.current_step >= len(self.steps):
                self.timer.stop()
                self.start_btn.setEnabled(True)
                
                # Enable controls when sorting is complete
                self.enable_controls(True)
                
    def start_sort(self):
        if not self.array:
            return
            
        # Reset sort state
        self.reset_sort_state()
        
        # Start sort
        self.sorting = True
        self.start_btn.setEnabled(False)
        
        # Disable controls during sort
        self.enable_controls(False)
        
        # Start timer for animation
        self.timer.start(self.delay)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.draw_array()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BubbleSort()
    window.show()
    sys.exit(app.exec_())