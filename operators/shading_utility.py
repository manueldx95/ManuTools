import bpy


def get_global_location(node):
    parent = node.parent
    if parent:
        return node.location + parent.location
    return node.location



def get_main_input_socket(node):
    # gestisci i casi speciali
    if node.bl_idname == "ShaderNodeHueSaturation":
        return node.inputs["Color"]
    elif node.bl_idname == "ShaderNodeBrightContrast":
        return node.inputs["Color"]
    elif node.bl_idname == "ShaderNodeRGBCurve":
        return node.inputs["Color"]
    elif node.bl_idname == "ShaderNodeValToRGB":
        return node.inputs["Fac"]
    elif node.bl_idname == "ShaderNodeMapRange":
        return node.inputs["Value"]
    elif node.bl_idname == "ShaderNodeMath":
        return node.inputs[0]
    else:
        # fallback generico
        return node.inputs[0]



def get_node_width(node_type):
    """Restituisce la larghezza approssimativa di un nodo basata sul tipo"""
    width_map = {
        "ShaderNodeHueSaturation": 200,
        "ShaderNodeBrightContrast": 200,
        "ShaderNodeRGBCurve": 240,
        "ShaderNodeValToRGB": 240,
        "ShaderNodeMapRange": 220,
        "ShaderNodeMath": 160,
        "ShaderNodeTexImage": 240,
        # Aggiungi altri tipi se necessario
    }
    return width_map.get(node_type, 180)  # Default 180



def calculate_optimal_spacing(node_types, base_spacing=50):
    """Calcola lo spacing ottimale tra i nodi"""
    spacings = []
    for i, node_type in enumerate(node_types):
        if i == 0:
            spacings.append(0)
        else:
            prev_width = get_node_width(node_types[i-1])
            curr_spacing = prev_width + base_spacing
            spacings.append(spacings[i-1] + curr_spacing)
    return spacings



def check_node_overlap(node_tree, proposed_positions, node_types):
    """Controlla se le posizioni proposte si sovrappongono con nodi esistenti"""
    margin = 20
    
    for i, (pos_x, pos_y) in enumerate(proposed_positions):
        node_width = get_node_width(node_types[i])
        node_height = 100  # Altezza standard approssimativa
        
        # Controlla overlap con nodi esistenti
        for existing_node in node_tree.nodes:
            if existing_node.location.x < pos_x + node_width + margin and \
               existing_node.location.x + get_node_width(existing_node.bl_idname) + margin > pos_x and \
               existing_node.location.y < pos_y + node_height + margin and \
               existing_node.location.y + node_height + margin > pos_y:
                return True, i
    
    return False, -1



def find_clear_area(node_tree, start_x, start_y, total_width, direction="right"):
    """Trova un'area libera per posizionare i nodi"""
    search_height = 200
    step_y = 50
    
    for y_offset in range(0, search_height, step_y):
        for y_direction in [1, -1]:  # Prova sopra e sotto
            test_y = start_y + (y_offset * y_direction)
            
            # Controlla se quest'area è libera
            area_clear = True
            for node in node_tree.nodes:
                if (node.location.x < start_x + total_width + 50 and 
                    node.location.x + get_node_width(node.bl_idname) + 50 > start_x and
                    node.location.y < test_y + 100 and 
                    node.location.y + 100 > test_y - 100):
                    area_clear = False
                    break
            
            if area_clear:
                return start_x, test_y
    
    # Se non trova spazio, torna alla posizione originale con offset
    return start_x, start_y + 200



def get_output_chain_from_node(node_tree, start_node):
    """Ottiene la catena di nodi collegati in uscita dal nodo di partenza"""
    chain = []
    current_node = start_node
    visited = set()
    
    while current_node and current_node not in visited:
        visited.add(current_node)
        
        # Cerca il primo output collegato
        next_node = None
        if hasattr(current_node, 'outputs'):
            for output in current_node.outputs:
                if output.links:
                    # Prendi il primo link trovato
                    next_node = output.links[0].to_node
                    break
        
        if next_node:
            chain.append(next_node)
            current_node = next_node
        else:
            break
    
    return chain

