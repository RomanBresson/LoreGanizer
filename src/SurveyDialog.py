from Classes import *
from LeftMenu import *

from PyQt5.QtWidgets import (
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QDialog
)

class SurveyDialog(QDialog):
    def __init__(self, labels, parent=None, add_bottom_button=False):
        super().__init__(parent)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.layout = QFormLayout(self)
        
        self.inputs = {}
        for lab in labels:
            self.inputs[lab] = QLineEdit(self)
            self.layout.addRow(lab, self.inputs[lab])
        self.buttonBox = buttonBox
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        if add_bottom_button:
            self.layout.addWidget(buttonBox)
                
    def getInputs(self):
        return tuple(input.text() for input in self.inputs.values())