import os, glob, argparse, logging, urllib2, simplejson, shutil, config
from bs4 import BeautifulSoup as Soup
from os import path
from enum import Enum
import pygogo as gogo
from testcases import *

test_case_master_dict = {
	1: GetAllForms(),
	2: GetFormById(),
	3: CopyForm(),
	4: DeleteForm()
}
execution_list = []

class ExecutionType(Enum):
	SINGLE = 1
	ALL = 2

def configure_parser(parser):
	parser.add_argument('-c', '--case-number', type=int, help='number of the specific test case to run')
	parser.add_argument('-e', '--execute', type=int, help='number of times to execute the indicated case / suite')
	parser.add_argument('-i', '--id', type=int, help='override default ID for use with copy & delete test cases')

def clear_prior_results():
	# Cleanup all raw results from prior run:
	files = glob.glob('./results/raw/*')

	for f in files:
   		os.remove(f)

   	# Cleanup & replace formatted HTML results from prior run (if exists) with template:
	shutil.copy('./results/results_template.html', './results/results.html')

	log_message = "Prior test results purged." if not files == None else "No prior test results found."
	logger.info(log_message)

def compile_execution_list(execution_type, times_to_execute, case_number=None):
	if execution_type is ExecutionType.ALL:
		for i in range(times_to_execute):
			for key, value in test_case_master_dict.items():
				execution_list.append(value)
	elif execution_type is ExecutionType.SINGLE:
		if case_number is not None:
			case = test_case_master_dict.get(case_number)

			if case.can_run_single:
				for i in range(times_to_execute):
					execution_list.append(case)
			else:
				logger.error("Selected case cannot be run in standalone SINGLE mode, aborting.")
		else:
			logger.error("No case number provided during SINGLE compilation, aborting.")

def execute_cases():
	copy_id = "0"
	execution_id = 1

	for case in execution_list:
		if (case.case_type == CaseType.COPY_FORM):
			copy_id = case.run(execution_id)
		elif (case.case_type == CaseType.DELETE_FORM):
			case.run(execution_id, copy_id)
		else:
			case.run(execution_id)

		resolution_text = "successfully." if case.status == ValidationStatus.PASS else "with failure."
		logger.info(case.name + ", execution ID " + str(execution_id) + " completed " + resolution_text)

		if execution_type == ExecutionType.ALL and execution_id % len(test_case_master_dict) == 0:
			reset_state()

		execution_id += 1

def update_statistics():
	total_cases = len(execution_list)

	successes = 0.00
	failures = 0.00

	for case in execution_list:
		if case.status == ValidationStatus.PASS:
			successes += 1.00
		else:
			failures += 1.00

	formatted_success_percentage = "{:.2%}".format(successes / total_cases)
	formatted_failure_percentage = "{:.2%}".format(failures / total_cases)

	logger.debug("Success percentage: " + formatted_success_percentage)
	logger.debug("Failure percentage: " + formatted_failure_percentage)

	# Update results table:
	page = open("./results/results.html")
	mainSoup = Soup(page.read(), "html.parser")

	total_run = mainSoup.find("td", {"id": "total-run"})
	total_successes = mainSoup.find("td", {"id": "total-successes"})
	total_failures = mainSoup.find("td", {"id": "total-failures"})
	success_percentage = mainSoup.find("td", {"id": "success-percentage"})
	failure_percentage = mainSoup.find("td", {"id": "failure-percentage"})

	total_run.string = str(total_cases)
	total_successes.string = str(int(successes))
	total_failures.string = str(int(failures))
	success_percentage.string = str(formatted_success_percentage)
	failure_percentage.string = str(formatted_failure_percentage)

	with open("./results/results.html", "w") as file:
			file.write(str(mainSoup))

def reset_state():
	# Required in two different circumstances so far:
	#   (a) if DELETE_FORM fails after a COPY_FORM for some reason during a full suite
	#   (b) if COPY_FORM is run once (or execute repeatedly) in SINGLE mode
	# In either case, we'll need to set back to a neutral state the best we can ahead of
	# the next potential run to keep subsequent iterations smooth.
	path = config.FORM_PATH + "?oauth_token=" + config.ACCESS_TOKEN
	body = simplejson.loads(urllib2.urlopen(path).read())
	deletion_list = []

	for form in body['forms']:
		if 'COPY' in form['name']:
			deletion_list.append(form['id'])

	deletion_status_list = []

	for deletion_id in deletion_list:
		base_path = config.FORM_BY_ID_PATH_TEMPLATE.replace(':id', deletion_id)
		path = base_path + "?oauth_token=" + config.ACCESS_TOKEN
		request = urllib2.Request(path, data=None)
		request.get_method = lambda: 'DELETE'
		deletion_status_list.append(urllib2.urlopen(request).getcode())

	has_reset = True

	for status in deletion_status_list:
		if status is not 200:
			has_reset = False
			break

	reset_statement = "State reset successfully." if has_reset else "Issue occurred during state reset."

	logger.debug(reset_statement)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Automated tool to execute this quick Formstack API testing suite.')

	configure_parser(parser)
	args = vars(parser.parse_args())

	log_format = '%(asctime)s - %(levelname)s - %(message)s'
	formatter = logging.Formatter(log_format)

	logger = gogo.Gogo(
		'examples.fmt',
		low_formatter=formatter,
		high_formatter=formatter).logger

	execution_type = ExecutionType.ALL if not args['case_number'] else ExecutionType.SINGLE
	times_to_execute = 1 if not args['execute'] else args['execute']

	logger.debug("Execution Type: " + execution_type.name)
	logger.debug("Times to Execute: " + str(times_to_execute))

	clear_prior_results()

	if execution_type is ExecutionType.ALL:
		compile_execution_list(execution_type, times_to_execute)
	elif execution_type is ExecutionType.SINGLE:
		compile_execution_list(execution_type, times_to_execute, args['case_number'])

	if len(execution_list) > 0:
		execute_cases()
		update_statistics()

		if execution_type == ExecutionType.SINGLE:
			reset_state()