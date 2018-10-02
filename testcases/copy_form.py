import urllib2, simplejson, config
from util.helpers import *
from util.form_data import FormData
from util.base_test import BaseTest

expected_response_code = 201
eligible_form = FormData('3211191', 'Test Form Alpha', 'https://raftacon.formstack.com/forms/test_form_alpha')

class CopyForm(BaseTest):
	def __init__(self):
		self.name = "COPY_FORM"
		self.case_type = CaseType.COPY_FORM
		self.response_form = None
		self.can_run_single = True

	def run(self, execution_id):
		BaseTest.run(self, execution_id)

		return "0" if self.response_form is None else self.response_form.id

	def execute(self):
		self.base_path = config.COPY_FORM_PATH_TEMPLATE.replace(':id', config.DEFAULT_FORM_ID)
		self.path = self.base_path + "?oauth_token=" + config.ACCESS_TOKEN
		self.request = urllib2.Request(self.path, data=None)
		self.request.get_method = lambda: 'POST'
		self.response = urllib2.urlopen(self.request)
		self.response_code = self.response.getcode()
		self.body = simplejson.loads(self.response.read())

		with open("./results/raw/" + str(self.execution_id) + "_copy_form_response.json", "w") as write_file:
			write_file.write(simplejson.dumps(self.body, indent=4, sort_keys=True))

	def validate(self):
		self.status = ValidationStatus.FAIL

		if self.response_code == expected_response_code:
			if (self.body is not None):
				self.response_form = FormData(self.body['id'], self.body['name'], self.body['url'])

				if eligible_form.name in self.response_form.name and \
				   eligible_form.url in self.response_form.url:
					self.status = ValidationStatus.PASS