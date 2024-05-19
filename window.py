from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow, QFileDialog
from PyQt6.uic import loadUi

from config import Config
from excel_loader import ExcelLoader
from services.facebook_ad_service import FacebookAdsService
from services.facebook_business_api import FacebookBusinessApi


class AdUpdateThread(QThread):
    logMessage = pyqtSignal(str, str)
    updateFinished = pyqtSignal()

    def __init__(self, adsService, adAccountId, selectedCampaignIds, dt):
        super().__init__()
        self.adsService = adsService
        self.adAccountId = adAccountId
        self.selectedCampaignIds = selectedCampaignIds
        self.dt = dt

    def run(self):
        for campaignId, row in zip(self.selectedCampaignIds, self.dt):
            try:
                self.logMessage.emit(f'Rozpoczęto aktualizację dla kampanii {campaignId}', 'black')
                self.adsService.update(self.adAccountId, campaignId, row)
                self.logMessage.emit(f'Zakończono aktualizację dla kampanii {campaignId}', 'green')
            except Exception as e:
                self.logMessage.emit(f"Wystąpił błąd z aktualizacją Campaign {campaignId}: {str(e)}", 'red')

        self.updateFinished.emit()


class Window(QMainWindow):
    def __init__(self):
        self.ad_update_thread = None
        self.dt = []

        try:
            super().__init__()
            loadUi("gui/app.ui", self)

            config = Config('config.json')
            self.__facebookBusinessApi = FacebookBusinessApi(config)
            self.__adsService = FacebookAdsService(self.__facebookBusinessApi)

            self.__fillInit()

            self.__selectedCampaignIds = []

            self.businessComboBox.currentIndexChanged.connect(self.fillAdAccountsCombobox)
            self.adAccountsComboBox.currentIndexChanged.connect(self.fillCampaignsListView)
            self.loadFileButton.clicked.connect(self.loadExcelFile)
            self.startButton.clicked.connect(self.adAllUpdate)
            self.campaignListView.clicked.connect(self.selectCampaignListView)
        except Exception as e:
            self.logError(str(e))

    def selectCampaignListView(self, index):
        data = self.campaignListView.model().data(index, Qt.ItemDataRole.UserRole)
        item = self.campaignListView.model().itemFromIndex(index)

        isChecked = item.checkState() == Qt.CheckState.Checked

        if isChecked:
            if data not in self.__selectedCampaignIds:
                self.__selectedCampaignIds.append(data)
        else:
            if data in self.__selectedCampaignIds:
                self.__selectedCampaignIds.remove(data)

    def adAllUpdate(self):
        try:
            if not self.dt:
                self.logError("Nie wczytano danych z pliku Excel.")
                return

            selected_business_index = self.businessComboBox.currentIndex()
            selected_business_id = self.businessComboBox.itemData(selected_business_index)

            if not selected_business_id:
                self.logError("Nie wybrano firmy.")
                return

            selected_adaccount_index = self.adAccountsComboBox.currentIndex()
            selected_adaccount_id = self.adAccountsComboBox.itemData(selected_adaccount_index)

            if not selected_adaccount_id:
                self.logError("Nie wybrano konta reklamowego.")
                return

            self.startButton.setText("Aktualizacja w toku...")
            self.startButton.setDisabled(True)

            self.log('Rozpoczęto aktualizację ADS', color='green')

            self.ad_update_thread = AdUpdateThread(self.__adsService, selected_adaccount_id, self.__selectedCampaignIds,
                                                   self.dt)
            self.ad_update_thread.logMessage.connect(self.log)
            self.ad_update_thread.updateFinished.connect(self.onUpdateFinished)
            self.ad_update_thread.start()

        except Exception as e:
            self.logError(str(e))

    def onUpdateFinished(self):
        self.log('KONIEC', color='green')

        self.startButton.setText("Start")
        self.startButton.setDisabled(False)

    def logError(self, errorMessage):
        self.log(errorMessage, color='red')

    def log(self, message, color='black'):
        self.logTextEdit.appendHtml(f"<font color='{color}'>{message}</font><br>")

    def __fillInit(self):
        self.fillBusinessCombobox()

    def fillBusinessCombobox(self):
        try:
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
        except Exception as e:
            self.logError(str(e))

    def fillAdAccountsCombobox(self):
        try:
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
        except Exception as e:
            self.logError(str(e))

    def fillCampaignsListView(self):
        try:
            selectedAdAccountIndex = self.adAccountsComboBox.currentIndex()

            if selectedAdAccountIndex == 0:
                self.campaignListView.setModel(None)
                return

            adAccountId = self.adAccountsComboBox.itemData(selectedAdAccountIndex)

            campaigns = self.__facebookBusinessApi.getCampaigns(adAccountId)

            model = QStandardItemModel()

            for campaign in campaigns:
                name = campaign['name']
                campaignId = campaign['id']

                item = QStandardItem(f"{name}")
                item.setCheckable(True)
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setData(campaignId, Qt.ItemDataRole.UserRole)
                model.appendRow(item)

            self.campaignListView.setModel(model)
        except Exception as e:
            self.logError(str(e))

    def loadExcelFile(self):
        try:
            excelLoader = ExcelLoader()

            filePath, _ = QFileDialog.getOpenFileName(self, "Wybierz plik Excel", "", "Excel Files (*.xlsx)")

            if filePath:
                self.dt = excelLoader.load(filePath)
                self.loadFileButton.setText(filePath.split('/')[-1])
            else:
                self.dt = None


        except Exception as e:
            self.dt = None
            self.logError(str(e))