def get_existing_node_types_in_chain(node_tree, image_node):
    """Ottiene i tipi di nodi già presenti nella catena dopo l'image texture"""
    chain = get_output_chain_from_node(node_tree, image_node)
    existing_types = set()
    
    for node in chain:
        existing_types.add(node.bl_idname)
    
    return existing_types, chain

def find_insertion_point(node_tree, image_node, node_types_to_add):
    """Trova il punto migliore per inserire i nuovi nodi nella catena esistente"""
    existing_types, chain = get_existing_node_types_in_chain(node_tree, image_node)
    
    # Definisci l'ordine preferito dei nodi (puoi personalizzarlo)
    preferred_order = [
        "ShaderNodeHueSaturation",
        "ShaderNodeBrightContrast", 
        "ShaderNodeRGBCurve",
        "ShaderNodeValToRGB",
        "ShaderNodeMapRange",
        "ShaderNodeMath"
    ]
    
    # Crea una mappa dei nodi esistenti con le loro posizioni nella catena
    existing_node_map = {}
    for i, node in enumerate(chain):
        existing_node_map[node.bl_idname] = (node, i)
    
    # Trova dove inserire i nuovi nodi
    insertion_groups = {}
    
    for node_type in node_types_to_add:
        if node_type in existing_types:
            continue  # Salta i nodi già esistenti
        
        # Trova la posizione ideale basata sull'ordine preferito
        preferred_index = preferred_order.index(node_type) if node_type in preferred_order else len(preferred_order)
        
        # Trova il punto di inserimento giusto
        insert_after_node = image_node
        insert_after_index = -1
        nodes_to_shift = []
        
        # Controlla se ci sono nodi esistenti che dovrebbero venire DOPO questo nuovo nodo
        for existing_type, (existing_node, chain_index) in existing_node_map.items():
            if existing_type in preferred_order:
                existing_preferred_index = preferred_order.index(existing_type)
                
                # Se il nodo esistente dovrebbe venire dopo il nuovo nodo
                if existing_preferred_index > preferred_index:
                    nodes_to_shift.append(existing_node)
                # Se il nodo esistente dovrebbe venire prima del nuovo nodo
                elif existing_preferred_index < preferred_index:
                    # Questo nodo può essere un punto di inserimento
                    if chain_index > insert_after_index:
                        insert_after_node = existing_node
                        insert_after_index = chain_index
        
        # Raggruppa per punto di inserimento
        if insert_after_node not in insertion_groups:
            insertion_groups[insert_after_node] = {
                'nodes_to_add': [],
                'nodes_to_shift': []
            }
        
        insertion_groups[insert_after_node]['nodes_to_add'].append(node_type)
        
        # Aggiungi i nodi da spostare (solo se non già inclusi)
        for node_to_shift in nodes_to_shift:
            if node_to_shift not in insertion_groups[insert_after_node]['nodes_to_shift']:
                insertion_groups[insert_after_node]['nodes_to_shift'].append(node_to_shift)
    
    return insertion_groups, chain

def filter_nodes_to_add(node_defs, existing_types):
    """Filtra i nodi da aggiungere escludendo quelli già presenti"""
    filtered_defs = []
    
    for node_type, label in node_defs:
        if node_type not in existing_types:
            filtered_defs.append((node_type, label))
    
    return filtered_defs

def get_connected_nodes_chain(node_tree, start_node, direction="right"):
    """Ottiene la catena di nodi collegati in una direzione specifica"""
    visited = set()
    chain = []
    
    def traverse_chain(node):
        if node in visited:
            return
        visited.add(node)
        chain.append(node)
        
        if direction == "right":
            # Segui i collegamenti in uscita
            for output in node.outputs:
                for link in output.links:
                    if link.to_node not in visited:
                        traverse_chain(link.to_node)
    
    traverse_chain(start_node)
    return chain[1:]  # Escludiamo il nodo di partenza

def shift_nodes_horizontally(nodes, offset_x):
    """Sposta una lista di nodi orizzontalmente"""
    for node in nodes:
        node.location.x += offset_x

