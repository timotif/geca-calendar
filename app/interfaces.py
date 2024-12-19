from abc import ABC, abstractmethod
from typing import List, Dict

class DataSourceInterface(ABC):
	"""Interface for data sources"""
	@abstractmethod
	def fetch_data(self) -> List[Dict]:
		pass

class StorageInterface(ABC):
	"""Interface for data storage"""
	@abstractmethod
	def save(self, data: List[Dict]):
		pass

	@abstractmethod
	def get(self, query: dict) -> List[Dict]:
		pass

	@abstractmethod
	def get_all(self) -> List[Dict]:
		pass

	@abstractmethod
	def get_by_id(self, id: str) -> Dict:
		pass 

class CalendarGeneratorInterface(ABC):
	"""Interface for calendar generators"""
	@abstractmethod
	def generate(self, events: List[Dict], filename: str) -> str:
		pass