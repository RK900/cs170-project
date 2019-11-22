import os


def get_files_with_extension(directory, extension):
	files = []
	for name in os.listdir(directory):
		if name.endswith(extension):
			files.append(f'{directory}/{name}')
	return files


def read_file(file):
	with open(file, 'r') as f:
		data = f.readlines()
	data = [line.replace("Â", " ").strip().split() for line in data]
	return data


def write_to_file(file, string, append=False):
	if append:
		mode = 'a'
	else:
		mode = 'w'
	with open(file, mode) as f:
		f.write(string)


def write_data_to_file(file, data, separator, append=False):
	if append:
		mode = 'a'
	else:
		mode = 'w'
	with open(file, mode) as f:
		for item in data:
			f.write(f'{item}{separator}')


def input_to_output(input_file):
	return input_file.replace('input', 'output').replace('.in', '.out')


class Stack:
	"A container with a last-in-first-out (LIFO) queuing policy."

	def _init_(self):
		self.lst = []

	def push(self, item):
		"Push 'item' onto the stack"
		self.lst.append(item)

	def pop(self):
		"Pop the most recently pushed item from the stack"
		return self.lst.pop()

	def isEmpty(self):
		"Returns true if the stack is empty"
		return len(self.lst) == 0

	def __repr__(self):
		return " ".join(self.lst)
