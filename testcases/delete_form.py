import urllib2, simplejson, config
from util.helpers import *
from util.form_data import FormData
from util.base_test import BaseTest

expected_response_code = 200
expected_success = "1"

class DeleteForm(BaseTest):
	def __init__(self):
		self.name = "DELETE_FORM"
		self.case_type = CaseType.DELETE_FORM
		self.can_run_single = False

	def execute(self):
		self.base_path = config.FORM_BY_ID_PATH_TEMPLATE.replace(':id', self.deletion_id)
		self.path = self.base_path + "?oauth_token=" + config.ACCESS_TOKEN
		self.request = urllib2.Request(self.path, data=None)
		self.request.get_method = lambda: 'DELETE'
		self.response = urllib2.urlopen(self.request)
		self.response_code = self.response.getcode()
		self.body = simplejson.loads(self.response.read())

		with open("./results/raw/" + str(self.execution_id) + "_delete_form_response.json", "w") as write_file:
			write_file.write(simplejson.dumps(self.body, indent=4, sort_keys=True))

	def validate(self):
		self.status = ValidationStatus.FAIL

		if self.response_code == expected_response_code:
			if self.body['id'] == self.deletion_id:
				if self.body['success'] == expected_success:
					self.status = ValidationStatus.PASS