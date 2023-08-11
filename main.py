from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QMainWindow,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QComboBox,
    QToolBar,
    QStatusBar,
    QMessageBox,
)
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class Database:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # Add menu bar items
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add an add student option to file menu
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert_student)
        file_menu_item.addAction(add_student_action)

        # Add about option to help menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # Add search option to Edit menu
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search_student)
        edit_menu_item.addAction(search_action)

        # Add table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        # Add toolbar elements
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create statusbar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def load_data(self):
        # Load the data from our database
        connection = Database().connect()
        result = connection.execute("SELECT * FROM students")

        # Add the data to the main window table
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

    def search_student(self):
        dialog = SearchDialog()
        dialog.exec()

    def cell_clicked(self):
        # Create edit button
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit_record)

        # Create delete button
        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete_record)

        # Prevent duplicate buttons when clicking other cell
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # Add buttons to statusbar
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def edit_record(self):
        dialog = EditDialog()
        dialog.exec()

    def delete_record(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
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

        # Add a register button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        button.clicked.connect(self.close)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        # Define value variables
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        # Establish database connection
        connection = Database().connect()
        cursor = connection.cursor()

        # Add values to our database and close the connection
        cursor.execute(
            "INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
            (name, course, mobile),
        )
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the mainwindow table
        student_management.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add search input
        self.searched_name = QLineEdit()
        self.searched_name.setPlaceholderText("Search")
        layout.addWidget(self.searched_name)

        # Add search button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        button.setStyleSheet("QPushButton {background-color: #0000FF; color: white;}")
        button.clicked.connect(self.close)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.searched_name.text()
        items = student_management.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            student_management.table.item(item.row(), 1).setSelected(True)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = student_management.table.currentRow()
        student_name = student_management.table.item(index, 1).text()

        # Edit student name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combobox of courses
        course_name = student_management.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile = student_management.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Get student id from selected row
        self.student_id = student_management.table.item(index, 0).text()

        # Add update button
        button = QPushButton("update")
        button.clicked.connect(self.update_student)
        button.clicked.connect(self.close)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        # Define value variables
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        # Establish connection
        connection = Database().connect()
        cursor = connection.cursor()

        # Update given values and close connection
        cursor.execute(
            "UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
            (name, course, mobile, self.student_id),
        )
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh table
        student_management.load_data()

        # Remove status bar buttons till new cell is clicked
        children = student_management.findChildren(QPushButton)
        if children:
            for child in children:
                student_management.statusbar.removeWidget(child)


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")

        # Define widgets for the dialog
        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")

        # Add widgets to dialog
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)
        self.setLayout(layout)

        # Make dialog window close when user clicks yes or no
        yes_button.clicked.connect(self.delete_student)
        yes_button.clicked.connect(self.close)
        no_button.clicked.connect(self.close)

    def delete_student(self):
        # Get index and student id from selected row
        index = student_management.table.currentRow()
        student_id = student_management.table.item(index, 0).text()

        # Establish connection
        connection = Database().connect()
        cursor = connection.cursor()

        # Delete selected student from database and close connection
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh table
        student_management.load_data()

        # Add confirmation message after succesfull deletion
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was delete succesfully!")
        confirmation_widget.exec()

        # Remove status bar buttons till new cell is clicked
        children = student_management.findChildren(QPushButton)
        if children:
            for child in children:
                student_management.statusbar.removeWidget(child)


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
This app was created during the course "The Python Mega Course".
Feel free to modify and reuse this app.
"""
        self.setText(content)


app = QApplication(sys.argv)
student_management = MainWindow()
student_management.show()
student_management.load_data()
sys.exit(app.exec())
