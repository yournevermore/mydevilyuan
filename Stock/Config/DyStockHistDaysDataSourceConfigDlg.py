import json
from collections import OrderedDict

from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QTextEdit, QPushButton, QGridLayout, QComboBox, QLineEdit, QApplication

from DyCommon.DyCommon import DyCommon
from Stock.Common.DyStockCommon import DyStockCommon
from .DyStockConfig import DyStockConfig


class DyStockHistDaysDataSourceConfigDlg(QDialog):
    tradeDaysMode = OrderedDict\
                    ([
                        ('Wind和TuShare相互验证(默认)', 'Verify'),
                        ('若冲突，则以Wind为主', 'Wind'),
                        ('若冲突，则以TuShare为主', 'TuShare'),
                    ])

    def __init__(self, parent=None):
        super().__init__(parent)

        self._read()
        self._initUi()
        
    def _initUi(self):
        self.setWindowTitle('配置-股票历史日线数据源')
 
        # 控件
        label = QLabel('股票历史日线数据源')

        self._windCheckBox = QCheckBox('Wind')
        self._windCheckBox.clicked.connect(self._windCheckBoxClicked)

        self._tuShareCheckBox = QCheckBox('TuShare')
        self._tuShareCheckBox.clicked.connect(self._tuShareCheckBoxClicked)

        self._tuShareProCheckBox = QCheckBox('TuSharePro')
        self._tuShareProCheckBox.clicked.connect(self._tuShareProCheckBoxClicked)

        self._tuShareProTokenLabel = QLabel('TuSharePro token')
        self._tuShareProTokenLineEdit = QLineEdit()

        description = """默认使用Wind

只选Wind：更新交易日数据，股票代码表和股票历史日线数据到Wind对应的数据库

只选TuShare：更新交易日数据，股票代码表和股票历史日线数据到TuShare对应的数据库

选两个：更新交易日数据，股票代码表和股票历史日线数据到Wind对应的数据库，并同时做两个源的数据验证

交易日数据，股票代码表和股票历史日线数据的载入也是基于上面选择的数据库
        """
        textEdit = QTextEdit()
        textEdit.setPlainText(description)
        textEdit.setReadOnly(True)

        cancelPushButton = QPushButton('Cancel')
        okPushButton = QPushButton('OK')
        cancelPushButton.clicked.connect(self._cancel)
        okPushButton.clicked.connect(self._ok)

        self._tradeDaysComboBox = QComboBox()
        descriptionTradeDays = "Wind有时交易日数据可能出错，所以选Wind时，总是跟TuShare做验证，由用户选择该如何做。"
        tradeDaysTextEdit = QTextEdit()
        tradeDaysTextEdit.setPlainText(descriptionTradeDays)
        tradeDaysTextEdit.setReadOnly(True)

        self._tuShareDaysIntervalLineEdit = QLineEdit() # TuShare日线数据每次下载间隔时间（秒）

        # 布局
        grid = QGridLayout()
        grid.setSpacing(10)
 
        grid.addWidget(label, 0, 0)
        grid.addWidget(self._windCheckBox, 1, 0)
        grid.addWidget(self._tuShareCheckBox, 2, 0)
        grid.addWidget(self._tuShareProCheckBox, 3, 0)
        grid.addWidget(self._tuShareProTokenLabel, 4, 0)
        grid.addWidget(self._tuShareProTokenLineEdit, 5, 0)

        grid.addWidget(textEdit, 6, 0)

        grid.addWidget(QLabel("                                                                 "), 7, 0)
        grid.addWidget(QLabel("交易日数据模式"), 8, 0)
        grid.addWidget(self._tradeDaysComboBox, 9, 0)
        grid.addWidget(tradeDaysTextEdit, 10, 0)

        grid.addWidget(QLabel("                                                                 "), 11, 0)
        grid.addWidget(QLabel("TuShare日线数据下载间隔时间(秒)"), 12, 0)
        grid.addWidget(self._tuShareDaysIntervalLineEdit, 13, 0)

        grid.addWidget(okPushButton, 0, 1)
        grid.addWidget(cancelPushButton, 1, 1)
 
        self.setLayout(grid)

        # set data source to UI
        if self._data.get('Wind'):
            self._windCheckBox.setChecked(True)

        enableTuSharePro = False
        if self._data.get('TuShare'):
            self._tuShareCheckBox.setChecked(True)
            enableTuSharePro = True

        self._tuShareProCheckBox.setEnabled(enableTuSharePro)

        # set tushare pro
        enableTushareProToken = False
        if self._tuShareProData.get('TuSharePro'):
            self._tuShareProCheckBox.setChecked(True)
            enableTushareProToken = True

        self._tuShareProTokenLabel.setEnabled(enableTuSharePro and enableTushareProToken)
        self._tuShareProTokenLineEdit.setEnabled(enableTuSharePro and enableTushareProToken)

        if self._tuShareProData.get('Token'):
            self._tuShareProTokenLineEdit.setText(self._tuShareProData.get('Token'))

        # set according to days source checkbox
        self._tradeDaysComboBox.addItems(list(self.tradeDaysMode))
        self._enableTradeDaysComboBox()
        
        for k, v in self.tradeDaysMode.items():
            if v == self._tradeDaysModeData["tradeDaysMode"]:
                self._tradeDaysComboBox.setCurrentText(k)
                break

        # tushare days downloading interval
        self._tuShareDaysIntervalLineEdit.setText(str(self._tuShareDaysIntervalData['interval']))

        self.resize(QApplication.desktop().size().width()//2, QApplication.desktop().size().height()//4*3)
        
    def _read(self):
        # data source
        file = DyStockConfig.getStockHistDaysDataSourceFileName()

        try:
            with open(file) as f:
                self._data = json.load(f)
        except:
            self._data = DyStockConfig.getDefaultHistDaysDataSource()

        # tushare pro
        file = DyStockConfig.getStockHistDaysTuShareProFileName()

        try:
            with open(file) as f:
                self._tuShareProData = json.load(f)
        except:
            self._tuShareProData = DyStockConfig.getDefaultHistDaysTuSharePro()

        # trade days mode
        file = DyStockConfig.getStockTradeDaysModeFileName()

        try:
            with open(file) as f:
                self._tradeDaysModeData = json.load(f)
        except:
            self._tradeDaysModeData = DyStockConfig.defaultTradeDaysMode

        # interval of tushare days downloading
        file = DyStockConfig.getStockTuShareDaysIntervalFileName()

        try:
            with open(file) as f:
                self._tuShareDaysIntervalData = json.load(f)
        except:
            self._tuShareDaysIntervalData = DyStockConfig.defaultTuShareDaysInterval

    def _ok(self):
        # data source
        data = {'Wind': False, 'TuShare': False}
        if self._windCheckBox.isChecked():
            data['Wind'] = True

        if self._tuShareCheckBox.isChecked():
            data['TuShare'] = True

        # config to variables
        DyStockConfig.configStockHistDaysDataSource(data)

        # save config
        file = DyStockConfig.getStockHistDaysDataSourceFileName()
        with open(file, 'w') as f:
            f.write(json.dumps(data, indent=4))

        # tushare pro
        data = {'TuSharePro': False, 'Token': None}
        if self._tuShareProCheckBox.isChecked():
            data['TuSharePro'] = True

        data['Token'] = self._tuShareProTokenLineEdit.text()

        DyStockConfig.configStockHistDaysTuSharePro(data)

        file = DyStockConfig.getStockHistDaysTuShareProFileName()
        with open(file, 'w') as f:
            f.write(json.dumps(data, indent=4))

        # trade days mode
        data = {}
        data["tradeDaysMode"] = self.tradeDaysMode[self._tradeDaysComboBox.currentText()]

        DyStockConfig.configStockTradeDaysMode(data)

        file = DyStockConfig.getStockTradeDaysModeFileName()
        with open(file, 'w') as f:
            f.write(json.dumps(data, indent=4))

        # tushare days downloading interval
        data = {}
        text = self._tuShareDaysIntervalLineEdit.text()
        try:
            data["interval"] = int(text)
        except:
            try:
                data["interval"] = float(text)
            except:
                data = DyStockConfig.defaultTuShareDaysInterval

        DyStockConfig.configStockTuShareDaysInterval(data)

        file = DyStockConfig.getStockTuShareDaysIntervalFileName()
        with open(file, 'w') as f:
            f.write(json.dumps(data, indent=4))

        self.accept()

    def _cancel(self):
        self.reject()

    def _enableTradeDaysComboBox(self):
        if self._windCheckBox.isChecked():
            self._tradeDaysComboBox.setEnabled(True)
        else:
            self._tradeDaysComboBox.setEnabled(False)

    def _checkBoxClicked(self):
        if not self._windCheckBox.isChecked() and not self._tuShareCheckBox.isChecked():
            self._windCheckBox.setChecked(True)

        self._enableTradeDaysComboBox()

    def _windCheckBoxClicked(self):
        self._checkBoxClicked()

    def _tuShareCheckBoxClicked(self):
        self._checkBoxClicked()

        enable = self._tuShareCheckBox.isChecked()
        self._tuShareProCheckBox.setEnabled(enable)

        enableToken = self._tuShareProCheckBox.isChecked()
        self._tuShareProTokenLabel.setEnabled(enable and enableToken)
        self._tuShareProTokenLineEdit.setEnabled(enable and enableToken)

    def _tuShareProCheckBoxClicked(self):
        enable = self._tuShareProCheckBox.isChecked()

        self._tuShareProTokenLabel.setEnabled(enable)
        self._tuShareProTokenLineEdit.setEnabled(enable)