from abc import ABC, abstractmethod
import pandas as pd

class InterfaceParser(ABC):
	"""
	Interface class for form parsers. Reference object has the following format:
	{"table title tag": {"indicator_count": 2, "description": "TBA"}}
	"""

	@abstractmethod
	def __init__(self, table: pd.DataFrame,
		generate_title_id = lambda tags: 1,
		generate_indicator_count = lambda title, subindicator_names: 2,
		generate_description = lambda title, subindicator_names, statform, indicator_names: "TBA",
		reference = None,
		statform = "-"):
		self.table = table.replace('', float('NaN')).dropna(how='all') \
			.dropna(axis=1, how='all').reset_index(drop=True)
		self.statform = statform
		if reference is None:
			# we're dealing with THE reference file
			self.reference_file = True
			self.reference = {}
		else:
			self.reference_file = False
			self.reference = reference
		# retrieve tags and subindicators
		self.tag_row_count, self.tags = self.retrieve_tags()
		self.subindicator_row_count, self.subindicators = self.retrieve_subindicators()
		self.subindicator_names = list(map(lambda x: ' > '.join((map(str, x))), self.subindicators))
		# voodoo magic - 1
		if self.reference_file:
			self.tags_title_id = generate_title_id(self.tags)
		else:
			titles = reference.keys()
			self.tags_title_id = next((index for index, element in
							  enumerate(self.tags) if element in titles), None)
		self.title = self.tags[self.tags_title_id]
		if self.reference_file:
			self.indicator_count = generate_indicator_count(self.title, self.subindicator_names)
		else:
			self.indicator_count = self.reference[self.title]['indicator_count']
		# retrieve indicators
		self.indicators = self.retrieve_indicators()
		self.indicator_names = list(map(lambda x: ' / '.join((map(str, x))), self.indicators))
		self.raw_values = self.retrieve_values()
		self.description = generate_description(self.title, self.subindicator_names, self.statform, self.indicator_names)

	@abstractmethod
	def retrieve_tags(self):
		"""Returns (tag_row_count, [tags]) from header"""
		pass

	@abstractmethod
	def retrieve_subindicators(self):
		"""Returns (subindicator_row_count, [[subindicator_1], [subindicator_2]...]). Table *HAS* to be without table tags above"""
		pass

	@abstractmethod
	def retrieve_indicators(self):
		"""Returns [[indicator_1], [indicator_2], ...]"""
		pass

	@abstractmethod
	def retrieve_values():
		"""Returns list of rows"""
		pass