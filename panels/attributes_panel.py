import bpy
from bpy.types import Panel

# Pannello principale
class MANUTOOLS_PT_attributes_manager(Panel):
    bl_label = "Attributes"
    bl_idname = "MANUTOOLS_PT_attributes_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ManuTools"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        mesh = obj.data
        props = context.scene.attributes_panel_props
        
        # Lista attributi con template_list
        row = layout.row()
        
        # Usa il template_list nativo di Blender per gli attributi
        row.template_list(
            "MESH_UL_attributes_custom", "",
            mesh, "attributes",
            mesh.attributes, "active_index",
            rows=4
        )
        
        # Colonna bottoni a destra
        col_buttons = row.column(align=True)
        col_buttons.operator("mesh.attribute_add_custom", text="", icon='ADD')
        col_buttons.operator("mesh.attribute_remove_selected", text="", icon='REMOVE')
        col_buttons.separator()
        col_buttons.menu("MESH_MT_attribute_convert_menu", text="", icon='TRIA_DOWN')
        col_buttons.separator()
        col_buttons.prop(props, "show_system_attributes", toggle=True, icon='FILTER', icon_only=True)
        
        # Bottoni Add rapidi
        row = layout.row(align=True)
        row.operator("mesh.add_vertex_attribute", text="Add Vertex", icon='ADD')
        row.operator("mesh.add_edge_attribute", text="Add Edge", icon='ADD')
        row.operator("mesh.add_face_attribute", text="Add Face", icon='ADD')
        
        layout.separator()
        
        row = layout.row()
        
        sub = row.row(align=True)
        sub.operator("mesh.attribute_assign", text="Assign")
        sub.operator("mesh.attribute_remove", text="Remove")
        
        sub = row.row(align=True)
        sub.operator("mesh.attribute_select", text="Select")
        sub.operator("mesh.attribute_deselect", text="Deselect")
        
        layout.separator()
        
        # Campo Weight
        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(props, "weight", slider=True)