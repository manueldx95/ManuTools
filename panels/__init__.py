import bpy

from .tools_panel import *
from .id_panel import *
from .shapekeys_panel import *
from .renamer_panel import *
from .attributes_panel import *
from .help_panel import *

def update_panel_category():
    """Update panel category from preferences"""
    try:
        prefs = bpy.context.preferences.addons['manutools'].preferences
        category = prefs.panel_category
    except:
        category = "ManuTools"  # Default fallback
    
    # Update all panels
    panels = [
        MANUTOOLS_PT_ToolsPanel,
        MANUTOOLS_PT_lp_hp_matcher,
        MANUTOOLS_PT_IDPanel,
        MANUTOOLS_PT_shapekeysmanager,
        MANUTOOLS_PT_attributes_manager,
        MANUTOOLS_PT_help,
    ]

    for panel in panels:
        try:
            bpy.utils.unregister_class(panel)
        except:
            pass
        panel.bl_category = category
        bpy.utils.register_class(panel)

def register():
    bpy.utils.register_class(MANUTOOLS_OT_open_preferences)
    bpy.utils.register_class(MANUTOOLS_OT_open_url)
    bpy.utils.register_class(MANUTOOLS_OT_contact_support)
    update_panel_category()

def unregister():
    bpy.utils.unregister_class(MANUTOOLS_PT_help)
    bpy.utils.unregister_class(MANUTOOLS_PT_attributes_manager)
    bpy.utils.unregister_class(MANUTOOLS_PT_shapekeysmanager)
    bpy.utils.unregister_class(MANUTOOLS_PT_IDPanel)
    bpy.utils.unregister_class(MANUTOOLS_PT_lp_hp_matcher)
    bpy.utils.unregister_class(MANUTOOLS_PT_ToolsPanel)
    bpy.utils.unregister_class(MANUTOOLS_OT_contact_support)
    bpy.utils.unregister_class(MANUTOOLS_OT_open_url)
    bpy.utils.unregister_class(MANUTOOLS_OT_open_preferences)