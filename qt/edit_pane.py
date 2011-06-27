# Created By: Virgil Dupras
# Created On: 2011-06-18
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from functools import partial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QCheckBox, QTextEdit)
from qtlib.util import verticalSpacer, horizontalSpacer

from core.pdf import ElementState
from core.gui.edit_pane import EditPane as EditPaneModel

class EditPane(QWidget):
    def __init__(self, app):
        QWidget.__init__(self)
        self.app = app
        self._setupUi()
        self.model = EditPaneModel(view=self, app=app.model)
        self.model.connect()
        
        self.normalButton.clicked.connect(partial(self.app.model.change_state_of_selected, ElementState.Normal))
        self.titleButton.clicked.connect(partial(self.app.model.change_state_of_selected, ElementState.Title))
        self.footnoteButton.clicked.connect(partial(self.app.model.change_state_of_selected, ElementState.Footnote))
        self.ignoreButton.clicked.connect(partial(self.app.model.change_state_of_selected, ElementState.Ignored))
        self.hideIgnoredCheckBox.stateChanged.connect(self.hideIgnoredCheckBoxStateChanged)
        self.textEdit.textChanged.connect(self.textEditTextChanged)
        self.saveEditsButton.clicked.connect(self.model.save_edits)
        self.cancelEditsButton.clicked.connect(self.model.cancel_edits)
        
    def _setupUi(self):
        self.mainLayout = QHBoxLayout(self)
        self.buttonLayout = QVBoxLayout()
        self.normalButton = QPushButton("Normal")
        self.buttonLayout.addWidget(self.normalButton)
        self.titleButton = QPushButton("Title")
        self.buttonLayout.addWidget(self.titleButton)
        self.footnoteButton = QPushButton("Footnote")
        self.buttonLayout.addWidget(self.footnoteButton)
        self.ignoreButton = QPushButton("Ignore")
        self.buttonLayout.addWidget(self.ignoreButton)
        self.buttonLayout.addItem(verticalSpacer())
        self.mainLayout.addLayout(self.buttonLayout)
        
        self.rightLayout = QVBoxLayout()
        self.hideIgnoredCheckBox = QCheckBox("Hide Ignored Elements")
        self.rightLayout.addWidget(self.hideIgnoredCheckBox)
        self.textEdit = QTextEdit()
        self.textEdit.setAcceptRichText(False)
        self.rightLayout.addWidget(self.textEdit)
        self.editButtonLayout = QHBoxLayout()
        self.editButtonLayout.addItem(horizontalSpacer())
        self.saveEditsButton = QPushButton("Save")
        self.editButtonLayout.addWidget(self.saveEditsButton)
        self.cancelEditsButton = QPushButton("Cancel")
        self.editButtonLayout.addWidget(self.cancelEditsButton)
        self.rightLayout.addLayout(self.editButtonLayout)
        self.mainLayout.addLayout(self.rightLayout)
        
    #--- Signals
    def hideIgnoredCheckBoxStateChanged(self, state):
        self.app.model.hide_ignored = state == Qt.Checked
    
    def textEditTextChanged(self):
        self.model.edit_text = self.textEdit.toPlainText()
    
    #--- model -> view
    def refresh_edit_text(self):
        self.textEdit.setText(self.model.edit_text)
        self.textEdit.setEnabled(self.model.edit_enabled)
        self.saveEditsButton.setEnabled(self.model.edit_enabled)
        self.cancelEditsButton.setEnabled(self.model.edit_enabled)
    