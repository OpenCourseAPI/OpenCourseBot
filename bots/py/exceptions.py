# class MajorNotFound(Exception):
#     """Exception raised for errors in the input salary.

#     Attributes:
#         salary -- input salary which caused the error
#         message -- explanation of the error
#     """

#     def __init__(self, salary, message="There is no reports"):
#         self.salary = salary
#         self.message = message
#         super().__init__(self.message)

#     def __str__(self):
#         return f'{self.salary} -> {self.message}'