def find_nodes_in_area(node_tree, start_x, start_y, width, height, exclude_nodes=None):
    """Trova tutti i nodi in un'area specifica"""
    if exclude_nodes is None:
        exclude_nodes = set()
    
    nodes_in_area = []
    for node in node_tree.nodes:
        if node in exclude_nodes:
            continue
        
        # Escludi i nodi che sono frame o che sono dentro frame
        if node.type == 'FRAME':
            continue
            
        node_width = get_node_width(node.bl_idname)
        node_height = 100  # Altezza standard
        
        # Controlla sovrapposizione
        if (node.location.x < start_x + width and 
            node.location.x + node_width > start_x and
            node.location.y < start_y + height and 
            node.location.y + node_height > start_y - height):
            nodes_in_area.append(node)
    
    return nodes_in_area

def create_space_by_shifting(node_tree, start_x, start_y, required_width, required_height, image_node):
    """Crea spazio spostando i nodi esistenti verso destra"""
    margin = 50
    total_width_needed = required_width + margin * 2
    
    # Crea set di nodi da escludere (image texture e tutti i nodi nel suo frame se presente)
    exclude_nodes = {image_node}
    
    # Se l'image texture è in un frame, escludi anche quello e tutti i nodi dentro
    if image_node.parent and image_node.parent.type == 'FRAME':
        frame = image_node.parent
        exclude_nodes.add(frame)
        # Aggiungi tutti i nodi figli del frame
        for node in node_tree.nodes:
            if node.parent == frame:
                exclude_nodes.add(node)
    
    # Trova tutti i nodi nell'area che vogliamo occupare
    conflicting_nodes = find_nodes_in_area(
        node_tree, 
        start_x - margin, 
        start_y - required_height//2, 
        total_width_needed, 
        required_height + margin * 2,
        exclude_nodes=exclude_nodes
    )
    
    if not conflicting_nodes:
        return start_x, start_y  # Nessun conflitto
    
    # Calcola quanto dobbiamo spostare
    shift_amount = (start_x + required_width + margin) - min(node.location.x for node in conflicting_nodes)
    
    if shift_amount <= 0:
        return start_x, start_y  # Non serve spostare
    
    # Raccogli tutti i nodi da spostare (incluse le catene collegate)
    all_nodes_to_shift = set(conflicting_nodes)
    
    # Per ogni nodo in conflitto, aggiungi la sua catena verso destra
    for node in conflicting_nodes:
        chain = get_connected_nodes_chain(node_tree, node, "right")
        all_nodes_to_shift.update(chain)
    
    # Rimuovi dall'insieme di spostamento i nodi che vogliamo escludere
    all_nodes_to_shift -= exclude_nodes
    
    # Sposta tutti i nodi
    shift_nodes_horizontally(all_nodes_to_shift, shift_amount)
    
    return start_x, start_y

def find_clear_area_with_shifting(node_tree, start_x, start_y, total_width, image_node, enable_shifting=True):
    """Versione migliorata che può spostare i nodi invece di cercare un'area libera"""
    
    if not enable_shifting:
        # Usa il comportamento originale
        return find_clear_area(node_tree, start_x, start_y, total_width)
    
    # Prima prova a creare spazio spostando i nodi
    required_height = 200  # Altezza approssimativa dell'area necessaria
    
    try:
        new_x, new_y = create_space_by_shifting(
            node_tree, start_x, start_y, total_width, required_height, image_node
        )
        return new_x, new_y
    except Exception as e:
        print(f"Errore nello spostamento nodi: {e}")
        # Fallback al comportamento originale
        return find_clear_area(node_tree, start_x, start_y, total_width)

