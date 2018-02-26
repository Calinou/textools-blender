import bpy
import os
import subprocess


class Op_Test:
	name = ""
	blend = ""
	python = ""
	test = None
	def __init__(self, name, python="", blend="", test=None):
		self.name = name
		self.python = python
		self.blend = blend
		self.test = test

	def run(self):
		print("Run test '{}'".format(self.name))

		# Open blend file first
		if self.blend:
			self.open_blend()

		# Execute test
		if self.test:
			self.test()

	def open_python(self):
		# https://stackoverflow.com/questions/281888/open-explorer-on-a-file
		# subprocess.Popen(r'explorer /select,"C:\path\of\folder\file"')
		# subprocess.call("explorer C:\\temp\\yourpath", shell=True)
		print("Open PY File")

	def open_blend(self):
		# https://stackoverflow.com/questions/281888/open-explorer-on-a-file
		# subprocess.Popen(r'explorer /select,"C:\path\of\folder\file"')
		# subprocess.call("explorer C:\\temp\\yourpath", shell=True)
		print("Open Blend File")