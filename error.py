"""
    Handles Submit to farm highest level error
"""
class SubmitToFarmError(Exception):
    def __init__(self, message):
        super(SubmitToFarmError, self).__init__(message)

class SubmitToFarmBuildError(Exception):
    def __init__(self, message):
        super(SubmitToFarmBuildError, self).__init__(message)

    def __str__(self):
        return "{}:\n {}\n".format(self.__class__.__name__, self.message)

class SubmitToFarmServerError(Exception):
    def __init__(self, message):
        super(SubmitToFarmServerError, self).__init__(message)

    def __str__(self):
        return "Server Error{} :\n {}\n".format(self.__class__.__name__, self.message)

class SubmitToFarmSubmitError(Exception):
    def __init__(self, message):
        super(SubmitToFarmSubmitError, self).__init__(message)

    def __str__(self):
        return "Submit Error:\n{}:\n {}\n".format(self.__class__.__name__, self.message)