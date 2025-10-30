bl_info = {
    "name": "ManuTools",
    "author": "Manuel D'Onofrio",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > ManuTools",
    "description": "Collection of tools and functions for 3D modeling workflow",
    "doc_url": "https://www.artstation.com/manueldonofrio",
    "category": "Mesh",
}

import importlib
import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty

# Richiesto da Blender per evitare il warning
__addon_enabled__ = False

# Import dei moduli principali
from . import operators, panels

# Lista dei moduli per il reload
modules = [operators, panels]

# Reload dei moduli se già caricati (per sviluppo)
if "bpy" in locals():
    for m in modules:
        importlib.reload(m)


class ManuToolsPreferences(AddonPreferences):
    bl_idname = __name__

    # Naming Conventions
    lowpoly_suffix: StringProperty(
        name="Low Poly Suffix",
        description="Suffix for low poly objects",
        default="_lp",
    )
    
    highpoly_suffix: StringProperty(
        name="High Poly Suffix",
        description="Suffix for high poly objects",
        default="_hp",
    )
    
    # LP/HP Matching
    max_matching_distance: FloatProperty(
        name="Max Matching Distance",
        description="Maximum distance for automatic LP/HP matching",
        default=5.0,
        min=0.1,
        max=100.0,
    )
    
    auto_rename_on_match: BoolProperty(
        name="Auto Rename on Match",
        description="Automatically rename HP objects when matched",
        default=True
    )
    
    # Face Sets Shortcuts
    enable_faceset_shortcuts: BoolProperty(
        name="Enable Face Set Shortcuts",
        description="Enable keyboard shortcuts (requires restart)",
        default=True
    )
    
    faceset_select_key: EnumProperty(
        name="Select Key",
        description="Key for selecting Face Set",
        items=[
            ('K', "K", ""),
            ('L', "L", ""),
            ('M', "M", ""),
            ('J', "J", ""),
        ],
        default='K'
    )
    
    faceset_select_modifier: EnumProperty(
        name="Select Modifier",
        items=[
            ('CTRL', "Ctrl", ""),
            ('ALT', "Alt", ""),
            ('SHIFT', "Shift", ""),
        ],
        default='CTRL'
    )
    
    faceset_add_modifier: EnumProperty(
        name="Add Modifier",
        items=[
            ('SHIFT', "Shift", ""),
            ('CTRL', "Ctrl", ""),
            ('ALT', "Alt", ""),
        ],
        default='SHIFT'
    )
    
    faceset_subtract_modifier: EnumProperty(
        name="Subtract Modifier",
        items=[
            ('ALT', "Alt", ""),
            ('CTRL', "Ctrl", ""),
            ('SHIFT', "Shift", ""),
        ],
        default='ALT'
    )
    
    # UI
    panel_category: StringProperty(
        name="Panel Category",
        description="Sidebar category name (requires restart)",
        default="ManuTools"
    )
    

    def draw(self, context):
        layout = self.layout
        
        # HEADER
        box = layout.box()
        row = box.row()
        row.label(text="ManuTools Preferences", icon='PREFERENCES')
        
        # NAMING CONVENTIONS
        box = layout.box()
        box.label(text="Naming Conventions", icon='SORTALPHA')
        
        split = box.split(factor=0.5)
        col = split.column()
        col.prop(self, "lowpoly_suffix")
        col = split.column()
        col.prop(self, "highpoly_suffix")
        
        # Warning per suffissi
        if not self.lowpoly_suffix or not self.highpoly_suffix:
            row = box.row()
            row.alert = True
            row.label(text="⚠ Suffixes cannot be empty!", icon='ERROR')
        
        if self.lowpoly_suffix == self.highpoly_suffix:
            row = box.row()
            row.alert = True
            row.label(text="⚠ LP and HP suffixes must be different!", icon='ERROR')
        
        # LP/HP MATCHING
        box = layout.box()
        box.label(text="LP/HP Auto Matching", icon='LINK_BLEND')
        
        col = box.column(align=True)
        col.prop(self, "max_matching_distance")
        col.prop(self, "auto_rename_on_match")
        
        # Info box
        info_box = box.box()
        info_box.label(text="Tip: Lower distance values make matching more strict", icon='INFO')        
        
        # FACE SETS SHORTCUTS
        box = layout.box()
        box.label(text="Face Sets Shortcuts", icon='KEYINGSET')
        
        col = box.column(align=True)
        col.prop(self, "enable_faceset_shortcuts")
        
        if self.enable_faceset_shortcuts:
            col.separator()
            
            # Shortcut customization
            sub_box = col.box()
            sub_box.label(text="Customize Shortcuts:", icon='PREFERENCES')
            
            # Select shortcut
            split = sub_box.split(factor=0.35)
            split.label(text="Select Face Set:")
            row = split.row(align=True)
            row.prop(self, "faceset_select_modifier", text="")
            row.prop(self, "faceset_select_key", text="")
            
            # Add shortcut 
            split = sub_box.split(factor=0.35)
            split.label(text="Add to Selection:")
            row = split.row(align=True)
            row.prop(self, "faceset_add_modifier", text="")
            row.prop(self, "faceset_select_key", text="")
            
            # Subtract shortcut 
            split = sub_box.split(factor=0.35)
            split.label(text="Subtract from Selection:")
            row = split.row(align=True)
            row.prop(self, "faceset_subtract_modifier", text="")
            row.prop(self, "faceset_select_key", text="")
            
            col.separator()
            
            # Current shortcuts display - UNA SOLA RIGA ✨
            info_box = col.box()
            info_box.label(text="Current Shortcuts:", icon='INFO')
            
            # Build shortcut display strings
            select_mod = self.faceset_select_modifier.title()
            add_mod = self.faceset_add_modifier.title()
            subtract_mod = self.faceset_subtract_modifier.title()
            key = self.faceset_select_key
            
            # TUTTO IN UNA RIGA ✨
            row = info_box.row(align=True)
            row.label(text=f"{select_mod}+{key}: Select")
            row.separator()
            row.label(text=f"{add_mod}+{key}: Add")
            row.separator()
            row.label(text=f"{subtract_mod}+{key}: Subtract")
            
            row = col.row()
            row.label(text="Changes require Blender restart", icon='ERROR')
        else:
            col.separator()
            col.label(text="Shortcuts are disabled", icon='CANCEL')
        
        # UI PREFERENCES
        box = layout.box()
        box.label(text="UI Preferences", icon='WINDOW')
        
        col = box.column(align=True)
        col.prop(self, "panel_category")
        
        row = col.row()
        row.label(text="Panel category change requires restart", icon='ERROR')
        
        # RESET TO DEFAULTS
        layout.separator()
        box = layout.box()
        row = box.row()
        row.operator("manutools.reset_preferences", icon='LOOP_BACK', text="Reset All to Defaults")


