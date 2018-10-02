import urllib2, simplejson, config
from util.helpers import *
from util.form_data import FormData
from util.base_test import BaseTest

expected_response_code = 200
eligible_forms = [
	FormData('3211191', 'Test Form Alpha', 'https://raftacon.formstack.com/forms/test_form_alpha'),
	FormData('3211194', 'Test Form Bravo', 'https://raftacon.formstack.com/forms/test_form_bravo'),
	FormData('3211200', 'Test Form Charlie', 'https://raftacon.formstack.com/forms/test_form_charlie')
]

class GetFormById(BaseTest):
	def __init__(self):
		self.name = "GET_FORM_BY_ID"
		self.case_type = CaseType.GET_FORM_BY_ID
		self.can_run_single = True

	def execute(self):
		self.base_path = config.FORM_BY_ID_PATH_TEMPLATE.replace(':id', config.DEFAULT_FORM_ID)
		self.path = self.base_path + "?oauth_token=" + config.ACCESS_TOKEN
		self.response = urllib2.urlopen(self.path)
		self.response_code = self.response.getcode()
		self.body = simplejson.loads(self.response.read())

		with open("./results/raw/" + str(self.execution_id) + "_get_form_by_id_response.json", "w") as write_file:
			write_file.write(simplejson.dumps(self.body, indent=4, sort_keys=True))

	def validate(self):
		response_form = None

		self.status = ValidationStatus.FAIL

		if self.response_code == expected_response_code:
			if (self.body is not None):
				response_form = FormData(self.body['id'], self.body['name'], self.body['url'])

				for form in eligible_forms:
					if form.id == response_form.id:
						self.status = ValidationStatus.PASS if form == response_form else ValidationStatus.FAIL

					if ValidationStatus.FAIL:
						break