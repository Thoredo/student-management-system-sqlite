from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QMainWindow,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QComboBox,
)
from PyQt6.QtGui import QAction
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Add menu bar items
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add an add student option to file menu
        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert_student)
        file_menu_item.addAction(add_student_action)

        # Add about option to help menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        # Add search option to Edit menu
        search_action = QAction("Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(
                    row_number, column_number, QTableWidgetItem(str(data))
                )

    def insert_student(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of Courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
            (name, course, mobile),
        )
        connection.commit()
        cursor.close()
        connection.close()
        student_management.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add Search Widget
        self.searched_name = QLineEdit()
        self.searched_name.setPlaceholderText("Search")
        layout.addWidget(self.searched_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        button.setStyleSheet("QPushButton {background-color: #0000FF; color: white;}")
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.searched_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        items = student_management.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            student_management.table.item(item.row(), 1).setSelected(True)


app = QApplication(sys.argv)
student_management = MainWindow()
student_management.show()
student_management.load_data()
sys.exit(app.exec())
