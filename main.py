import sys
import random
import numpy as np
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame,
                           QGraphicsView, QGraphicsScene, QGraphicsItem)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BarItem(QGraphicsItem):
    def __init__(self, value, x, y, width, height, color):
        super().__init__()
        self.value = value
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.setAcceptHoverEvents(True)
        
    def boundingRect(self):
        return QRectF(self.x, self.y, self.width, self.height)
        
    def paint(self, painter, option, widget):
        # Draw the bar
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        
        # Draw the value
        painter.setPen(QPen(QColor("#c77dff")))  # Changed to theme color
        painter.setFont(QFont("Arial", 8))
        text = str(self.value)
        text_width = painter.fontMetrics().width(text)
        text_x = int(self.x + self.width/2 - text_width/2)
        text_y = int(self.y - 5)
        painter.drawText(text_x, text_y, text)

class BinarySearchVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Binary Search Visualization")
        self.setMinimumSize(1000, 800)
        
        # Set window flags to customize title bar
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Set window background color and title bar style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QGraphicsView {
                background-color: #1a1a2e;
            }
            QMenuBar {
                background-color: #1a1a2e;
                color: #c77dff;
                border: none;
            }
            QMenuBar::item {
                background-color: #1a1a2e;
                color: #c77dff;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #5a189a;
                color: #c77dff;
            }
            QMenu {
                background-color: #1a1a2e;
                color: #c77dff;
                border: 1px solid #5a189a;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #5a189a;
                color: #c77dff;
            }
            QTitleBar {
                background-color: #1a1a2e;
            }
            QWidget#titleBar {
                background-color: #1a1a2e;
                border-bottom: 1px solid #5a189a;
            }
        """)
        
        # Create a custom title bar
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(30)
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        # Add title label
        title_label = QLabel("Binary Search Visualization")
        title_label.setStyleSheet("color: #c77dff; font-size: 14px;")
        self.title_bar_layout.addWidget(title_label)
        
        # Add window control buttons
        close_btn = QPushButton("````×````")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #c77dff;
                border: none;
                font-size: 20px;
                padding: 0px 5px;
            }
            QPushButton:hover {
                color: #ff4444;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        minimize_btn = QPushButton("−")
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #c77dff;
                border: none;
                font-size: 20px;
                padding: 0px 5px;
            }
            QPushButton:hover {
                color: #9d4edd;
            }
        """)
        minimize_btn.clicked.connect(self.showMinimized)
        
        self.title_bar_layout.addStretch()
        self.title_bar_layout.addWidget(minimize_btn)
        self.title_bar_layout.addWidget(close_btn)
        
        # Add title bar to window
        self.title_bar.setGeometry(0, 0, self.width(), 30)
        
        # Initialize variables
        self.array = []
        self.target = 0
        self.left = 0
        self.right = 0
        self.mid = 0
        self.current_step = 0
        self.start_time = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.update_timer = QTimer()  # New timer for real-time updates
        self.update_timer.timeout.connect(self.update_time)  # New method for time updates
        self.is_auto_playing = False
        self.search_history = []  # Store search history
        self.animation_delay = 500  # Default delay in milliseconds
        self.array_size = 15  # Default array size
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create control panel
        control_panel = QFrame()
        control_panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton {
                background-color: #5a189a;
                color: #c77dff;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #9d4edd;
            }
            QPushButton:disabled {
                background-color: #3c096c;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #5a189a;
                border-radius: 5px;
                font-size: 14px;
                background-color: #1a1a2e;
                color: #c77dff;
            }
            QLabel {
                font-size: 14px;
                color: #c77dff;
            }
        """)
        
        control_layout = QHBoxLayout(control_panel)
        
        # Create input field for array size
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("Array Size")
        self.size_input.setText("15")  # Default value
        self.size_input.setFixedWidth(80)  # Set fixed width
        control_layout.addWidget(QLabel("Size:"))
        control_layout.addWidget(self.size_input)
        
        # Create input field for target value
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target value")
        control_layout.addWidget(QLabel("Target:"))
        control_layout.addWidget(self.target_input)
        
        # Create delay input field with ms label
        delay_container = QWidget()
        delay_layout = QHBoxLayout(delay_container)
        delay_layout.setContentsMargins(0, 0, 0, 0)
        delay_layout.setSpacing(5)
        
        self.delay_input = QLineEdit()
        self.delay_input.setPlaceholderText("Delay")
        self.delay_input.setText("500")  # Default value
        self.delay_input.setFixedWidth(60)  # Set fixed width
        delay_layout.addWidget(self.delay_input)
        
        delay_label = QLabel("ms")
        delay_label.setStyleSheet("color: #c77dff;")
        delay_layout.addWidget(delay_label)
        
        control_layout.addWidget(QLabel("Speed:"))
        control_layout.addWidget(delay_container)
        
        # Create timing label
        self.timing_label = QLabel("Time: 0.0 ms")
        control_layout.addWidget(self.timing_label)
        
        # Create step counter label
        self.step_label = QLabel("Steps: 0")
        control_layout.addWidget(self.step_label)
        
        # Create buttons
        self.generate_btn = QPushButton("Generate Array")
        self.search_btn = QPushButton("Start Search")
        self.next_step_btn = QPushButton("Next Step")
        self.reset_btn = QPushButton("Reset")
        
        control_layout.addWidget(self.generate_btn)
        control_layout.addWidget(self.search_btn)
        control_layout.addWidget(self.next_step_btn)
        control_layout.addWidget(self.reset_btn)
        
        # Add control panel to main layout
        layout.addWidget(control_panel)
        
        # Create visualization widgets
        viz_layout = QHBoxLayout()
        
        # Create QGraphicsView for bar visualization
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setMinimumSize(500, 400)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        viz_layout.addWidget(self.view)
        
        # Create Matplotlib figure for step visualization
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumSize(400, 400)
        viz_layout.addWidget(self.canvas)
        
        layout.addLayout(viz_layout)
        
        # Connect signals
        self.generate_btn.clicked.connect(self.generate_array)
        self.search_btn.clicked.connect(self.start_search)
        self.next_step_btn.clicked.connect(self.next_step)
        self.reset_btn.clicked.connect(self.reset)
        
        # Initialize
        self.generate_array()
        
    def generate_array(self):
        # Stop any ongoing animation
        self.animation_timer.stop()
        self.update_timer.stop()
        
        # Clear the scene
        self.scene.clear()
        
        # Get array size from input
        try:
            self.array_size = int(self.size_input.text())
            if self.array_size < 5:  # Minimum size of 5
                self.array_size = 5
                self.size_input.setText("5")
            elif self.array_size > 100:  # Maximum size of 100
                self.array_size = 100
                self.size_input.setText("100")
        except ValueError:
            self.size_input.setText("15")  # Reset to default if invalid
            self.array_size = 15
        
        # Generate a random array of unique numbers between 1 and 100
        self.array = sorted(random.sample(range(1, 101), self.array_size))
        
        # Select a random target from the array
        self.target = random.choice(self.array)
        
        # Reset all variables
        self.left = 0
        self.right = len(self.array) - 1
        self.mid = 0
        self.current_step = 0
        self.start_time = 0
        self.search_history = []  # Clear search history
        
        # Update the target input field
        self.target_input.setText(str(self.target))
        
        # Update labels
        self.timing_label.setText("Time: 0.0 ms")
        self.step_label.setText("Steps: 0")
        
        # Reset button states
        self.next_step_btn.setEnabled(True)
        self.search_btn.setEnabled(True)
        
        # Clear and update the plot
        self.fig.clear()
        self.canvas.draw()
        
        # Update the visualization
        self.update_visualization()
        
        # Force a repaint of the view
        self.view.viewport().update()
        
    def next_step(self):
        if self.left <= self.right:
            self.mid = (self.left + self.right) // 2
            self.current_step += 1
            self.step_label.setText(f"Steps: {self.current_step}")
            
            # Add current state to history
            self.search_history.append((self.left, self.right, self.mid))
            
            # Stop the timer when using step button
            self.update_timer.stop()
            
            self.update_visualization()
            
            if self.array[self.mid] == self.target:
                self.show_result(True)
                self.next_step_btn.setEnabled(False)
            elif self.array[self.mid] < self.target:
                self.left = self.mid + 1
            else:
                self.right = self.mid - 1
        else:
            self.show_result(False)
            self.next_step_btn.setEnabled(False)
            
    def start_search(self):
        try:
            self.target = int(self.target_input.text())
            if self.target not in self.array:
                self.target_input.setText("Value not in array!")
                return
                
            # Get animation delay from input
            try:
                self.animation_delay = int(self.delay_input.text())
                if self.animation_delay < 50:  # Minimum delay of 50ms
                    self.animation_delay = 50
                    self.delay_input.setText("50")
                elif self.animation_delay > 2000:  # Maximum delay of 2000ms
                    self.animation_delay = 2000
                    self.delay_input.setText("2000")
            except ValueError:
                self.delay_input.setText("500")  # Reset to default if invalid
                self.animation_delay = 500
                
        except ValueError:
            self.target_input.setText("Invalid input!")
            return
            
        self.left = 0
        self.right = len(self.array) - 1
        self.current_step = 0
        self.start_time = time.time()
        self.next_step_btn.setEnabled(True)
        self.is_auto_playing = True
        self.search_history = []  # Clear search history when starting new search
        self.animation_timer.start(self.animation_delay)  # Use the specified delay
        self.update_timer.start(10)  # Update time every 10ms for smooth display
        
    def update_time(self):
        if self.start_time > 0:
            elapsed_time = (time.time() - self.start_time) * 1000
            self.timing_label.setText(f"Time: {elapsed_time:.1f} ms")

    def reset(self):
        self.left = 0
        self.right = len(self.array) - 1
        self.mid = 0
        self.current_step = 0
        self.animation_timer.stop()
        self.update_timer.stop()  # Stop the time update timer
        self.timing_label.setText("Time: 0.0 ms")
        self.step_label.setText("Steps: 0")
        self.next_step_btn.setEnabled(True)
        self.is_auto_playing = False
        self.search_history = []  # Clear search history
        self.update_visualization()
        
    def update_visualization(self):
        # Clear scene
        self.scene.clear()
        
        # Calculate dimensions
        width = self.view.width()
        height = self.view.height()
        bar_width = width / (len(self.array) + 1)
        bar_height = height * 0.8
        
        # Draw bars
        for i, value in enumerate(self.array):
            x = (i + 1) * bar_width
            y = height - (value / 100) * bar_height
            
            # Set color based on position with new color scheme
            if i == self.mid:
                color = QColor("#9d4edd")  # Vibrant Purple for mid
            elif self.left <= i <= self.right:
                color = QColor("#5a189a")  # Deep Purple for search range
            else:
                color = QColor("#000000")  # Black for others
                
            bar = BarItem(value, x - bar_width/2, y, bar_width - 2, height - y, color)
            self.scene.addItem(bar)
            
        # Update Matplotlib plot
        self.update_plot()
        
        # Force a repaint of the view
        self.view.viewport().update()
        
    def update_plot(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        # Set background color
        self.fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        
        # Plot search history
        for i, (left, right, mid) in enumerate(self.search_history):
            # Draw search range
            ax.plot([left, right], [i, i], color='#5a189a', linewidth=2, alpha=0.5)  # Deep Purple
            # Draw middle point
            ax.plot(mid, i, 'o', color='#9d4edd', markersize=8)  # Vibrant Purple
            # Add value at middle point
            ax.text(mid, i + 0.1, str(self.array[mid]), 
                   horizontalalignment='center', 
                   verticalalignment='bottom',
                   color='#5a189a',  # Deep Purple for text
                   fontsize=10)
        
        # Plot current state if there are steps
        if self.current_step > 0:
            # Draw current search range
            ax.plot([self.left, self.right], [self.current_step, self.current_step], 
                   color='#5a189a', linewidth=3, alpha=0.8)  # Deep Purple
            # Draw current middle point
            ax.plot(self.mid, self.current_step, 'o', color='#9d4edd', markersize=12)  # Vibrant Purple
            # Add current value
            ax.text(self.mid, self.current_step + 0.1, str(self.array[self.mid]), 
                   horizontalalignment='center', 
                   verticalalignment='bottom',
                   color='#5a189a',  # Deep Purple for text
                   fontsize=12)
            
        ax.set_title('Binary Search History', color='#5a189a')  # Deep Purple
        ax.set_xlabel('Array Index', color='#5a189a')  # Deep Purple
        ax.set_ylabel('Step Number', color='#5a189a')  # Deep Purple
        ax.tick_params(colors='#5a189a')  # Deep Purple
        ax.grid(True, alpha=0.2, color='#5a189a')  # Deep Purple
        
        # Set axis limits
        ax.set_ylim(-1, max(1, self.current_step + 1))
        ax.set_xlim(-1, len(self.array))
        
        # Set spines color
        for spine in ax.spines.values():
            spine.set_color('#5a189a')  # Deep Purple
        
        # Set the canvas background color
        self.canvas.setStyleSheet("background-color: #1a1a2e;")
        
        # Adjust layout to prevent scrollbars
        self.fig.tight_layout()
        
        self.canvas.draw()
        
    def show_result(self, found):
        # Add result text to scene
        text = self.scene.addText("Found!" if found else "Not Found!")
        text.setDefaultTextColor(QColor("#9d4edd" if found else "#000000"))  # Vibrant Purple for Found, Black for Not Found
        text.setFont(QFont("Arial", 20, QFont.Bold))
        text.setPos(self.view.width()/2 - text.boundingRect().width()/2, 20)

    def update_animation(self):
        if self.left <= self.right:
            self.mid = (self.left + self.right) // 2
            self.current_step += 1
            self.step_label.setText(f"Steps: {self.current_step}")
            
            # Add current state to history
            self.search_history.append((self.left, self.right, self.mid))
            
            self.update_visualization()
            
            if self.array[self.mid] == self.target:
                self.animation_timer.stop()
                self.update_timer.stop()  # Stop the time update timer
                self.show_result(True)
                self.next_step_btn.setEnabled(False)
            elif self.array[self.mid] < self.target:
                self.left = self.mid + 1
            else:
                self.right = self.mid - 1
        else:
            self.animation_timer.stop()
            self.update_timer.stop()  # Stop the time update timer
            self.show_result(False)
            self.next_step_btn.setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BinarySearchVisualizer()
    window.show()
    sys.exit(app.exec_())
