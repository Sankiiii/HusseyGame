import pyttsx3  
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QFrame, QLabel, 
    QMainWindow, QPushButton, QVBoxLayout, QGridLayout, 
    QWidget, QSpacerItem, QSizePolicy, QHBoxLayout,QMessageBox,QInputDialog
)
import sys
import random

class NumberGrid(QFrame):
    numberClicked = Signal(int)  

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QGridLayout(self)
        layout.setSpacing(10)
        
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.buttonClicked.connect(self._handleButtonClick)
        for i in range(1, 91):  
            button = QPushButton(str(i))
            button.setFixedSize(61, 51)
            button.setFont(QFont(None, 13))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 20px;
                    font-size: 2.3em;
                    padding: 10px 20px;
                    border: none;
                }
                QPushButton:hover { 
                    background-color: #45a049;
                    transform: scale(1.05);
                    transition: transform 0.2s;
                }
                QPushButton:pressed { background-color: #367c39; }
                QPushButton:disabled { background-color: #BDBDBD; }  /* Grey when disabled */
            """)
            
            row = (i - 1) // 10
            col = (i - 1) % 10
            layout.addWidget(button, row, col)
            self.buttonGroup.addButton(button, i)

    def _handleButtonClick(self, button):
        number = int(button.text())
        self.numberClicked.emit(number)
        button.setEnabled(False)  
        button.setStyleSheet("""
            QPushButton {
                background-color: #BDBDBD;  /* Grey color */
                color: white;
                border-radius: 20px;
                font-size: 2.3em;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:pressed { background-color: #FF5722; }  /* Red when pressed */
            QPushButton:disabled { background-color: #FA4032; }  /* Grey when disabled */
        """)

    def reset(self):
        """Reset all buttons to enabled state"""
        for button in self.buttonGroup.buttons():
            button.setEnabled(True)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 20px;
                    font-size: 2.3em;
                    padding: 10px 20px;
                    border: none;
                }
                QPushButton:hover { 
                    background-color: #45a049;
                    transform: scale(1.05);
                    transition: transform 0.2s;
                }
                QPushButton:pressed { background-color: #367c39; }
                QPushButton:disabled { background-color: #BDBDBD; }
            """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

       
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150) 
        self.engine.setProperty('volume', 1) 

    def initUI(self):
        self.setWindowTitle("Number Grid Game")
        self.setMinimumSize(800, 750)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        
        topSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(topSpacer)

       
        self.scoreLabel = QLabel("Current Token : 0")
        self.scoreLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scoreLabel.setStyleSheet("font-size: 24px; color: #4CAF50;")
        layout.addWidget(self.scoreLabel)

        # Spacer between score and grid
        layout.addSpacing(20)

        # Tokens remaining label
        self.tokensRemainingLabel = QLabel("Tokens Remaining: 0")
        self.tokensRemainingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tokensRemainingLabel.setStyleSheet("font-size: 20px; color: #FF5722;")
        layout.addWidget(self.tokensRemainingLabel)

        # Spacer between tokens and grid
        layout.addSpacing(20)

        # Number grid
        self.numberGrid = NumberGrid()
        self.numberGrid.numberClicked.connect(self.handleNumberClick)
        layout.addWidget(self.numberGrid)

        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(15) 
        
       
        genratebutton = QPushButton("Generate number")
        genratebutton.clicked.connect(self.generateNumber)
        genratebutton.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        buttonLayout.addWidget(genratebutton)

        # Start Auto Generation Button
        startButton = QPushButton("Start Auto-Generate")
        startButton.clicked.connect(self.startAutoGenerate)
        startButton.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        buttonLayout.addWidget(startButton)

        # Stop Auto Generation Button
        stopButton = QPushButton("Stop Auto-Generate")
        stopButton.clicked.connect(self.stopAutoGenerate)
        stopButton.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        buttonLayout.addWidget(stopButton)

        # Reset Game Button
        resetButton = QPushButton("Reset Game")
        resetButton.clicked.connect(self.resetGame)
        resetButton.setStyleSheet("""
            QPushButton {
                background-color: #8BC34A;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #7CB342; }
        """)
        buttonLayout.addWidget(resetButton)

        layout.addLayout(buttonLayout)

        bottomSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(bottomSpacer)

        self.score = 0
        self.tokensRemaining = 90  

        self.autoGenerateTimer = QTimer(self)
        self.autoGenerateTimer.timeout.connect(self.autoGenerateNumber)
        self.autoGenerateActive = False

    def handleNumberClick(self, number):
        if self.tokensRemaining > 0:  # Only allow actions if tokens remain
            self.score = number
            self.scoreLabel.setText(f"Current Token : {self.score}")
            
            self.tokensRemaining -= 1
            self.tokensRemainingLabel.setText(f"Tokens Remaining: {self.tokensRemaining}")

            # Announce the selected number
            self.announceNumber(number)
            
            if self.tokensRemaining == 0:
                name, ok = QInputDialog.getText(self, "Enter Your Name", "Please enter your name:")

        if ok and name:
            # If the user entered a name, show a congratulations message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Congratulations!")
                msg.setText(f"Congratulations, {name}! You are the winner!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                self.stopAutoGenerate()

    def announceNumber(self, number):
        self.engine.say(str(number))  # Text to be spoken
        self.engine.runAndWait()  # Wait until the speech is finished

    def generateNumber(self):
        if self.tokensRemaining > 0:  # Only generate a number if tokens are remaining
            # Generate a random number between 1 and 90
            number = random.randint(1, 90)

            # Find the button corresponding to the number that hasn't been clicked
            button = self.numberGrid.buttonGroup.buttons()[number - 1]

            # If the button is enabled, click it
            if button.isEnabled():
                self.numberGrid._handleButtonClick(button)
            else:
                # If the button is already clicked, try again
                self.generateNumber()

    def autoGenerateNumber(self):
        if self.tokensRemaining > 0:  # Only generate a number if tokens are remaining
            number = random.randint(1, 90)

            # Find the button corresponding to the number
            button = self.numberGrid.buttonGroup.buttons()[number - 1]

            # If the button is enabled, click it
            if button.isEnabled():
                self.numberGrid._handleButtonClick(button)
            else:
                # If the button is already clicked, try again
                self.autoGenerateNumber()
            
    def startAutoGenerate(self):
        if not self.autoGenerateActive:
            self.autoGenerateTimer.start()  
            self.autoGenerateActive = True

    def stopAutoGenerate(self):
        if self.autoGenerateActive:
            self.autoGenerateTimer.stop()
            self.autoGenerateActive = False

    def resetGame(self):
        self.score = 0
        self.tokensRemaining = 90
        self.scoreLabel.setText("Current token : 0")
        self.tokensRemainingLabel.setText(f"Tokens Remaining: {self.tokensRemaining}")
        self.numberGrid.reset()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
