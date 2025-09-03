import bpy

from .tools_panel import *
from .id_panel import *
from .shapekeys_panel import *
from .dev_panel import *
from .renamer_panel import *

def register():
    bpy.utils.register_class(MANUTOOLS_PT_ToolsPanel)
    bpy.utils.register_class(MANUTOOLS_PT_IDPanel)
    bpy.utils.register_class(MANUTOOLS_PT_ShapekeyCopyPanel)
    bpy.utils.register_class(MANUTOOLS_PT_DevPanel)
    bpy.utils.register_class(MANUTOOLS_PT_lp_hp_matcher)

    

def unregister():
    # Unregister in ordine inverso per sicurezza
    try:
        bpy.utils.unregister_class(MANUTOOLS_PT_lp_hp_matcher)
    except:
        pass
    try:
        bpy.utils.unregister_class(MANUTOOLS_PT_DevPanel)
    except:
        pass
    try:
        bpy.utils.unregister_class(MANUTOOLS_PT_ShapekeyCopyPanel)
    except:
        pass
    try:
        bpy.utils.unregister_class(MANUTOOLS_PT_IDPanel)
    except:
        pass
    try:
        bpy.utils.unregister_class(MANUTOOLS_PT_ToolsPanel)
    except:
        pass