import bpy

from .tools_panel import *
from .id_panel import *
from .shapekeys_panel import *
from .renamer_panel import *
from .attributes_panel import *

def register():
    bpy.utils.register_class(MANUTOOLS_PT_ToolsPanel)
    bpy.utils.register_class(MANUTOOLS_PT_lp_hp_matcher)
    bpy.utils.register_class(MANUTOOLS_PT_IDPanel)
    bpy.utils.register_class(MANUTOOLS_PT_shapekeysmanager)
    bpy.utils.register_class(MANUTOOLS_PT_attributes_manager)

def unregister():
    bpy.utils.unregister_class(MANUTOOLS_PT_attributes_manager)
    bpy.utils.unregister_class(MANUTOOLS_PT_shapekeysmanager)
    bpy.utils.unregister_class(MANUTOOLS_PT_IDPanel)
    bpy.utils.unregister_class(MANUTOOLS_PT_lp_hp_matcher)
    bpy.utils.unregister_class(MANUTOOLS_PT_ToolsPanel)
