from abc import ABC, abstractmethod

class DataSourceInterface(ABC):
	"""Interface for data sources"""
	@abstractmethod
	def fetch_data(self) -> list[dict]: # TODO: maybe use typing.List and typing.Dict
		pass

class StorageInterface(ABC):
	"""Interface for data storage"""
	@abstractmethod
	def save(self, data: list[dict]):
		pass

	@abstractmethod
	def get(self, query: dict) -> list[dict]:
		pass

class CalendarGeneratorInterface(ABC):
	"""Interface for calendar generators"""
	@abstractmethod
	def generate(self, events: list[dict], filename: str) -> str:
		pass