def create_and_link_nodes_improved(node_tree, image_node, node_defs, settings=None):
    """Versione migliorata con spacing intelligente, spostamento nodi e gestione nodi esistenti"""
    
    # Usa le impostazioni dell'utente o default
    if settings is None:
        base_spacing = 50
        auto_position = True
        vertical_offset = 0
        enable_node_shifting = True
    else:
        base_spacing = settings.base_spacing
        auto_position = settings.auto_position
        vertical_offset = settings.vertical_offset
        enable_node_shifting = getattr(settings, 'enable_node_shifting', True)
    
    # Controlla quali nodi sono già presenti nella catena
    existing_types, existing_chain = get_existing_node_types_in_chain(node_tree, image_node)
    
    # Filtra i nodi da aggiungere
    filtered_node_defs = filter_nodes_to_add(node_defs, existing_types)
    
    if not filtered_node_defs:
        print("Tutti i nodi richiesti sono già presenti nella catena")
        return
    
    # Trova i punti di inserimento e i nodi da spostare
    insertion_groups, chain = find_insertion_point(node_tree, image_node, [nd[0] for nd in filtered_node_defs])
    
    # Raggruppa i nodi per tipo e label
    node_type_to_label = {node_type: label for node_type, label in filtered_node_defs}
    
    # Processa ogni gruppo di inserimento
    for insert_after_node, group_info in insertion_groups.items():
        nodes_to_add = group_info['nodes_to_add']
        nodes_to_shift = group_info['nodes_to_shift']
        
        if not nodes_to_add:
            continue
        
        # Crea la lista di definizioni per questo gruppo
        group_node_defs = [(node_type, node_type_to_label[node_type]) for node_type in nodes_to_add]
        
        # Trova il link da spezzare
        link_to_break = None
        target_node = None
        target_socket = None
        
        if hasattr(insert_after_node, 'outputs') and insert_after_node.outputs:
            for output in insert_after_node.outputs:
                if output.links:
                    link_to_break = output.links[0]  # Prendi il primo link
                    target_node = link_to_break.to_node
                    target_socket = link_to_break.to_socket
                    break
        
        if link_to_break:
            node_tree.links.remove(link_to_break)
        
        # Calcola posizioni per questo gruppo
        global_loc = get_global_location(insert_after_node)
        start_x = global_loc.x + get_node_width(insert_after_node.bl_idname) + base_spacing
        start_y = global_loc.y + vertical_offset
        
        # Estrai solo i tipi di nodo per questo gruppo
        node_types = [node_def[0] for node_def in group_node_defs]
        
        # Calcola spacing ottimale
        x_offsets = calculate_optimal_spacing(node_types, base_spacing)
        
        # Calcola larghezza totale necessaria
        total_width = x_offsets[-1] + get_node_width(node_types[-1]) if x_offsets else 0
        
        # Se ci sono nodi da spostare, calcoliamo lo spostamento necessario
        if nodes_to_shift and enable_node_shifting:
            # Trova la posizione x minima dei nodi da spostare
            min_x_to_shift = min(node.location.x for node in nodes_to_shift)
            required_space_end = start_x + total_width + base_spacing
            
            if min_x_to_shift < required_space_end:
                shift_amount = required_space_end - min_x_to_shift
                shift_existing_nodes_in_chain(node_tree, nodes_to_shift, shift_amount)
        
        # Trova area libera o sposta altri nodi se necessario
        if auto_position:
            final_x, final_y = find_clear_area_with_shifting(
                node_tree, start_x, start_y, total_width, image_node, enable_node_shifting
            )
        else:
            final_x, final_y = start_x, start_y
        
        # Crea e posiziona i nodi di questo gruppo
        prev_socket = insert_after_node.outputs[0] if insert_after_node.outputs else None
        last_created_node = insert_after_node
        
        for i, (node_type, label) in enumerate(group_node_defs):
            new_node = node_tree.nodes.new(type=node_type)
            new_node.label = label
            
            # Usa le posizioni calcolate
            node_x = final_x + x_offsets[i]
            new_node.location = (node_x, final_y)
            
            # Mantieni la gerarchia del frame se presente
            if insert_after_node.parent and insert_after_node.parent.type == 'FRAME':
                new_node.parent = insert_after_node.parent
            
            # Collega i nodi
            if hasattr(new_node, 'inputs') and len(new_node.inputs) > 0:
                main_input = get_main_input_socket(new_node)
                if main_input and prev_socket:
                    node_tree.links.new(prev_socket, main_input)
            
            # Prepara per il prossimo nodo
            if hasattr(new_node, 'outputs') and len(new_node.outputs) > 0:
                prev_socket = new_node.outputs[0]
                last_created_node = new_node
        
        # Ricollegata alla destinazione originale
        if target_node and target_socket and prev_socket:
            node_tree.links.new(prev_socket, target_socket)

