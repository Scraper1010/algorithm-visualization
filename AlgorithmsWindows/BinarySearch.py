from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame,
                           QGraphicsView, QGraphicsScene, QGraphicsItem, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPalette
import random, sys


class BarItem(QGraphicsItem): 
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


class BinarySearch(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Binary Search Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Color scheme
        self.colors = {
            "background": QColor("#1e1e2f"),
            "default": QColor("#4fc3f7"),
            "left_range": QColor("#1976d2"),
            "right_range": QColor("#0288d1"),
            "mid_element": QColor("#fbc02d"),
            "found_element": QColor("#81c784"),
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
        self.target = 0
        self.delay = 1000
        self.left = 0
        self.right = 0
        self.mid = 0
        self.found = False
        self.searching = False
        self.step_by_step = False
        self.current_step = 0
        self.steps = []
        
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
                border: 1px solid #2d2d3f;
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
        
        # Target input
        target_label = QLabel("Target:")
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target value")
        
        # Delay input
        delay_label = QLabel("Delay (ms):")
        self.delay_input = QSpinBox()
        self.delay_input.setRange(100, 5000)
        self.delay_input.setValue(1000)
        self.delay_input.setSingleStep(100)
        self.delay_input.valueChanged.connect(self.update_delay)
        
        # Buttons
        self.generate_btn = QPushButton("Generate Array")
        self.generate_btn.clicked.connect(self.generate_array)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)
        
        self.start_btn = QPushButton("Start Search")
        self.start_btn.clicked.connect(self.start_search)
        self.start_btn.setEnabled(False)
        
        # Add controls to layout
        control_layout.addWidget(size_label)
        control_layout.addWidget(self.size_input)
        control_layout.addWidget(target_label)
        control_layout.addWidget(self.target_input)
        control_layout.addWidget(delay_label)
        control_layout.addWidget(self.delay_input)
        control_layout.addWidget(self.generate_btn)
        control_layout.addWidget(self.reset_btn)
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
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
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
        # Fix for the random.sample error - ensure we don't try to sample more than available
        max_value = 100
        if self.array_size > max_value:
            self.array_size = max_value
            self.size_input.setValue(max_value)
            
        self.array = random.sample(range(1, max_value + 1), self.array_size)
        self.array.sort()  # Binary search requires sorted array
        
        # Set target to largest number by default
        self.target = self.array[-1]
        self.target_input.setText(str(self.target))
        
        # Draw array
        self.draw_array()
        
        # Reset search state
        self.reset_search_state()
        
        # Update UI
        self.status_label.setText("Array generated. Ready to search.")
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
            
            bar = BarItem(value, i, bar_width - 2, bar_height)
            bar.setPos(x, y)
            
            # Set color based on search state
            if self.found and value == self.target:
                # Found element - highlight in green (highest priority)
                bar.color = self.colors["found_element"]
            elif self.searching:
                if i == self.mid:
                    bar.color = self.colors["mid_element"]
                elif self.left <= i <= self.right:
                    if i == self.left:
                        bar.color = self.colors["left_range"]
                    elif i == self.right:
                        bar.color = self.colors["right_range"]
                    else:
                        bar.color = self.colors["default"]
                else:
                    bar.color = QColor(100, 100, 100)  # Dimmed
            else:
                # Default color when not searching
                bar.color = self.colors["default"]
                
            self.scene.addItem(bar)
            
    def reset_search_state(self):
        self.left = 0
        self.right = len(self.array) - 1
        self.mid = 0
        self.found = False
        self.searching = False
        self.step_by_step = False
        self.current_step = 0
        self.steps = []
        
        # Prepare steps for visualization
        if self.array:
            self.prepare_search_steps()
            self.steps_counter.setText(f"Steps: 0/{len(self.steps)}")
            
    def prepare_search_steps(self):
        self.steps = []
        left, right = 0, len(self.array) - 1
        
        while left <= right:
            mid = (left + right) // 2
            self.steps.append((left, mid, right))
            
            if self.array[mid] == self.target:
                break
            elif self.array[mid] < self.target:
                left = mid + 1
            else:
                right = mid - 1
                
        # If we've gone through all steps and haven't found the target,
        # add a final step to indicate the search is complete
        if not self.found and self.steps:
            self.steps.append((left, mid, right))
            
    def reset(self):
        self.timer.stop()
        self.reset_search_state()
        self.draw_array()
        self.status_label.setText("Search reset. Ready to search.")
        self.start_btn.setEnabled(True)
        
        # Enable all controls
        self.enable_controls(True)
        
    def enable_controls(self, enable):
        """Enable or disable all controls based on search state"""
        self.size_input.setEnabled(enable)
        self.target_input.setEnabled(enable)
        self.delay_input.setEnabled(enable)
        self.generate_btn.setEnabled(enable)
        self.reset_btn.setEnabled(enable)
        
    def next_step(self):
        if not self.array or self.current_step >= len(self.steps):
            return
            
        # Get current step
        left, mid, right = self.steps[self.current_step]
        self.left = left
        self.mid = mid
        self.right = right
        
        # Update status
        if self.array[mid] == self.target:
            self.found = True
            self.status_label.setText(f"Found {self.target} at index {mid}")
            self.timer.stop()
            
            # Enable controls when search is complete
            self.enable_controls(True)
        elif self.array[mid] < self.target:
            self.status_label.setText(f"Checking index {mid}: {self.array[mid]} < {self.target}, searching right half")
        else:
            self.status_label.setText(f"Checking index {mid}: {self.array[mid]} > {self.target}, searching left half")
            
        # Update steps counter
        self.steps_counter.setText(f"Steps: {self.current_step + 1}/{len(self.steps)}")
            
        # Draw updated array
        self.draw_array()
        
        # Move to next step
        self.current_step += 1
        
        # If not in step-by-step mode, continue with timer
        if not self.step_by_step and self.timer.isActive():
            if self.current_step >= len(self.steps):
                self.timer.stop()
                self.start_btn.setEnabled(True)
                
                # Check if target was found
                if not self.found:
                    self.status_label.setText(f"Target {self.target} not found in the array")
                
                # Enable controls when search is complete
                self.enable_controls(True)
                
    def start_search(self):
        if not self.array:
            return
            
        # Get target from input
        try:
            self.target = int(self.target_input.text())
        except ValueError:
            self.status_label.setText("Invalid target value. Please enter a number.")
            return
            
        # Reset search state
        self.reset_search_state()
        
        # Start search
        self.searching = True
        self.start_btn.setEnabled(False)
        
        # Disable controls during search
        self.enable_controls(False)
        
        # Start timer for animation
        self.timer.start(self.delay)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.draw_array()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BinarySearch()
    window.show()
    sys.exit(app.exec_())