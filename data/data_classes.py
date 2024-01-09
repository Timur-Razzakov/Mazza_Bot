class TariffData:
    # сохраняем данные о пользователе
    def __init__(self):
        self.user_id = None
        self.tariff_id = None
        self.tariff_name = None
        self.tariff_name_uzb = None
        self.description = None
        self.description_uzb = None
        self.price = None

    def reset(self):
        self.user_id = None
        self.tariff_id = None
        self.tariff_name = None
        self.tariff_name_uzb = None
        self.description = None
        self.description_uzb = None
        self.price = None


tariffs_data = {}


class RegistrationData:
    # сохраняем данные о пользователе
    def __init__(self):
        self.user_id = None
        self.user_name = None
        self.user_phone = None
        self.lang = None


registration_data = {}


class CourseData:
    # сохраняем данные о курсе
    def __init__(self):
        self.user_id = None
        self.product_name = None
        self.product_name_uzb = None
        self.product_id = None
        self.description = None
        self.description_uzb = None
        self.tariff_id = None
        self.free = None
        self.file_id = None
        self.file_type = None

    def reset(self):
        self.user_id = None
        self.product_name = None
        self.product_name_uzb = None
        self.product_id = None
        self.description = None
        self.description_uzb = None
        self.tariff_id = None
        self.free = None
        self.file_id = None
        self.file_type = None


courses_data = {}


class MailingData:
    # сохраняем данные о пользователе
    def __init__(self):
        self.user_id = None
        self.message = None
        self.lang = None
        self.has_tariff = None
        self.file_id = None
        self.file_type = None


mailings_data = {}



class HelpData:
    # получаем text и контакт для связи
    def __init__(self):
        self.user_id = None
        self.text = None
        self.contact = None


help_data = {}

