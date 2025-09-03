import bpy

class MANUTOOLS_PT_ShapekeyCopyPanel(bpy.types.Panel):
    bl_label = "Shapekeys Copy"
    bl_idname = "MANUTOOLS_PT_ShapekeysCopy_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ManuTools"
    #bl_options = "DEFAULT_CLOSED"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Select sources then target and click the button.")
        col = layout.column(align=True)
        # Add the "Name Only" checkbox
        col.prop(context.scene, "name_only", text="Name Only")
        col.prop(context.scene, "active_only", text="Active Only")
        col.operator("object.shapekey_transfer", text="Copy Shape keys", icon="COPYDOWN")
        col.operator("object.shapekey_animation_transfer", text="Copy Animation", icon="ANIM")