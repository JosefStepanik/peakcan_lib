# Import common modules
import os, sys

# Finding the path of the current file
current_path = os.path.dirname(__file__)
lib_path = os.path.join(current_path, '..')
sys.path.append(lib_path)

# Adding the path to the sys.path
lib_path = os.path.join(current_path, '..', 'src')
sys.path.append(lib_path)


# Import own modules
from src.PCANBasic import *        ## PCAN-Basic library import
from src.tool_can import *
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget, QPushButton, QLineEdit, QComboBox, QVBoxLayout, QTextEdit


class TestApp(QWidget):
    '''
    This class is used to test tool_can module.
    '''
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("CAN Communication")
        self.setGeometry(100, 100, 400, 400)
        self.layout = QVBoxLayout()
        container = QHBoxLayout()
        
        self.m_NonPnPHandles = HW_HANDLES
        self.m_BAUDRATES = HW_BAUDRATES
        self.m_errors = ERRORS
        

        # Add widgets.
        self.hw_combo = QComboBox()
        self.hw_rate = QComboBox()
        for item in self.m_NonPnPHandles:
            self.hw_combo.addItem(item)
        for item in self.m_BAUDRATES:
            self.hw_rate.addItem(item)
            
        self.line_edits = []
        for _ in range(9):
            line_edit = QLineEdit()
            self.line_edits.append(line_edit)
            container.addWidget(line_edit)
        self.line_edits[0].setPlaceholderText('Address')
        self.line_edits[1].setPlaceholderText('Data 1')
        self.line_edits[2].setPlaceholderText('Data 2')
        self.line_edits[3].setPlaceholderText('Data 3')
        self.line_edits[4].setPlaceholderText('Data 4')
        self.line_edits[5].setPlaceholderText('Data 5')
        self.line_edits[6].setPlaceholderText('Data 6')
        self.line_edits[7].setPlaceholderText('Data 7')
        self.line_edits[8].setPlaceholderText('Data 8')

        self.init_btn = QPushButton('Initialize')
        self.init_btn.clicked.connect(self.init_can)
        
        self.send_btn = QPushButton('Send')
        self.send_btn.clicked.connect(self.send_can)
        
        self.textbox = QTextEdit()
        
        # Add to layout.
        self.layout.addWidget(self.hw_combo)
        self.layout.addWidget(self.hw_rate)
        self.layout.addWidget(self.init_btn)
        self.layout.addLayout(container)
        self.layout.addWidget(self.send_btn)
        self.layout.addWidget(self.textbox)
        
        # Set layout.
        self.setLayout(self.layout)
        
        
    def init_can(self):
        '''
        This function is used to initialize the CAN.
        '''
        try:
            self.can = NewPCANBasic(PcanHandle=self.m_NonPnPHandles[self.hw_combo.currentText()])
            status = self.can.Initialize(self.can.PcanHandle, self.m_BAUDRATES[self.hw_rate.currentText()])
            if PCAN_ERROR_OK != status:
                raise
            self.textbox.setText('Initialized.\n')
        except Exception as err:
            error_message = self.can.get_formatted_error(status)
            self.textbox.setText('Error in initializing CAN device: {}.\n'.format(error_message))
            
    def send_can(self):
        '''
        This function is used to send the CAN message.
        '''
        try:
            command = []
            for line_edit in self.line_edits:
                inp_str = line_edit.text()
                inp_num = int(inp_str,16)
                if not inp_str.isdigit() or inp_num < 0 or inp_num > 255:
                    self.textbox.insertPlainText("Please enter valid data (0-255).\n")
                    return
                command.append(inp_num)
            address = command[0]
            command = command[1:len(command)]
            response = self.can.write_read(address, command)
            self.textbox.setText("You recieve {0} with address ID {1}.\n".format(self.can.get_data_string(response[1].DATA, response[1].MSGTYPE), self.can.get_id_string(response[1].ID, response[1].MSGTYPE)))
        except Exception as err:
            self.textbox.append('Error in sending the CAN message: {}.\n'.format(err))
            
        

# Main function
if __name__ == '__main__':
   app = QApplication(sys.argv)
   test = TestApp()
   test.show()
   app.exec()