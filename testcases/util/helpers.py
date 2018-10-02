from enum import Enum

class CaseType(Enum):
	GET_ALL_FORMS = 1
	GET_FORM_BY_ID = 2
	COPY_FORM = 3
	DELETE_FORM = 4

class ValidationStatus(Enum):
	PASS = 1
	FAIL = 2