class MANUTOOLS_OT_reset_preferences(bpy.types.Operator):
    """Reset all ManuTools preferences to default values"""
    bl_idname = "manutools.reset_preferences"
    bl_label = "Reset Preferences"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        addon_name = __name__
        prefs = context.preferences.addons[addon_name].preferences
        
        # Reset a valori di default
        prefs.lowpoly_suffix = "_lp"
        prefs.highpoly_suffix = "_hp"
        prefs.max_matching_distance = 5.0
        prefs.auto_rename_on_match = True
        prefs.enable_faceset_shortcuts = True
        prefs.faceset_select_key = 'K'
        prefs.faceset_select_modifier = 'CTRL'
        prefs.faceset_add_modifier = 'SHIFT'
        prefs.faceset_subtract_modifier = 'ALT'
        prefs.compact_panels = False
        prefs.show_tooltips = True
        prefs.panel_category = "ManuTools"
        
        self.report({'INFO'}, "Preferences reset to defaults")
        return {'FINISHED'}


def register():
    global __addon_enabled__
    __addon_enabled__ = True
    
    try:
        # Registra prima le preferenze  ✨ AGGIUNTO
        bpy.utils.register_class(MANUTOOLS_OT_reset_preferences)
        bpy.utils.register_class(ManuToolsPreferences)
        
        # Poi registra i moduli  ✨ AGGIUNTO
        for m in modules:
            if hasattr(m, 'register'):
                m.register()
            else:
                print(f"[MANUTOOLS] Warning: {m.__name__} has no register function()")
    except Exception as e:
        print(f"[MANUTOOLS] Error during register: {e}")
        __addon_enabled__ = False
        raise


def unregister():
    global __addon_enabled__
    __addon_enabled__ = False
    
    try:
        # Unregistra i moduli prima  ✨ AGGIUNTO
        for m in reversed(modules):
            if hasattr(m, 'unregister'):
                m.unregister()
            else:
                print(f"[MANUTOOLS] Warning: {m.__name__} has no unregister function()")
        
        # Poi unregistra le preferenze  ✨ AGGIUNTO
        bpy.utils.unregister_class(ManuToolsPreferences)
        bpy.utils.unregister_class(MANUTOOLS_OT_reset_preferences)
    except Exception as e:
        print(f"[MANUTOOLS] Error during unregister: {e}")
        raise


if __name__ == "__main__":
    register()
