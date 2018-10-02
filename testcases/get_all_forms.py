import urllib2, simplejson, config
from util.helpers import *
from util.form_data import FormData
from util.base_test import BaseTest

expected_response_code = 200
expected_forms = [
	FormData('3211191', 'Test Form Alpha', 'https://raftacon.formstack.com/forms/test_form_alpha'),
	FormData('3211194', 'Test Form Bravo', 'https://raftacon.formstack.com/forms/test_form_bravo'),
	FormData('3211200', 'Test Form Charlie', 'https://raftacon.formstack.com/forms/test_form_charlie')
]

class GetAllForms(BaseTest):
	def __init__(self):
		self.name = "GET_ALL_FORMS"
		self.case_type = CaseType.GET_ALL_FORMS
		self.can_run_single = True

	def execute(self):
		self.path = config.FORM_PATH + "?oauth_token=" + config.ACCESS_TOKEN
		self.response = urllib2.urlopen(self.path)
		self.response_code = self.response.getcode()
		self.body = simplejson.loads(self.response.read())

		with open("./results/raw/" + str(self.execution_id) + "_get_all_forms_response.json", "w") as write_file:
			write_file.write(simplejson.dumps(self.body, indent=4, sort_keys=True))

	def validate(self):
		response_forms = []

		for form in self.body['forms']:
			response_forms.append(FormData(form['id'], form['name'], form['url']))
		
		self.status = ValidationStatus.FAIL

		if self.response_code == expected_response_code:
			self.status = ValidationStatus.PASS if expected_forms == response_forms else ValidationStatus.FAIL