def shift_existing_nodes_in_chain(node_tree, nodes_to_shift, shift_amount):
    """Sposta i nodi esistenti nella catena insieme alle loro connessioni a valle"""
    if not nodes_to_shift or shift_amount <= 0:
        return
    
    # Raccogli tutti i nodi da spostare includendo le catene collegate
    all_nodes_to_shift = set(nodes_to_shift)
    
    # Per ogni nodo da spostare, aggiungi anche tutti i nodi che vengono dopo di lui
    for node in nodes_to_shift:
        downstream_chain = get_connected_nodes_chain(node_tree, node, "right")
        all_nodes_to_shift.update(downstream_chain)
    
    # Sposta tutti i nodi
    shift_nodes_horizontally(all_nodes_to_shift, shift_amount)


class NodeSettings(bpy.types.PropertyGroup):
    use_hsl: bpy.props.BoolProperty(name="HSL", default=True)
    use_bc: bpy.props.BoolProperty(name="Bright/Contrast", default=True)
    use_curves: bpy.props.BoolProperty(name="RGB Curves", default=True)

    use_ramp: bpy.props.BoolProperty(name="ColorRamp", default=True)
    use_maprange: bpy.props.BoolProperty(name="Map Range", default=True)
    use_math: bpy.props.BoolProperty(name="Math", default=True)
    
    # Preferenze spacing
    base_spacing: bpy.props.IntProperty(
        name="Node Spacing", 
        default=50, 
        min=20, 
        max=200,
        description="Spazio base tra i nodi"
    )
    
    auto_position: bpy.props.BoolProperty(
        name="Auto Position", 
        default=True,
        description="Trova automaticamente posizione libera per evitare sovrapposizioni"
    )
    
    vertical_offset: bpy.props.IntProperty(
        name="Vertical Offset",
        default=0,
        min=-500,
        max=500,
        description="Offset verticale per i nuovi nodi"
    )

    enable_node_shifting: bpy.props.BoolProperty(
        name="Enable Node Shifting", 
        default=True,
        description="Sposta automaticamente i nodi esistenti per fare spazio invece di cercare un'area libera"
    )



class NODE_OT_AddColorAdjust(bpy.types.Operator):
    bl_idname = "node.add_color_adjust"
    bl_label = "Adjust Color"

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        image_node = get_active_image_texture_node(context)
        if not image_node:
            self.report({'WARNING'}, "Seleziona un nodo Image Texture")
            return {'CANCELLED'}

        s = context.scene.node_settings
        nodes_to_add = []
        if s.use_hsl:
            nodes_to_add.append(("ShaderNodeHueSaturation", "HSL"))
        if s.use_bc:
            nodes_to_add.append(("ShaderNodeBrightContrast", "Bright/Contrast"))
        if s.use_curves:
            nodes_to_add.append(("ShaderNodeRGBCurve", "RGB Curves"))

        if nodes_to_add:
            create_and_link_nodes_improved(node_tree, image_node, nodes_to_add, context.scene.node_settings)
        else:
            self.report({'INFO'}, "Nessun nodo selezionato")
        return {'FINISHED'}



class NODE_OT_AddValueAdjust(bpy.types.Operator):
    bl_idname = "node.add_value_adjust"
    bl_label = "Adjust Value"

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        image_node = get_active_image_texture_node(context)
        if not image_node:
            self.report({'WARNING'}, "Seleziona un nodo Image Texture")
            return {'CANCELLED'}

        s = context.scene.node_settings
        nodes_to_add = []
        if s.use_ramp:
            nodes_to_add.append(("ShaderNodeValToRGB", "ColorRamp"))
        if s.use_maprange:
            nodes_to_add.append(("ShaderNodeMapRange", "Map Range"))
        if s.use_math:
            nodes_to_add.append(("ShaderNodeMath", "Math"))

        if nodes_to_add:
            create_and_link_nodes_improved(node_tree, image_node, nodes_to_add, context.scene.node_settings)
        else:
            self.report({'INFO'}, "Nessun nodo selezionato")
        return {'FINISHED'}



def get_active_image_texture_node(context):
    try:
        node_tree = context.space_data.edit_tree
        if not node_tree:
            return None
        for node in node_tree.nodes:
            if node.select and node.type == 'TEX_IMAGE':
                return node
    except AttributeError:
        return None
    return None



classes = (
    NodeSettings,
    NODE_OT_AddColorAdjust,
    NODE_OT_AddValueAdjust,
)



def shading_utility_register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.node_settings = bpy.props.PointerProperty(type=NodeSettings)

def shading_utility_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.node_settings