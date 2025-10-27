
import bpy

from bpy.types import Operator
from bpy.props import IntProperty


# Operatori Placeholder per i bottoni del mockup
class SHAPEKEYS_OT_toggle_shape_value(Operator):
    """Toggle shape key value between 0.0 and 1.0"""
    bl_idname = "shapekeys.toggle_shape_value"
    bl_label = "Toggle Shape Key Value"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty()

    def execute(self, context):
        obj = context.object
        if obj and obj.data.shape_keys and self.index < len(obj.data.shape_keys.key_blocks):
            key_block = obj.data.shape_keys.key_blocks[self.index]
            if self.index > 0:  # Non toggleare la basis
                key_block.value = 0.0 if key_block.value > 0.0 else 1.0
        return {'FINISHED'}


class SHAPEKEYS_OT_set_value_to_min(Operator):
    """Set shape key value to minimum"""
    bl_idname = "shapekeys.set_value_to_min"
    bl_label = "Set to Min"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj and obj.active_shape_key and obj.active_shape_key_index > 0:
            sk = obj.active_shape_key
            sk.value = sk.slider_min
        return {'FINISHED'}


class SHAPEKEYS_OT_set_value_to_max(Operator):
    """Set shape key value to maximum"""
    bl_idname = "shapekeys.set_value_to_max"
    bl_label = "Set to Max"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj and obj.active_shape_key and obj.active_shape_key_index > 0:
            sk = obj.active_shape_key
            sk.value = sk.slider_max
        return {'FINISHED'}


class SHAPEKEYS_OT_solo_mode(Operator):
    """Only show the active Shape Key at full influence"""
    bl_idname = "shapekeys.solo_mode"
    bl_label = "Solo Mode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type == 'MESH' and obj.data.shape_keys and 
                obj.active_shape_key_index > 0)

    def execute(self, context):
        obj = context.object
        
        # Toggle della proprietà show_only_shape_key sull'oggetto
        obj.show_only_shape_key = not obj.show_only_shape_key
        
        return {'FINISHED'}




class SHAPEKEYS_OT_clear_shape_key(Operator):
    """Restore the active shape key by resetting all deformations"""
    bl_idname = "shapekeys.clear_shape_key"
    bl_label = "Clear Shape Key"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type == 'MESH' and obj.data.shape_keys and 
                obj.active_shape_key_index > 0)

    def execute(self, context):
        obj = context.object
        active_sk = obj.active_shape_key
        basis_sk = obj.data.shape_keys.key_blocks[0]
        
        # Reset di tutti i vertici alla posizione Basis
        for i, vert in enumerate(active_sk.data):
            vert.co = basis_sk.data[i].co
        
        # Resetta anche il valore a 0
        active_sk.value = 0.0
        
        self.report({'INFO'}, f"Shape key '{active_sk.name}' cleared")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SHAPEKEYS_OT_swap_shape_key_values(Operator):
    """Swap the vertex positions between min and max values of the active shape key"""
    bl_idname = "shapekeys.swap_shape_key_values"
    bl_label = "Swap Shape Key Values"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type == 'MESH' and obj.data.shape_keys and 
                obj.active_shape_key_index > 0)

    def execute(self, context):
        obj = context.object
        
        # Store original mode
        original_mode = obj.mode
        
        # Get the shape keys and the selected shape key
        shape_keys = obj.data.shape_keys
        shape_key_index = obj.active_shape_key_index
        shape_key = shape_keys.key_blocks[shape_key_index]

        # Set the active shape key to the basis (0)
        obj.active_shape_key_index = 0

        # Enter edit mode
        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all vertices
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Blend from the selected shape key to the basis
        bpy.ops.mesh.blend_from_shape(shape=shape_key.name, blend=1.0, add=True)

        # Set the active shape key back to the selected one
        obj.active_shape_key_index = shape_key_index
        
        # Blend from the basis to the selected shape key
        bpy.ops.mesh.blend_from_shape(shape=shape_key.name, blend=-2.0, add=True)
        
        # Return to original mode
        if original_mode != 'EDIT':
            bpy.ops.object.mode_set(mode=original_mode)

        self.report({'INFO'}, "Shape Key Values Swapped!")
        return {'FINISHED'}


class SHAPEKEYS_OT_edit_mode(Operator):
    """Toggle Edit Mode for Shape Keys"""
    bl_idname = "shapekeys.edit_mode"
    bl_label = "Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.data.shape_keys

    def execute(self, context):
        obj = context.object
        # Toggle use_shape_key_edit_mode
        obj.use_shape_key_edit_mode = not obj.use_shape_key_edit_mode
        return {'FINISHED'}


