import bpy
import random

# Funzione che assegna il colore ai vertici selezionati in Edit mode o all'intera mesh in Object mode
def set_vertex_colors(obj, color):
    original_mode = obj.mode
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    mesh = obj.data
    if not mesh.vertex_colors:
        mesh.vertex_colors.new(name="IDColor")
    color_layer = mesh.vertex_colors.active

    # Determina se siamo in Object mode o Edit mode basandosi sulla modalità originale
    if original_mode == 'OBJECT':
        # Object mode: applica il colore a tutta la mesh
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                color_layer.data[loop_index].color = color
    else:
        # Edit mode: applica il colore solo alle facce selezionate
        for poly in mesh.polygons:
            if poly.select:
                for loop_index in poly.loop_indices:
                    color_layer.data[loop_index].color = color

    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode=original_mode)


class ApplyVertexColorOperator(bpy.types.Operator):
    """Apply selected color to active or selected mesh objects"""
    bl_idname = "object.apply_vertex_color"
    bl_label = "Apply ID Color"

    def execute(self, context):
        props = context.scene.vertex_color_tool
        color = (props.color[0], props.color[1], props.color[2], 1.0)
        
        # Ottieni tutti gli oggetti selezionati
        selected_objects = context.selected_objects
        
        # Filtra solo le mesh
        mesh_objects = [obj for obj in selected_objects if obj.type == 'MESH']
        
        if not mesh_objects:
            self.report({'ERROR'}, "No mesh selected.")
            return {'CANCELLED'}
        
        # Salva l'oggetto attivo corrente
        original_active = context.active_object
        
        # Applica il colore a tutti gli oggetti mesh selezionati
        for obj in mesh_objects:
            # Imposta temporaneamente l'oggetto come attivo per le operazioni
            context.view_layer.objects.active = obj
            set_vertex_colors(obj, color)
        
        # Ripristina l'oggetto attivo originale
        context.view_layer.objects.active = original_active
        
        # Report di successo
        if len(mesh_objects) == 1:
            self.report({'INFO'}, f"Color applied to {mesh_objects[0].name}")
        else:
            self.report({'INFO'}, f"Color applied to {len(mesh_objects)} objects")

        return {'FINISHED'}


class SetColorPresetOperator(bpy.types.Operator):
    """Set the vertex color from a predefined color preset"""
    bl_idname = "object.set_color_preset"
    bl_label = "Set Color Preset"

    color: bpy.props.FloatVectorProperty(size=4)

    def execute(self, context):
        context.scene.vertex_color_tool.color = self.color[:3]
        return {'FINISHED'}


class RandomizeColorOperator(bpy.types.Operator):
    """Randomize the vertex color"""
    bl_idname = "object.randomize_vertex_color"
    bl_label = "Shuffle"

    def execute(self, context):
        props = context.scene.vertex_color_tool
        random_color = (random.random(), random.random(), random.random())
        props.color = random_color
        return {'FINISHED'}


class ToggleViewportColorVertexOperator(bpy.types.Operator):
    """Toggle viewport display to Vertex Color"""
    bl_idname = "view3d.toggle_viewport_color_vertex"
    bl_label = "Vertex Color"
    bl_options = {'REGISTER', 'UNDO'}

    previous_color_type: bpy.props.StringProperty(default='MATERIAL')

    def execute(self, context):
        props = context.scene.vertex_color_tool

        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            if space.shading.color_type == 'VERTEX':
                                space.shading.color_type = self.previous_color_type
                                props.show_vertex_color = False
                            else:
                                self.previous_color_type = space.shading.color_type
                                space.shading.color_type = 'VERTEX'
                                props.show_vertex_color = True
                            return {'FINISHED'}
        return {'CANCELLED'}


class VertexColorProperties(bpy.types.PropertyGroup):
    """Store properties for vertex color tools"""
    color: bpy.props.FloatVectorProperty(
        name="Color",
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