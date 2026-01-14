import bpy


class MANUTOOLS_OT_AddBevelModifier(bpy.types.Operator):
    """Add a custom Bevel modifier for modeling (Amount 0.003, Segments 2, Weight limit, Profile 1.0)"""
    bl_idname = "manutools.add_bevel_modifier"
    bl_label = "Add Bevel Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.type == 'MESH'

    def execute(self, context):
        obj = context.object

        # Se siamo in Edit Mode, passa temporaneamente a Object Mode
        was_in_edit = (context.mode == 'EDIT_MESH')
        if was_in_edit:
            bpy.ops.object.mode_set(mode='OBJECT')

        # Aggiungi il modificatore Bevel
        bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')

        # Configura le impostazioni
        bevel_mod.width = 0.003          # Amount
        bevel_mod.segments = 2            # Segments
        bevel_mod.limit_method = 'WEIGHT' # Limit Method su Weight
        bevel_mod.profile = 1.0           # Profile shape 1.0

        # Torna in Edit Mode se era attivo prima
        if was_in_edit:
            bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, "Bevel modifier added.")
        return {'FINISHED'}


classes = (
    MANUTOOLS_OT_AddBevelModifier,
)


def bevel_modifier_register():
    for cls in classes:
        bpy.utils.register_class(cls)


def bevel_modifier_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
