class FormData():
	def __init__(self, id, name, url):
		self.id = id
		self.name = name
		self.url = url

	def __eq__(self, other):
		if self.__class__ != other.__class__:
			return False
		else:
			return self.__dict__ == other.__dict__