import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QFont, QIntValidator
import pandas as pd
import mysql.connector

fields = ('Student_Name', 'Roll_No', 'Accounts_Marks', 'Business_Studies_Marks', 'Economics_Marks', 'Informatics_Marks', 'English_Marks')

class StudentReportCard(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def validateEntry(self, text):
        if not text.isdigit():
            sender = self.sender()
            cursor_position = sender.cursorPosition()
            if cursor_position > 0:
                sender.setText(sender.text().rstrip(sender.text()[cursor_position - 1]))  # Remove non-numeric characters
                sender.setCursorPosition(cursor_position - 1)  # Adjust cursor position
            else:
                sender.setText('')  # If cursor position is at index 0, clear the QLineEdit

    def initUI(self):
        self.setWindowTitle('Students Report Card Generator')
        self.setGeometry(600, 200, 950, 600)
        self.setWindowIcon(QIcon('D:/My_Projects/logo.jpg'))

        heading_label = QLabel('SSSHSS Report Card Generation', self)
        heading_label.setGeometry(200, 50, 10000000, 90)
        font = heading_label.font()
        font.setPointSize(17)
        font.setBold(True)
        heading_label.setFont(font)

        # Add image
        image_label = QLabel(self)
        image_label.setGeometry(50, 50, 100, 100)
        pixmap = QPixmap('D:/My_Projects/logo.jpg')
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)

        self.entries = {}

        # Initial y-coordinate for the first field
        y_coordinate = 200

        for field in fields:
            # Replace underscores with spaces in displayed labels only
            displayed_field_name = field.replace('_', ' ')
            label = QLabel(displayed_field_name + ':', self)
            label.setGeometry(30, y_coordinate, 800, 30)  # Adjusted width of labels
            font = QFont()
            font.setPointSize(12)  # Increased font size
            label.setFont(font)

            entry = QLineEdit(self)
            entry.setGeometry(360, y_coordinate, 400, 35)  # Adjusted width of entry fields
            if field == 'Roll_No' or 'Marks' in field:
                entry.setValidator(QIntValidator())  # Allow only integers for age and marks fields

            entry_font = QFont()
            entry_font.setPointSize(16)  # Set font size
            entry.setFont(entry_font)
            self.entries[field] = entry

            # Increment y-coordinate for the next field
            y_coordinate += 40

        add_button = QPushButton('Add Student Details', self)
        add_button.clicked.connect(self.insertData)
        add_button.setGeometry(50, y_coordinate + 20, 200, 40)  # Adjusted position and size of the button

        single_report_button = QPushButton('Download This Student Report Card', self)
        single_report_button.clicked.connect(self.downloadSingleReportCard)
        single_report_button.setGeometry(280, y_coordinate + 20, 300, 40)  # Adjusted position and size of the button

        all_report_button = QPushButton('Download All Students Report Card', self)
        all_report_button.clicked.connect(self.downloadAllReportCards)
        all_report_button.setGeometry(610, y_coordinate + 20, 300, 40)  # Adjusted position and size of the button

        self.show()

    def areAllEntriesFilled(self):
        for entry in self.entries.values():
            if entry.text().strip() == '':
                return False
        return True
    
    def insertData(self):
        if self.areAllEntriesFilled():
            data = {field: entry.text() for field, entry in self.entries.items()}
            self.insertIntoDatabase(data)
        else:
            QMessageBox.critical(self, 'Error', 'Please fill in all fields.')

    def insertIntoDatabase(self, data):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='12345',
                database='ssshss'
            )
            cursor = conn.cursor()

            roll_no = data['Roll_No']
            cursor.execute(f"SELECT * FROM student_marks WHERE `Roll_No` = '{roll_no}'")
            result = cursor.fetchone()

            if result:
                QMessageBox.critical(self, 'Error', f'Roll No ({roll_no}) already exists!')
            else:
                query = f"""INSERT INTO student_marks 
                            (`Student_Name`, `Roll_No`, `Accounts_Marks`, `Business_Studies_Marks`, `Economics_Marks`, `Informatics_Marks`, `English_Marks`) 
                            VALUES ('{data['Student_Name']}', '{data['Roll_No']}', '{data['Accounts_Marks']}', '{data['Business_Studies_Marks']}', '{data['Economics_Marks']}', '{data['Informatics_Marks']}', '{data['English_Marks']}')"""
                cursor.execute(query)
                conn.commit()
                QMessageBox.information(self, 'Success', 'Student Data is Added Successfully!')
        except Exception as e:
            print('Error:', e)
        finally:
            cursor.close()
            conn.close()

    def downloadSingleReportCard(self):
        try:
            # Check if any field is empty
            for entry in self.entries.values():
                if entry.text().strip() == '':
                    QMessageBox.critical(self, 'Error', 'Please fill in all fields.')
                    return
            # Get the student's name from the entry field
            student_name = self.entries['Student_Name'].text()

            # Gather data for the single report card
            data = [self.entries[field].text() for field in fields]

            # Generate report card DataFrame
            df = pd.DataFrame([data], columns=fields)

            # Add total marks and percentage columns
            numeric_columns = ['Accounts_Marks', 'Business_Studies_Marks', 'Economics_Marks', 'Informatics_Marks', 'English_Marks']
            df[numeric_columns] = df[numeric_columns].astype(float)
            df['Total_Marks'] = df[numeric_columns].sum(axis=1)
            df['Total_Maximum_Marks'] = len(numeric_columns) * 100
            df['Percentage'] = (df['Total_Marks'] / df['Total_Maximum_Marks']) * 100
            df['Percentage'] = df['Percentage'].astype(str) + '%'  # Add % symbol to percentage column

            # Save to Excel with student's name as filename
            filename = f"{student_name}_Report_Card.xlsx"
            df.to_excel(f'D:/My_Projects/{filename}', index=False)
            QMessageBox.information(self, 'Success', f'Report Card Downloaded Successfully as {filename}!')
        except Exception as e:
            print('Error:', e)

    def downloadAllReportCards(self):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='12345',
                database='ssshss'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT Student_Name, Roll_No, Accounts_Marks, Business_Studies_Marks, Economics_Marks, Informatics_Marks, English_Marks FROM student_marks")
            data = cursor.fetchall()
            if data:
                self.generateReportCard(data)
            else:
                QMessageBox.warning(self, 'No Data', 'No data available to generate report cards.')
        except Exception as e:
            print('Error:', e)
        finally:
            cursor.close()
            conn.close()

    def generateReportCard(self, data):
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data, columns=['Student_Name', 'Roll_No', 'Accounts_Marks', 'Business_Studies_Marks', 'Economics_Marks', 'Informatics_Marks', 'English_Marks'])

            # Ensure marks columns are numeric
            numeric_columns = ['Accounts_Marks', 'Business_Studies_Marks', 'Economics_Marks', 'Informatics_Marks', 'English_Marks']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

            # Calculate total marks and percentage
            df['Total_Marks'] = df[numeric_columns].sum(axis=1)
            df['Total_Maximum_Marks'] = len(numeric_columns) * 100
            df['Percentage'] = (df['Total_Marks'] / df['Total_Maximum_Marks']) * 100

            # Add Pass/Fail column based on percentage
            df['Pass_or_Fail'] = df['Percentage'].apply(lambda x: 'Pass' if x >= 33 else 'Fail')

            # Reorder columns
            df = df[['Student_Name', 'Roll_No', 'Accounts_Marks', 'Business_Studies_Marks', 'Economics_Marks', 'Informatics_Marks', 'English_Marks', 'Total_Marks', 'Total_Maximum_Marks', 'Percentage', 'Pass_or_Fail']]

            # Save to Excel without index
            df.to_excel('D:/My_Projects/All-Students-Report-Card.xlsx', index=False)
            QMessageBox.information(self, 'Success', 'Report Card(s) Downloaded Successfully!')
        except Exception as e:
            print('Error:', e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StudentReportCard()
    sys.exit(app.exec_())