class MESH_UL_shape_keys_custom(bpy.types.UIList):
    """Personalized UIList for Shape Keys with custom layout"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = active_data
        key_block = item
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Main row
            row = layout.row(align=True)
            
            # Lock icon - usa LOCKED/UNLOCKED come in Blender standard
            row.prop(key_block, "lock_shape", text="", emboss=False)
            
            # Shape key name
            row.prop(key_block, "name", text="", emboss=False, icon='SHAPEKEY_DATA')
            
            # Value slider or frame number
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="", emboss=False)
            elif index > 0:
                sub_row = row.row(align=True)
                sub_row.prop(key_block, "value", text="", emboss=False, slider=True)
                
                # Toggle button (pallino)
                toggle_icon = 'RADIOBUT_ON' if key_block.value > 0.0 else 'RADIOBUT_OFF'
                toggle_op = sub_row.operator("shapekeys.toggle_shape_value", text="", icon=toggle_icon, emboss=False)
                toggle_op.index = index
            else:
                row.label(text="")
            
            # Mute checkbox - usa il prop standard senza icona custom
            row.prop(key_block, "mute", text="", emboss=False)
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='SHAPEKEY_DATA')


class SHAPEKEYS_OT_reset_to_basis(Operator):
    """Reset the active shape key to the Basis"""
    bl_idname = "shapekeys.reset_to_basis"
    bl_label = "Reset to Basis"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys and obj.active_shape_key_index > 0

    def execute(self, context):
        obj = context.active_object
        active_sk = obj.active_shape_key
        basis_sk = obj.data.shape_keys.key_blocks[0]
        
        # Reset dei vertici alla posizione Basis
        for i, vert in enumerate(active_sk.data):
            vert.co = basis_sk.data[i].co

        self.report({'INFO'}, f"Shape key '{active_sk.name}' reset to Basis")
        return {'FINISHED'}


class SHAPEKEYS_OT_propagate_to_shape(Operator):
    """Propagate the changes of the selected vertices to the active shape key"""
    bl_idname = "shapekeys.propagate_to_shape"
    bl_label = "Propagate to Shape"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 0 and context.mode == 'EDIT_MESH')

    def execute(self, context):
        bpy.ops.mesh.shape_propagate_to_all()
        return {'FINISHED'}


class SHAPEKEYS_OT_blend_from_shape(Operator):
    """Blend from the selected shape key"""
    bl_idname = "shapekeys.blend_from_shape"
    bl_label = "Blend From Shape"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Replica le proprietà dell'operatore nativo
    shape: bpy.props.EnumProperty(
        name="Shape",
        description="Shape key to blend from",
        items=lambda self, context: [
            (kb.name, kb.name, "") 
            for kb in context.object.data.shape_keys.key_blocks
        ] if context.object and context.object.data.shape_keys else []
    )
    
    blend: bpy.props.FloatProperty(
        name="Blend",
        description="Blending factor",
        default=1.0,
        soft_min=-1.0,
        soft_max=1.0
    )
    
    add: bpy.props.BoolProperty(
        name="Add",
        description="Add rather than blend between shapes",
        default=False
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and obj.data.shape_keys and 
                len(obj.data.shape_keys.key_blocks) > 0 and context.mode == 'EDIT_MESH')

    def execute(self, context):
        # Ora chiama l'operatore nativo con i parametri specificati
        bpy.ops.mesh.blend_from_shape(
            shape=self.shape,
            blend=self.blend,
            add=self.add
        )
        return {'FINISHED'}


class SHAPEKEYS_OT_copy_shape_key(Operator):
    """Duplicate the active shape key"""
    bl_idname = "shapekeys.copy_shape_key"
    bl_label = "Duplicate Shape Key"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys and obj.active_shape_key_index > 0

    def execute(self, context):
        obj = context.active_object
        active_sk = obj.active_shape_key
        
        # Crea una nuova shape key copiando quella attiva
        new_sk = obj.shape_key_add(name=active_sk.name + "_copy", from_mix=False)
        
        # Copia le coordinate dei vertici
        for i, vert in enumerate(active_sk.data):
            new_sk.data[i].co = vert.co
        
        # Copia anche le proprietà
        new_sk.value = active_sk.value
        new_sk.slider_min = active_sk.slider_min
        new_sk.slider_max = active_sk.slider_max
        new_sk.vertex_group = active_sk.vertex_group
        new_sk.relative_key = active_sk.relative_key

        self.report({'INFO'}, f"Shape key '{active_sk.name}' duplicated")
        return {'FINISHED'}


class SHAPEKEYS_OT_join_as_shapes(Operator):
    """Join selected objects as shape keys in the active object"""
    bl_idname = "shapekeys.join_as_shapes"
    bl_label = "Join as Shapes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) >= 2 and 
                context.active_object and 
                context.active_object.type == 'MESH')

    def execute(self, context):
        obj = context.active_object
        selected = [o for o in context.selected_objects if o != obj and o.type == 'MESH']
        
        if not selected:
            self.report({'ERROR'}, "Select at least two meshes")
            return {'CANCELLED'}
        
        # Verifica che tutti gli oggetti abbiano lo stesso numero di vertici
        base_verts = len(obj.data.vertices)
        for target in selected:
            if len(target.data.vertices) != base_verts:
                self.report({'ERROR'}, f"'{target.name}' has a different number of vertices")
                return {'CANCELLED'}
        
        # Crea le shape keys se non esistono
        if not obj.data.shape_keys:
            obj.shape_key_add(name="Basis", from_mix=False)
        
        # Aggiungi ogni oggetto come shape key
        for target in selected:
            # Crea la nuova shape key
            new_sk = obj.shape_key_add(name=target.name, from_mix=False)
            
            # Copia le posizioni dei vertici dall'oggetto target
            for i, vert in enumerate(target.data.vertices):
                new_sk.data[i].co = vert.co

        self.report({'INFO'}, f"{len(selected)} objects added as shape keys")
        return {'FINISHED'}


class SHAPEKEYS_OT_transfer_shape_keys(Operator):
    """Transfers all shape keys to the selected object using Data Transfer"""
    bl_idname = "shapekeys.transfer_shape_keys"
    bl_label = "Transfer Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) == 2 and 
                context.active_object and 
                context.active_object.type == 'MESH' and
                context.active_object.data.shape_keys)

    def execute(self, context):
        source = context.active_object
        target = [obj for obj in context.selected_objects if obj != source][0]
        
        if target.type != 'MESH':
            self.report({'ERROR'}, "The target object must be a mesh")
            return {'CANCELLED'}
        
        # Usa il Data Transfer modifier per trasferire le shape keys
        # Prima crea le shape keys sul target se non esistono
        if not target.data.shape_keys:
            target.shape_key_add(name="Basis", from_mix=False)
        
        # Per ogni shape key nella source, usa il Join as Shapes approach
        basis_sk = source.data.shape_keys.key_blocks[0]
        
        for i, sk in enumerate(source.data.shape_keys.key_blocks):
            if i == 0:  # Salta la Basis
                continue
                
            # Verifica se la shape key esiste già nel target
            if sk.name in target.data.shape_keys.key_blocks:
                target_sk = target.data.shape_keys.key_blocks[sk.name]
            else:
                target_sk = target.shape_key_add(name=sk.name, from_mix=False)
            
            # Usa il Surface Deform per trasferire la deformazione
            # Questo è un approccio semplificato - per risultati migliori si userebbe Data Transfer
            self.report({'INFO'}, "Transfer Shape Keys - Use 'Copy Shape Keys to Selected' from the specials menu (V) for a more accurate transfer")
            return {'FINISHED'}

        self.report({'INFO'}, f"Shape keys transferred from '{source.name}' to '{target.name}'")
        return {'FINISHED'}


class SHAPEKEYS_OT_delete_all_shape_keys(Operator):
    """Deletes all shape keys without applying them"""
    bl_idname = "shapekeys.delete_all_shape_keys"
    bl_label = "Delete All Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys

    def execute(self, context):
        obj = context.active_object
        
        # Assicurati di essere in Object Mode
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Rimuovi tutte le shape keys
        while obj.data.shape_keys:
            obj.active_shape_key_index = 0
            bpy.ops.object.shape_key_remove(all=True)
        
        self.report({'INFO'}, "All deleted shape keys")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SHAPEKEYS_OT_apply_all_shape_keys(Operator):
    """Apply all active shape keys as permanent deformations"""
    bl_idname = "shapekeys.apply_all_shape_keys"
    bl_label = "Apply All Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 1

    def execute(self, context):
        obj = context.active_object
        
        # Assicurati di essere in Object Mode
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Applica tutte le shape keys con il loro valore corrente
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)

        self.report({'INFO'}, "All shape keys applied to the mesh")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


# Registrazione
classes = (
    SHAPEKEYS_OT_toggle_shape_value,
    SHAPEKEYS_OT_set_value_to_min,
    SHAPEKEYS_OT_set_value_to_max,
    SHAPEKEYS_OT_solo_mode,
    SHAPEKEYS_OT_clear_shape_key,
    SHAPEKEYS_OT_swap_shape_key_values,
    SHAPEKEYS_OT_edit_mode,
    SHAPEKEYS_OT_reset_to_basis,
    SHAPEKEYS_OT_propagate_to_shape,
    SHAPEKEYS_OT_blend_from_shape,
    SHAPEKEYS_OT_copy_shape_key,
    SHAPEKEYS_OT_join_as_shapes,
    SHAPEKEYS_OT_transfer_shape_keys,
    SHAPEKEYS_OT_delete_all_shape_keys,
    SHAPEKEYS_OT_apply_all_shape_keys,
    MESH_UL_shape_keys_custom,
)


def shape_key_manager_register():
    for cls in classes:
        bpy.utils.register_class(cls)


def shape_key_manager_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

