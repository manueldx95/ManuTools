bl_info = {
    "name": "ManuTools",
    "author": "Manuel D'Onofrio",
    "version": (1, 1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > ManuTools",
    "description": "Collection of tools and functions in one Addon",
    "doc_url": "https://www.artstation.com/manueldonofrio",
    "category": "Mesh",
}

import sys
import importlib
import bpy
from bpy.types import AddonPreferences

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

    def draw(self, context):
        layout = self.layout
        
        # ==================== UI ManuTools ====================
        box = layout.box()
        box.label(text="ManuTools Settings", icon='TOOL_SETTINGS')
        
        # Placeholder per future impostazioni
        box.label(text="No additional settings available")


def register():
    global __addon_enabled__
    __addon_enabled__ = True
    
    try:
        # Registra prima le preferenze
        bpy.utils.register_class(ManuToolsPreferences)
        
        # Poi registra i moduli
        for m in modules:
            if hasattr(m, 'register'):
                m.register()
            else:
                print(f"[MANUTOOLS] Warning: {m.__name__} non ha funzione register()")
    except Exception as e:
        print(f"[MANUTOOLS] Errore durante register: {e}")
        __addon_enabled__ = False
        raise


def unregister():
    global __addon_enabled__
    __addon_enabled__ = False
    
    try:
        # Unregistra i moduli prima
        for m in reversed(modules):
            if hasattr(m, 'unregister'):
                m.unregister()
            else:
                print(f"[MANUTOOLS] Warning: {m.__name__} non ha funzione unregister()")
        
        # Poi unregistra le preferenze
        bpy.utils.unregister_class(ManuToolsPreferences)
    except Exception as e:
        print(f"[MANUTOOLS] Errore durante unregister: {e}")
        raise


# Per testing/debug
if __name__ == "__main__":
    register()