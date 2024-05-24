from abc import ABC, abstractmethod
import pandas as pd

class InterfaceParser(ABC):
	"""
	Interface class for form parsers.
	"""
	@abstractmethod
	def __init__(self, table: pd.DataFrame,
		generate_title_id = lambda tags: 1,
		generate_indicator_count = lambda title, subindicator_names: 2,
		generate_description = lambda title, subindicator_names, statform, indicator_names: "TBA",
		reference = None):
		self.table = table

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
		self.tags_title_id = generate_title_id(self.tags)
		self.title = self.tags[self.tags_title_id]
		self.indicator_count = generate_indicator_count(self.title, self.subindicator_names)
		# retrieve indicators
		self.indicators = self.retrieve_indicators()
		self.raw_values = self.retrieve_values()

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