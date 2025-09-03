import bpy

class RENAME_OT_SwapObjectNames(bpy.types.Operator):
    """Swap the names of two meshes selected in the Outliner."""
    bl_idname = "rename.swap_object_names"
    bl_label = "Swap Name"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        selected_objects = context.selected_objects
        return len(selected_objects) == 2 and all(obj.type == 'MESH' for obj in selected_objects)

    def execute(self, context):
        selected_objects = context.selected_objects
        name1 = selected_objects[0].name
        name2 = selected_objects[1].name
        
        # Scambio dei nomi
        selected_objects[0].name = "TEMP_SWAP_NAME_12345"
        selected_objects[1].name = name1
        selected_objects[0].name = name2
        
        self.report({'INFO'}, "Names successfully swapped!")
        return {'FINISHED'}

def menu_func_add_item(self, context):
    self.layout.operator(RENAME_OT_SwapObjectNames.bl_idname)

def swap_names_register():
    bpy.utils.register_class(RENAME_OT_SwapObjectNames)
    bpy.types.OUTLINER_MT_object.append(menu_func_add_item)

def swap_names_unregister():
    bpy.utils.unregister_class(RENAME_OT_SwapObjectNames)
    bpy.types.OUTLINER_MT_object.remove(menu_func_add_item)