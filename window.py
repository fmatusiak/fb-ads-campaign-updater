from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow, QFileDialog
from PyQt6.uic import loadUi

from config import Config
from excel_loader import ExcelLoader
from services.facebook_business_api import FacebookBusinessApi


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("gui/app.ui", self)
        config = Config('config.json')

        self.__facebookBusinessApi = FacebookBusinessApi(config)

        self.__fillInit()

        self.businessComboBox.currentIndexChanged.connect(self.fillAdAccountsCombobox)
        self.adAccountsComboBox.currentIndexChanged.connect(self.fillCampaignsListView)

    def logError(self, errorMessage):
        self.logTextEdit.appendHtml(f"<font color='red'>{errorMessage}</font>")

    def __fillInit(self):
        self.fillBusinessCombobox()

    def fillBusinessCombobox(self):
        selectedIndex = self.businessComboBox.currentIndex()

        if selectedIndex == 0:
            return

        businesses = self.__facebookBusinessApi.getBusinesses()

        self.businessComboBox.clear()
        self.businessComboBox.addItem("WYBIERZ")

        for business in businesses:
            name = business['name']
            businessId = business['id']
            self.businessComboBox.addItem(name, businessId)

    def fillAdAccountsCombobox(self):
        selectedIndex = self.adAccountsComboBox.currentIndex()

        if selectedIndex == 0:
            return

        selectedBusinessIndex = self.businessComboBox.currentIndex()

        if selectedBusinessIndex == 0:
            self.adAccountsComboBox.clear()
            return

        businessId = self.businessComboBox.itemData(selectedBusinessIndex)

        adAccounts = self.__facebookBusinessApi.getAdAccounts(businessId)

        self.adAccountsComboBox.clear()
        self.adAccountsComboBox.addItem("WYBIERZ")

        for adAccount in adAccounts:
            name = adAccount['name']
            adAccountId = adAccount['id']
            self.adAccountsComboBox.addItem(name, adAccountId)

    def fillCampaignsListView(self):
        selectedAdAccountIndex = self.adAccountsComboBox.currentIndex()

        if selectedAdAccountIndex == 0:
            self.campaignListView.setModel(None)
            return

        adAccountId = self.adAccountsComboBox.itemData(selectedAdAccountIndex)

        campaigns = self.__facebookBusinessApi.getCampaigns(adAccountId, ['ACTIVE'])

        model = QStandardItemModel()

        for campaign in campaigns:
            name = campaign['name']
            campaign_id = campaign['id']
            item = QStandardItem(f"{name} ({campaign_id})")
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            model.appendRow(item)

        self.campaignListView.setModel(model)

    def loadExcelFile(self):
        excelLoader = ExcelLoader()

        filePath, _ = QFileDialog.getOpenFileName(self, "Wybierz plik Excel", "", "Excel Files (*.xlsx)")

        if filePath:
            self.dt = excelLoader.load(filePath)
