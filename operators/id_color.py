import bpy
import random

# Funzione che assegna il colore ai vertici selezionati
def set_vertex_colors(obj, color):
    original_mode = obj.mode
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    mesh = obj.data
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="IDColor") # Aggiungi un nome al layer
    color_layer = mesh.vertex_colors.active

    for poly in mesh.polygons:
        if poly.select:
            for loop_index in poly.loop_indices:
                color_layer.data[loop_index].color = color

    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode=original_mode)


class ApplyVertexColorOperator(bpy.types.Operator):
    bl_idname = "object.apply_vertex_color"
    bl_label = "Apply ID Color"

    def execute(self, context):
        obj = context.active_object
        props = context.scene.vertex_color_tool

        if obj and obj.type == 'MESH':
            color = (props.color[0], props.color[1], props.color[2], 1.0)
            set_vertex_colors(obj, color)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Nessuna mesh selezionata.")
            return {'CANCELLED'}


class SetColorPresetOperator(bpy.types.Operator):
    bl_idname = "object.set_color_preset"
    bl_label = "Imposta Colore"

    color: bpy.props.FloatVectorProperty(size=4)

    def execute(self, context):
        context.scene.vertex_color_tool.color = self.color[:3]
        return {'FINISHED'}


class RandomizeColorOperator(bpy.types.Operator):
    bl_idname = "object.randomize_vertex_color"
    bl_label = "Shuffle" # Etichetta più corta

    def execute(self, context):
        props = context.scene.vertex_color_tool
        random_color = (random.random(), random.random(), random.random())
        props.color = random_color
        return {'FINISHED'}
    




class ToggleViewportColorVertexOperator(bpy.types.Operator):
    bl_idname = "view3d.toggle_viewport_color_vertex"
    bl_label = "Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}

    previous_color_type: bpy.props.StringProperty(default='MATERIAL') # Memorizza la modalità precedente

    def execute(self, context):
        props = context.scene.vertex_color_tool

        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            if space.shading.color_type == 'VERTEX':
                                space.shading.color_type = self.previous_color_type # Ripristina la modalità precedente
                                props.show_vertex_color = False
                            else:
                                self.previous_color_type = space.shading.color_type # Memorizza la modalità corrente
                                space.shading.color_type = 'VERTEX'
                                props.show_vertex_color = True
                            return {'FINISHED'}
        return {'CANCELLED'}
    







class VertexColorProperties(bpy.types.PropertyGroup):
    color: bpy.props.FloatVectorProperty(
        name="Colore",
        subtype='COLOR',
        min=0.0,
        max=1.0,
        default=(1.0, 0.0, 0.0)
    )
    show_vertex_color: bpy.props.BoolProperty(default=False)
        


classes = (
    VertexColorProperties,
    ApplyVertexColorOperator,
    SetColorPresetOperator,
    RandomizeColorOperator,
    ToggleViewportColorVertexOperator,
)

def id_color_register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vertex_color_tool = bpy.props.PointerProperty(type=VertexColorProperties)

def id_color_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vertex_color_tool