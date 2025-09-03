import bpy
import random

# Preset di colori (nome, colore RGBA)
COLOR_PRESETS = [
    ("Red",  (1.0, 0.0, 0.0, 1.0)),
    ("Orange",    (1.0, 0.3, 0.0, 1.0)),
    ("Blue",      (0.0, 0.0, 1.0, 1.0)),
    ("Yellow",   (1.0, 1.0, 0.0, 1.0)),
    ("Green",    (0.0, 1.0, 0.0, 1.0)),
    ("Magenta", (1.0, 0.0, 1.0, 1.0)),
    ("Black", (0.0, 0.0, 0.0, 1.0)),
    ("White", (1.0, 1.0, 1.0, 1.0)),
]

class MANUTOOLS_PT_IDPanel(bpy.types.Panel):
    bl_label = "Vertex ID Color"
    bl_idname = "MANUTOOLS_PT_id_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ManuTools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.vertex_color_tool

        row = layout.row(align=True) # Crea una riga per il colore e il bottone
        row.prop(props, "color", text="")
        row.operator("object.randomize_vertex_color", icon='FILE_REFRESH') # Aggiungi l'operatore alla stessa riga

        layout.label(text="ID Color:")

        grid = layout.grid_flow(columns=3, even_columns=True)
        for name, col in COLOR_PRESETS[:-2]:
            op = grid.operator("object.set_color_preset", text=name )
            op.color = col

        # Riga separata per Black e White
        bw_row = layout.row(align=True)
        for name, col in COLOR_PRESETS[-2:]: # Prendi solo gli ultimi due
            op = bw_row.operator("object.set_color_preset", text=name )
            op.color = col


        layout.separator()
        apply_row = layout.row(align=True) # Crea una riga per i due bottoni
        apply_row.operator("object.apply_vertex_color", icon='BRUSH_DATA')
        apply_row.operator("view3d.toggle_viewport_color_vertex", text="", icon='MATERIAL_DATA', depress=props.show_vertex_color)

        


