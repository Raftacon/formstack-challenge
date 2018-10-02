import urllib, urllib2, simplejson, time, datetime, config
from bs4 import BeautifulSoup as Soup
from .helpers import *
from .form_data import FormData

class BaseTest:
	def run(self, execution_id, deletion_id=None):
		self.execution_id = execution_id
		self.deletion_id = deletion_id
		self.execute()
		self.validate()
		self.export()

	def execute(self):
		raise NotImplementedError()

	def validate(self):
		raise NotImplementedError()

	def export(self):
		page = open("./results/results.html")
		mainSoup = Soup(page.read(), "html.parser")

		timestamp = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
		data_target = 'data-target="#results-' + str(self.execution_id) + '"'
		button_name = timestamp + ' - TEST RUN ' + str(self.execution_id) + ': "' + self.name + '" DETAILS'
		collapsible_id = 'id="results-' + str(self.execution_id) + '"'
		text_color = "green" if self.status == ValidationStatus.PASS else "red"
		text_status = "PASS" if self.status == ValidationStatus.PASS else "FAIL"
		pass_fail_text = '<b style="color:' + text_color + '">' + text_status + '</b><br>'

		case_data = Soup('<div>' + pass_fail_text + '<button class="button-primary" data-toggle="collapse" ' + \
			data_target + '>' + button_name + '</button><div ' + collapsible_id + \
			' class="collapse"><br><b>Request URL &amp; Query String:</b><pre><code>' + self.path + \
			'</code></pre><b>Response Code:</b><pre><code>' + str(self.response_code) + \
			'</code></pre><b>Response (JSON):</b><pre><code style="text-align:left"><xmp>' + \
			simplejson.dumps(self.body, indent=4, sort_keys=True) + '</xmp></code></pre></div><hr>', "html.parser")

		end = mainSoup.find("div", {"id": "end"})

		end.insert_before(case_data)

		with open("./results/results.html", "w") as file:
			file.write(str(mainSoup))