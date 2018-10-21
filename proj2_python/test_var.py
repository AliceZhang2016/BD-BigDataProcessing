class Foo:
	all = 0
	def __init__(self, _name):
		self.name = _name
	def add(self):
		Foo.all+=1

if __name__=='__main__':
	foo1 = Foo("f1")
	foo1.add()
	print(Foo.all)
	foo1.add()
	print(Foo.all)
	foo2 = Foo("f2")
	foo2.add()
	print(Foo.all)
