import sys

class NetworkSecurityException(Exception):
    def __init__(self, error, error_detail: sys):
        super().__init__(str(error))
        self.error_message = self.get_detailed_error_message(error, error_detail)

    def get_detailed_error_message(self, error, error_detail: sys):
        _, _, exc_tb = error_detail.exc_info()
        filename = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        return f"Error occurred in script: [{filename}] line number: [{line_number}] error message: [{str(error)}]"

    def __str__(self):
        return self.error_message

