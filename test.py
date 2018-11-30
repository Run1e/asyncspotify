from math import ceil

class SliceIterator:
	def __init__(self, list, step):
		self.current = -1
		self.list = list
		self.step = step
		self.step_count = len(list) / step
	
	def __iter__(self):
		return self
	
	def __next__(self):
		self.current += 1
		base = self.current * self.step
		
		if self.current >= self.step_count:
			raise StopIteration
		
		return self.list[base:base + self.step]
	
	
my_list = [1, 2, 3, 4, 5]

i = 0
for item in SliceIterator(my_list, 2):
	print(f'{i} -> {item}')
	i += 1