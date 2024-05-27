# Import common modules
from logging import PlaceHolder
import os, sys
from re import I
from string import printable
from tkinter import END

# Finding the path of the current file
current_path = os.path.dirname(__file__)
lib_path = os.path.join(current_path, '..')
sys.path.append(lib_path)

# Adding the path to the sys.path
lib_path = os.path.join(current_path, '..', 'src')
sys.path.append(lib_path)


# Import own modules
from src.tool_can import NewPCANBasic
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget, QPushButton, QLineEdit, QComboBox, QVBoxLayout, QTextEdit


HW_CONNECT = [
            'PCAN_ISABUS1',
            'PCAN_ISABUS2',
            'PCAN_ISABUS3',
            'PCAN_ISABUS4',
            'PCAN_ISABUS5',
            'PCAN_ISABUS6',
            'PCAN_ISABUS7',
            'PCAN_ISABUS8',
            'PCAN_DNGBUS1',
            'PCAN_PCIBUS1',
            'PCAN_PCIBUS2',
            'PCAN_PCIBUS3',
            'PCAN_PCIBUS4',
            'PCAN_PCIBUS5',
            'PCAN_PCIBUS6',
            'PCAN_PCIBUS7',
            'PCAN_PCIBUS8',
            'PCAN_PCIBUS9',
            'PCAN_PCIBUS10',
            'PCAN_PCIBUS11',
            'PCAN_PCIBUS12',
            'PCAN_PCIBUS13',
            'PCAN_PCIBUS14',
            'PCAN_PCIBUS15',
            'PCAN_PCIBUS16',
            'PCAN_USBBUS1',
            'PCAN_USBBUS2',
            'PCAN_USBBUS3',
            'PCAN_USBBUS4',
            'PCAN_USBBUS5',
            'PCAN_USBBUS6',
            'PCAN_USBBUS7',
            'PCAN_USBBUS8',
            'PCAN_USBBUS9',
            'PCAN_USBBUS10',
            'PCAN_USBBUS11',
            'PCAN_USBBUS12',
            'PCAN_USBBUS13',
            'PCAN_USBBUS14',
            'PCAN_USBBUS15',
            'PCAN_USBBUS16',
            'PCAN_LANBUS1',
            'PCAN_LANBUS2',
            'PCAN_LANBUS3',
            'PCAN_LANBUS4',
            'PCAN_LANBUS5',
            'PCAN_LANBUS6',
            'PCAN_LANBUS7',
            'PCAN_LANBUS8',
            'PCAN_LANBUS9',
            'PCAN_LANBUS10',
            'PCAN_LANBUS11',
            'PCAN_LANBUS12',
            'PCAN_LANBUS13',
            'PCAN_LANBUS14',
            'PCAN_LANBUS15',
            'PCAN_LANBUS16',
                 ]
HW_RATE = [
            'PCAN_BAUD_1M',
            'PCAN_BAUD_800K',
            'PCAN_BAUD_500K',
            'PCAN_BAUD_250K',
            'PCAN_BAUD_125K',
            'PCAN_BAUD_100K',
            'PCAN_BAUD_95K',
            'PCAN_BAUD_83K',
            'PCAN_BAUD_50K',
            'PCAN_BAUD_47K',
            'PCAN_BAUD_33K',
            'PCAN_BAUD_20K',
            'PCAN_BAUD_10K',
            'PCAN_BAUD_5K',
            ]

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

        # Add widgets.
        self.hw_combo = QComboBox()
        self.hw_rate = QComboBox()
        for item in HW_CONNECT:
            self.hw_combo.addItem(item)
        for item in HW_RATE:
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
            self.can = NewPCANBasic(PcanHandle=self.hw_combo.currentText())
            self.can.Initialize(self.can.PcanHandle, self.hw_rate.currentText())
            self.textbox.setText('Initialized.\n')
        except Exception as err:
            self.textbox.setText('Error in initializing CAN device: {}.\n'.format(err))
        
    def send_can(self):
        '''
        This function is used to send the CAN message.
        '''
        try:
            command = []
            for line_edit in self.line_edits:
                inp = line_edit.text()
                if not inp.isdigit() or int(inp) < 0 or int(inp) > 255:
                    self.textbox.insertPlainText("Please enter valid data (0-255).\n")
                    return
                command.append(int(inp))
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