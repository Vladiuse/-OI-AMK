class CheckerError(BaseException):
    """Checker error"""


class NoUflParamPreLand(CheckerError):
    """Нет параметра ?ufl="""

class NoAdminSiteDataScript(CheckerError):
    """Нет скрипта с ценами из админки"""


class IncorrectPreLandUrl(CheckerError):
    """Не правильный url прелэнда"""

class NoCountryInDB(CheckerError):
    """Нет страны в базе данных"""