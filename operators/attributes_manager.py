import bpy
from bpy.types import Panel, Operator, PropertyGroup, UIList, Menu
from bpy.props import FloatProperty, StringProperty, IntProperty, BoolProperty

# Attributi di sistema da nascondere di default
SYSTEM_ATTRIBUTES = {
    'position', 'UVMap', 'material_index', 'sharp_edge', 
    'sharp_face', '.corner_edge', '.corner_vert', '.edge_verts'
}

# UIList personalizzata per gli attributi con icone custom
class MESH_UL_attributes_custom(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        attr = item
        props = context.scene.attributes_panel_props
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Icona personalizzata in base al dominio
            if attr.domain == 'POINT':
                custom_icon = 'VERTEXSEL'
                domain_display = "Vertex"
            elif attr.domain == 'EDGE':
                custom_icon = 'EDGESEL'
                domain_display = "Edge"
            elif attr.domain == 'FACE':
                custom_icon = 'FACESEL'
                domain_display = "Face"
            else:
                custom_icon = 'MESH_DATA'
                domain_display = attr.domain.title()
            
            # Nome attributo con icona custom
            layout.prop(attr, "name", text="", emboss=False, icon=custom_icon)
            
            # Tipo di dato
            if attr.data_type == 'BOOLEAN':
                type_display = "Boolean"
            else:
                type_display = attr.data_type.replace('_', ' ').title()
            
            layout.label(text=f"{domain_display} - {type_display}")
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MESH_DATA')
    
    def filter_items(self, context, data, propname):
        attrs = getattr(data, propname)
        props = context.scene.attributes_panel_props
        
        flt_flags = []
        flt_neworder = []
        
        # Filtra attributi di sistema
        if not props.show_system_attributes:
            for attr in attrs:
                if attr.name in SYSTEM_ATTRIBUTES or attr.name.startswith('.') or attr.name == 'UVMap' or attr.name.startswith('UVMap'):
                    flt_flags.append(0)  # Nascosto
                else:
                    flt_flags.append(self.bitflag_filter_item)  # Visibile
        else:
            flt_flags = [self.bitflag_filter_item] * len(attrs)
        
        return flt_flags, flt_neworder

# Property Group per salvare le proprietà
class AttributesPanelProperties(PropertyGroup):
    weight: FloatProperty(
        name="Weight",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Weight value for attribute"
    )
    
    show_system_attributes: BoolProperty(
        name="Show System Attributes",
        default=False,
        description="Show system attributes (UVMap, position, etc.)"
    )

# Operatori per gestione attributi
class MESH_OT_attribute_add(Operator):
    bl_idname = "mesh.attribute_add_custom"
    bl_label = "Add Attribute"
    bl_description = "Add new attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: StringProperty(
        name="Name",
        default="Attribute"
    )
    
    domain: bpy.props.EnumProperty(
        name="Domain",
        items=[
            ('POINT', "Vertex", "Vertex attribute"),
            ('EDGE', "Edge", "Edge attribute"),
            ('FACE', "Face", "Face attribute"),
        ],
        default='POINT'
    )
    
    data_type: bpy.props.EnumProperty(
        name="Data Type",
        items=[
            ('BOOLEAN', "Boolean", "True or False"),
            ('FLOAT', "Float", "Floating point value"),
            ('INT', "Integer", "Integer value"),
            ('FLOAT_VECTOR', "Vector", "3D vector"),
            ('FLOAT_COLOR', "Color", "RGBA color"),
        ],
        default='BOOLEAN'
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        # Crea nome unico
        base_name = self.name
        counter = 1
        unique_name = base_name
        
        while unique_name in mesh.attributes:
            unique_name = f"{base_name}.{counter:03d}"
            counter += 1
        
        # Aggiungi l'attributo
        mesh.attributes.new(name=unique_name, type=self.data_type, domain=self.domain)
        
        self.report({'INFO'}, f"Added attribute: {unique_name}")
        return {'FINISHED'}

class MESH_OT_attribute_remove_selected(Operator):
    bl_idname = "mesh.attribute_remove_selected"
    bl_label = "Remove Attribute"
    bl_description = "Remove selected attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if not context.object or context.object.type != 'MESH':
            return False
        mesh = context.object.data
        props = context.scene.attributes_panel_props
        
        # Verifica che ci sia un attributo selezionato
        if mesh.attributes.active_index < 0 or mesh.attributes.active_index >= len(mesh.attributes):
            return False
        
        # Verifica che l'attributo selezionato sia visibile (non filtrato)
        attr = mesh.attributes[mesh.attributes.active_index]
        if not props.show_system_attributes:
            if attr.name in SYSTEM_ATTRIBUTES or attr.name.startswith('.') or attr.name == 'UVMap' or attr.name.startswith('UVMap'):
                return False
        
        return True
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        attr_to_remove = mesh.attributes[mesh.attributes.active_index]
        attr_name = attr_to_remove.name
        
        # Rimuovi attributo
        mesh.attributes.remove(attr_to_remove)
        
        self.report({'INFO'}, f"Removed attribute: {attr_name}")
        return {'FINISHED'}

class MESH_OT_attribute_convert(Operator):
    bl_idname = "mesh.attribute_convert"
    bl_label = "Convert Attribute"
    bl_description = "Convert attribute to different domain"
    bl_options = {'REGISTER', 'UNDO'}
    
    domain: bpy.props.EnumProperty(
        name="Domain",
        items=[
            ('POINT', "Vertex", "Convert to vertex attribute"),
            ('EDGE', "Edge", "Convert to edge attribute"),
            ('FACE', "Face", "Convert to face attribute"),
        ]
    )
    
    @classmethod
    def poll(cls, context):
        if not context.object or context.object.type != 'MESH':
            return False
        mesh = context.object.data
        props = context.scene.attributes_panel_props
        
        # Verifica che ci sia un attributo selezionato
        if mesh.attributes.active_index < 0 or mesh.attributes.active_index >= len(mesh.attributes):
            return False
        
        # Verifica che l'attributo selezionato sia visibile (non filtrato)
        attr = mesh.attributes[mesh.attributes.active_index]
        if not props.show_system_attributes:
            if attr.name in SYSTEM_ATTRIBUTES or attr.name.startswith('.') or attr.name == 'UVMap' or attr.name.startswith('UVMap'):
                return False
        
        return True
    
    def execute(self, context):
        import bmesh
        
        obj = context.object
        mesh = obj.data
        attr = mesh.attributes[mesh.attributes.active_index]
        
        if attr.domain == self.domain:
            self.report({'INFO'}, f"Attribute already in {self.domain} domain")
            return {'CANCELLED'}
        
        # Salva i dati
        old_name = attr.name
        old_type = attr.data_type
        old_domain = attr.domain
        
        # Leggi i valori dall'attributo originale
        old_values = {}
        if old_type == 'BOOLEAN':
            for i, elem in enumerate(attr.data):
                old_values[i] = elem.value
        elif old_type == 'FLOAT':
            for i, elem in enumerate(attr.data):
                old_values[i] = elem.value
        elif old_type == 'INT':
            for i, elem in enumerate(attr.data):
                old_values[i] = elem.value
        
        # Crea nuovo attributo con dominio diverso
        new_attr = mesh.attributes.new(name=old_name + "_temp", type=old_type, domain=self.domain)
        
        # Usa bmesh per mappare i valori tra domini
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        # Mappa i valori dal dominio vecchio al nuovo
        new_values = {}
        
        if old_domain == 'FACE' and self.domain == 'POINT':
            # Da Face a Vertex: ogni vertice prende il valore delle facce a cui appartiene
            for i, face in enumerate(bm.faces):
                if i in old_values and old_values[i]:
                    for vert in face.verts:
                        new_values[vert.index] = old_values[i]
        
        elif old_domain == 'FACE' and self.domain == 'EDGE':
            # Da Face a Edge: ogni edge prende il valore delle facce a cui appartiene
            for i, face in enumerate(bm.faces):
                if i in old_values and old_values[i]:
                    for edge in face.edges:
                        new_values[edge.index] = old_values[i]
        
        elif old_domain == 'POINT' and self.domain == 'FACE':
            # Da Vertex a Face: la faccia è True se almeno un vertice è True
            for i, face in enumerate(bm.faces):
                for vert in face.verts:
                    if vert.index in old_values and old_values[vert.index]:
                        new_values[i] = old_values[vert.index]
                        break
        
        elif old_domain == 'POINT' and self.domain == 'EDGE':
            # Da Vertex a Edge: l'edge è True se almeno un vertice è True
            for i, edge in enumerate(bm.edges):
                for vert in edge.verts:
                    if vert.index in old_values and old_values[vert.index]:
                        new_values[i] = old_values[vert.index]
                        break
        
        elif old_domain == 'EDGE' and self.domain == 'POINT':
            # Da Edge a Vertex: ogni vertice prende il valore degli edge a cui appartiene
            for i, edge in enumerate(bm.edges):
                if i in old_values and old_values[i]:
                    for vert in edge.verts:
                        new_values[vert.index] = old_values[i]
        
        elif old_domain == 'EDGE' and self.domain == 'FACE':
            # Da Edge a Face: la faccia è True se almeno un edge è True
            for i, face in enumerate(bm.faces):
                for edge in face.edges:
                    if edge.index in old_values and old_values[edge.index]:
                        new_values[i] = old_values[edge.index]
                        break
        
        bm.free()
        
        # Applica i nuovi valori
        if old_type == 'BOOLEAN':
            for i, elem in enumerate(new_attr.data):
                elem.value = new_values.get(i, False)
        elif old_type == 'FLOAT':
            for i, elem in enumerate(new_attr.data):
                elem.value = new_values.get(i, 0.0)
        elif old_type == 'INT':
            for i, elem in enumerate(new_attr.data):
                elem.value = new_values.get(i, 0)
        
        # Rimuovi vecchio attributo
        mesh.attributes.remove(attr)
        
        # Rinomina nuovo attributo
        new_attr.name = old_name
        
        self.report({'INFO'}, f"Converted {old_name} to {self.domain}")
        return {'FINISHED'}

# Operatori per Assign/Remove/Select/Deselect
class MESH_OT_attribute_assign(Operator):
    bl_idname = "mesh.attribute_assign"
    bl_label = "Assign"
    bl_description = "Assign attribute value to selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH' or not context.object or context.object.type != 'MESH':
            return False
        mesh = context.object.data
        props = context.scene.attributes_panel_props
        
        # Verifica che ci sia un attributo selezionato
        if mesh.attributes.active_index < 0 or mesh.attributes.active_index >= len(mesh.attributes):
            return False
        
        # Verifica che l'attributo selezionato sia visibile (non filtrato)
        attr = mesh.attributes[mesh.attributes.active_index]
        if not props.show_system_attributes:
            if attr.name in SYSTEM_ATTRIBUTES or attr.name.startswith('.') or attr.name == 'UVMap' or attr.name.startswith('UVMap'):
                return False
        
        return True
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        props = context.scene.attributes_panel_props
        
        attr = mesh.attributes[mesh.attributes.active_index]
        
        # Imposta l'attributo attivo
        mesh.attributes.active = attr
        
        # Usa l'operatore nativo di Blender per assegnare attributi
        if attr.data_type == 'BOOLEAN':
            # Per booleani usa weight > 0.5 come True
            value_bool = props.weight > 0.5
            bpy.ops.mesh.attribute_set(value_bool=value_bool)
        elif attr.data_type == 'FLOAT':
            # Per float usa il valore weight direttamente
            bpy.ops.mesh.attribute_set(value_float=props.weight)
        elif attr.data_type == 'INT':
            # Per int converte weight in intero
            bpy.ops.mesh.attribute_set(value_int=int(props.weight * 100))
        else:
            self.report({'WARNING'}, f"Data type {attr.data_type} not supported for assignment")
            return {'CANCELLED'}
        
        self.report({'INFO'}, f"Assigned value to selection")
        return {'FINISHED'}

class MESH_OT_attribute_remove(Operator):
    bl_idname = "mesh.attribute_remove"
    bl_label = "Remove"
    bl_description = "Remove attribute value from selection (set to 0/False)"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH' or not context.object or context.object.type != 'MESH':
            return False
        mesh = context.object.data
        props = context.scene.attributes_panel_props
        
        # Verifica che ci sia un attributo selezionato
        if mesh.attributes.active_index < 0 or mesh.attributes.active_index >= len(mesh.attributes):
            return False
        
        # Verifica che l'attributo selezionato sia visibile (non filtrato)
        attr = mesh.attributes[mesh.attributes.active_index]
        if not props.show_system_attributes:
            if attr.name in SYSTEM_ATTRIBUTES or attr.name.startswith('.') or attr.name == 'UVMap' or attr.name.startswith('UVMap'):
                return False
        
        return True
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        attr = mesh.attributes[mesh.attributes.active_index]
        
        # Imposta l'attributo attivo
        mesh.attributes.active = attr
        
        # Usa l'operatore nativo per impostare a 0/False
        if attr.data_type == 'BOOLEAN':
            bpy.ops.mesh.attribute_set(value_bool=False)
        elif attr.data_type == 'FLOAT':
            bpy.ops.mesh.attribute_set(value_float=0.0)
        elif attr.data_type == 'INT':
            bpy.ops.mesh.attribute_set(value_int=0)
        else:
            self.report({'WARNING'}, f"Data type {attr.data_type} not supported")
            return {'CANCELLED'}
        
        self.report({'INFO'}, f"Removed value from selection")
        return {'FINISHED'}

class MESH_OT_attribute_select(Operator):
    bl_idname = "mesh.attribute_select"
    bl_label = "Select"
    bl_description = "Select geometry with this attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH' or not context.object or context.object.type != 'MESH':
            return False
        mesh = context.object.data
        props = context.scene.attributes_panel_props
        
        # Verifica che ci sia un attributo selezionato
        if mesh.attributes.active_index < 0 or mesh.attributes.active_index >= len(mesh.attributes):
            return False
        
        # Verifica che l'attributo selezionato sia visibile (non filtrato)
        attr = mesh.attributes[mesh.attributes.active_index]
        if not props.show_system_attributes:
            if attr.name in SYSTEM_ATTRIBUTES or attr.name.startswith('.') or attr.name == 'UVMap' or attr.name.startswith('UVMap'):
                return False
        
        return True
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        attr = mesh.attributes[mesh.attributes.active_index]
        
        # Usa l'operatore nativo di Blender per selezionare
        try:
            # Prima imposta l'attributo attivo
            mesh.attributes.active = attr
            
            # Poi usa select_by_attribute
            bpy.ops.mesh.select_by_attribute()
            
            self.report({'INFO'}, f"Selected elements with attribute")
        except Exception as e:
            self.report({'ERROR'}, f"Error selecting: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class MESH_OT_attribute_deselect(Operator):
    bl_idname = "mesh.attribute_deselect"
    bl_label = "Deselect"
    bl_description = "Deselect geometry with this attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH' or not context.object or context.object.type != 'MESH':
            return False
        mesh = context.object.data
        props = context.scene.attributes_panel_props
        
        # Verifica che ci sia un attributo selezionato
        if mesh.attributes.active_index < 0 or mesh.attributes.active_index >= len(mesh.attributes):
            return False
        
        # Verifica che l'attributo selezionato sia visibile (non filtrato)
        attr = mesh.attributes[mesh.attributes.active_index]
        if not props.show_system_attributes:
            if attr.name in SYSTEM_ATTRIBUTES or attr.name.startswith('.') or attr.name == 'UVMap' or attr.name.startswith('UVMap'):
                return False
        
        return True
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        attr = mesh.attributes[mesh.attributes.active_index]
        
        # Usa l'operatore nativo di Blender per deselezionare
        try:
            # Prima imposta l'attributo attivo
            mesh.attributes.active = attr
            
            # Salva la selezione corrente
            bpy.ops.mesh.select_all(action='INVERT')
            
            # Seleziona gli elementi con attributo
            bpy.ops.mesh.select_by_attribute()
            
            # Poi inverti la selezione per deselezionare
            bpy.ops.mesh.select_all(action='INVERT')
            
            self.report({'INFO'}, f"Deselected elements with attribute")
        except Exception as e:
            self.report({'ERROR'}, f"Error deselecting: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class MESH_OT_add_vertex_attribute(Operator):
    bl_idname = "mesh.add_vertex_attribute"
    bl_label = "Add Vertex"
    bl_description = "Add boolean vertex attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        # Crea nome unico
        base_name = "Vertex_Attr"
        counter = 1
        unique_name = base_name
        
        while unique_name in mesh.attributes:
            unique_name = f"{base_name}.{counter:03d}"
            counter += 1
        
        # Aggiungi attributo vertex booleano
        mesh.attributes.new(name=unique_name, type='BOOLEAN', domain='POINT')
        
        self.report({'INFO'}, f"Added vertex attribute: {unique_name}")
        return {'FINISHED'}

class MESH_OT_add_edge_attribute(Operator):
    bl_idname = "mesh.add_edge_attribute"
    bl_label = "Add Edge"
    bl_description = "Add boolean edge attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        # Crea nome unico
        base_name = "Edge_Attr"
        counter = 1
        unique_name = base_name
        
        while unique_name in mesh.attributes:
            unique_name = f"{base_name}.{counter:03d}"
            counter += 1
        
        # Aggiungi attributo edge booleano
        mesh.attributes.new(name=unique_name, type='BOOLEAN', domain='EDGE')
        
        self.report({'INFO'}, f"Added edge attribute: {unique_name}")
        return {'FINISHED'}

class MESH_OT_add_face_attribute(Operator):
    bl_idname = "mesh.add_face_attribute"
    bl_label = "Add Face"
    bl_description = "Add boolean face attribute"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        mesh = obj.data
        
        # Crea nome unico
        base_name = "Face_Attr"
        counter = 1
        unique_name = base_name
        
        while unique_name in mesh.attributes:
            unique_name = f"{base_name}.{counter:03d}"
            counter += 1
        
        # Aggiungi attributo face booleano
        mesh.attributes.new(name=unique_name, type='BOOLEAN', domain='FACE')
        
        self.report({'INFO'}, f"Added face attribute: {unique_name}")
        return {'FINISHED'}

# Menu per conversione attributi
class MESH_MT_attribute_convert_menu(Menu):
    bl_label = "Convert To"
    bl_idname = "MESH_MT_attribute_convert_menu"
    
    def draw(self, context):
        layout = self.layout
        op = layout.operator("mesh.attribute_convert", text="Vertex")
        op.domain = 'POINT'
        op = layout.operator("mesh.attribute_convert", text="Edge")
        op.domain = 'EDGE'
        op = layout.operator("mesh.attribute_convert", text="Face")
        op.domain = 'FACE'



# Registrazione
classes = (
    MESH_UL_attributes_custom,
    AttributesPanelProperties,
    MESH_OT_attribute_add,
    MESH_OT_attribute_remove_selected,
    MESH_OT_attribute_convert,
    MESH_OT_attribute_assign,
    MESH_OT_attribute_remove,
    MESH_OT_attribute_select,
    MESH_OT_attribute_deselect,
    MESH_OT_add_vertex_attribute,
    MESH_OT_add_edge_attribute,
    MESH_OT_add_face_attribute,
    MESH_MT_attribute_convert_menu,
)

def attributes_manager_register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.attributes_panel_props = bpy.props.PointerProperty(type=AttributesPanelProperties)

def attributes_manager_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.attributes_panel_props