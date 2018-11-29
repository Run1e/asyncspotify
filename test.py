
class A:
	@property
	def type(self):
		return 'asd'
	
b = A()

print(hasattr(A, 'type'))