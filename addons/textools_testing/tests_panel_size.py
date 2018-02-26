import bpy
import os

from . import utilities

tests = []

# tests_size.append( TT_Test('size_dropdown', call=None))
# tests_size.append( TT_Test('op_uv_size_get', call=None))
# tests_size.append( TT_Test('op_uv_crop', call=None))
# tests_size.append( TT_Test('op_uv_resize', call=None))
# tests_size.append( TT_Test('op_texture_reload_all', call=None))
# tests_size.append( TT_Test('uv_channel', call=None))
# tests_size.append( TT_Test('op_uv_channel_add', call=None))
# tests_size.append( TT_Test('op_uv_channel_swap', call=None))


def test_op_uv_size_get():
	print("A")
tests.append( utilities.Op_Test('op_uv_size_get', python='op_uv_size_get', blend="fdsfsd", test=test_op_uv_size_get))


def test_op_uv_crop():
	print("B")
tests.append( utilities.Op_Test('op_uv_crop', python='op_uv_crop', blend="", test=test_op_uv_crop))

