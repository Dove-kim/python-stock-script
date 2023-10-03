from PyQt5.QAxContainer import QAxWidget

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("kimwoom class")

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_CommConnect()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)

    def login_slot(self, err_code):
        print(err_code)
    def signal_login_CommConnect(self):
        self.dynamicCall("CommConnect()")