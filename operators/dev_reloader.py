import bpy
import sys
import importlib
import gc
import time

class ReloadAddonProperties(bpy.types.PropertyGroup):
    addon_name: bpy.props.StringProperty(
        name="Addon Folder Name",
        description="Name of the addon folder to reload",
        default=""
    )

class ReloadAddonOperator(bpy.types.Operator):
    """Ricarica forzatamente un addon in modo sicuro, senza far crashare Blender."""
    bl_idname = "manutools.reload_addon"
    bl_label = "Reload Addon"

    def execute(self, context):
        addon_name = context.scene.reload_addon_props.addon_name.strip()
        if not addon_name:
            self.report({'WARNING'}, "Inserisci il nome della cartella dell'addon.")
            return {'CANCELLED'}

        try:
            # Step 1: Verifica che l'addon esista nei moduli
            if addon_name not in sys.modules and not any(name.startswith(addon_name + ".") for name in sys.modules):
                self.report({'WARNING'}, f"Addon '{addon_name}' non trovato nei moduli caricati.")
                return {'CANCELLED'}
            
            # Step 2: Salva reference alle proprietà che potrebbero essere rimosse
            saved_props = self.save_scene_properties(context, addon_name)
            
            # Step 3: Cleanup handlers e timer prima di tutto
            self.cleanup_handlers_and_timers(addon_name)
            
            # Step 4: Forza garbage collection
            gc.collect()
            
            # Step 5: Trova tutti i moduli dell'addon
            modules_to_remove = [name for name in sys.modules if name == addon_name or name.startswith(addon_name + ".")]
            
            # Step 6: Ordina i moduli per depth (prima i sottomoduli, poi il principale)
            modules_to_remove.sort(key=lambda x: x.count('.'), reverse=True)
            
            print(f"[DEV RELOADER] Moduli da rimuovere: {modules_to_remove}")
            
            # Step 7: Sicurezza extra - rimuovi proprietà Scene che potrebbero causare crash
            self.cleanup_scene_properties(context, addon_name)
            
            # Step 8: Unregister solo il modulo principale
            unregister_errors = []
            main_module = sys.modules.get(addon_name)
            if main_module and hasattr(main_module, "unregister"):
                try:
                    print(f"[DEV RELOADER] Unregistering {addon_name}")
                    main_module.unregister()
                except Exception as e:
                    unregister_errors.append(f"{addon_name}: {str(e)}")
                    print(f"[DEV RELOADER] Warning: errore durante unregister di {addon_name}: {e}")
            
            # Step 9: Pausa più lunga per stabilizzare Blender
            time.sleep(0.2)
            
            # Step 10: Rimuovi moduli da sys.modules in ordine sicuro
            for mod_name in modules_to_remove:
                if mod_name in sys.modules:
                    try:
                        # Pulisci eventuali reference prima di rimuovere
                        mod = sys.modules[mod_name]
                        if hasattr(mod, '__dict__'):
                            mod.__dict__.clear()
                        del sys.modules[mod_name]
                        print(f"[DEV RELOADER] Rimosso {mod_name} da sys.modules")
                    except Exception as e:
                        print(f"[DEV RELOADER] Errore rimozione {mod_name}: {e}")
            
            # Step 11: Forza garbage collection aggressivo
            for _ in range(3):
                gc.collect()
            
            # Step 12: Pausa prima del reload
            time.sleep(0.2)
            
            # Step 13: Reimporta e registra
            print(f"[DEV RELOADER] Reimportando {addon_name}")
            new_mod = importlib.import_module(addon_name)
            
            if hasattr(new_mod, "register"):
                new_mod.register()
                print(f"[DEV RELOADER] Register chiamato per {addon_name}")
            else:
                self.report({'WARNING'}, f"Addon '{addon_name}' non ha funzione register()")
            
            # Step 14: Ripristina proprietà salvate se necessario
            self.restore_scene_properties(context, saved_props)
            
            # Step 15: Forza aggiornamento UI
            self.force_ui_update(context)
            
            # Report finale
            if unregister_errors:
                self.report({'WARNING'}, f"Addon ricaricato con {len(unregister_errors)} warning durante unregister")
            else:
                self.report({'INFO'}, f"Addon '{addon_name}' ricaricato correttamente.")
            
        except ImportError as e:
            print(f"[DEV RELOADER] Errore di import: {e}")
            self.report({'ERROR'}, f"Errore di import durante il reload: {e}")
            return {'CANCELLED'}
        except Exception as e:
            print(f"[DEV RELOADER] Errore completo: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Errore durante il reload: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}
    
    def cleanup_handlers_and_timers(self, addon_name):
        """Pulisce handler e timer che potrebbero causare problemi"""
        try:
            # Rimuovi timer attivi (approccio più sicuro)
            if hasattr(bpy.app, 'timers'):
                # Verifica che bpy.app.timers sia iterabile
                try:
                    timers_list = list(bpy.app.timers)
                    removed_timers = 0
                    for timer in timers_list:
                        try:
                            # Prova a identificare timer che potrebbero appartenere all'addon
                            timer_name = getattr(timer, '__name__', str(timer))
                            if addon_name.lower() in timer_name.lower():
                                bpy.app.timers.remove(timer)
                                removed_timers += 1
                                print(f"[DEV RELOADER] Rimosso timer dell'addon: {timer}")
                        except Exception as timer_error:
                            print(f"[DEV RELOADER] Errore rimozione timer: {timer_error}")
                    
                    if removed_timers > 0:
                        print(f"[DEV RELOADER] Rimossi {removed_timers} timer")
                        
                except TypeError:
                    print("[DEV RELOADER] bpy.app.timers non iterabile, skip cleanup timer")
            
            # Pulisci handler comuni che potrebbero dare problemi
            handlers_to_check = [
                'frame_change_pre',
                'frame_change_post', 
                'render_pre',
                'render_post',
                'load_post',
                'save_pre',
                'save_post',
                'depsgraph_update_pre',
                'depsgraph_update_post'
            ]
            
            for handler_name in handlers_to_check:
                try:
                    if hasattr(bpy.app.handlers, handler_name):
                        handler_list = getattr(bpy.app.handlers, handler_name)
                        if hasattr(handler_list, '__len__') and len(handler_list) > 0:
                            print(f"[DEV RELOADER] Handler {handler_name} ha {len(handler_list)} elementi")
                            # In futuro si potrebbe implementare una logica più sofisticata
                            # per identificare e rimuovere solo gli handler dell'addon specifico
                except Exception as handler_error:
                    print(f"[DEV RELOADER] Errore controllo handler {handler_name}: {handler_error}")
                    
        except Exception as e:
            print(f"[DEV RELOADER] Warning durante cleanup handlers: {e}")
    
    def force_ui_update(self, context):
        """Forza l'aggiornamento dell'interfaccia utente"""
        try:
            # Aggiorna tutte le aree
            for area in context.screen.areas:
                area.tag_redraw()
            
            # Forza aggiornamento delle proprietà
            if hasattr(context, 'object') and context.object:
                context.object.update_tag()
            
            # Aggiorna la scena
            context.scene.update_tag()
            
            print("[DEV RELOADER] UI aggiornata")
            
        except Exception as e:
            print(f"[DEV RELOADER] Warning durante aggiornamento UI: {e}")
    
    def save_scene_properties(self, context, addon_name):
        """Salva le proprietà Scene che potrebbero essere rimosse"""
        saved_props = {}
        try:
            scene = context.scene
            # Salva proprietà comuni che potrebbero essere dell'addon
            for attr_name in dir(scene):
                if (attr_name.startswith(addon_name.lower()) or 
                    addon_name.lower() in attr_name.lower() or
                    attr_name.endswith('_props')):
                    try:
                        attr_value = getattr(scene, attr_name)
                        saved_props[attr_name] = attr_value
                        print(f"[DEV RELOADER] Salvata proprietà: {attr_name}")
                    except:
                        pass
        except Exception as e:
            print(f"[DEV RELOADER] Errore salvataggio proprietà: {e}")
        return saved_props
    
    def cleanup_scene_properties(self, context, addon_name):
        """Rimuove proprietà Scene che potrebbero causare crash"""
        try:
            scene = context.scene
            props_to_remove = []
            
            # Trova proprietà che potrebbero appartenere all'addon
            for attr_name in dir(scene):
                if (attr_name.startswith(addon_name.lower()) or 
                    addon_name.lower() in attr_name.lower()):
                    # Non rimuovere reload_addon_props che ci serve per il reload
                    if attr_name != 'reload_addon_props':
                        props_to_remove.append(attr_name)
            
            # Rimuovi le proprietà trovate
            for prop_name in props_to_remove:
                try:
                    if hasattr(bpy.types.Scene, prop_name):
                        delattr(bpy.types.Scene, prop_name)
                        print(f"[DEV RELOADER] Rimossa proprietà Scene: {prop_name}")
                except Exception as e:
                    print(f"[DEV RELOADER] Errore rimozione proprietà {prop_name}: {e}")
                    
        except Exception as e:
            print(f"[DEV RELOADER] Errore cleanup proprietà: {e}")
    
    def restore_scene_properties(self, context, saved_props):
        """Ripristina proprietà Scene se necessario"""
        try:
            # Per ora non ripristiniamo, lasciamo che l'addon le ricrei
            # In futuro si potrebbe implementare un ripristino intelligente
            if saved_props:
                print(f"[DEV RELOADER] Proprietà salvate disponibili per ripristino: {list(saved_props.keys())}")
        except Exception as e:
            print(f"[DEV RELOADER] Errore ripristino proprietà: {e}")

# Operatore più semplice che combina set + reload
class MANUTOOLS_OT_SetAndReloadAddon(bpy.types.Operator):
    """Imposta il nome dell'addon e lo ricarica immediatamente"""
    bl_idname = "manutools.set_and_reload_addon"
    bl_label = "Set and Reload Addon"
    
    addon_name: bpy.props.StringProperty(
        name="Addon Name",
        description="Nome dell'addon da ricaricare"
    )
    
    def execute(self, context):
        if not hasattr(context.scene, 'reload_addon_props'):
            self.report({'ERROR'}, "ReloadAddonProperties non registrata")
            return {'CANCELLED'}
            
        if not self.addon_name:
            self.report({'ERROR'}, "Nome addon non specificato")
            return {'CANCELLED'}
            
        # Imposta il nome nel campo
        context.scene.reload_addon_props.addon_name = self.addon_name
        
        # Chiama direttamente l'operatore di reload
        return bpy.ops.manutools.reload_addon()

# Operatore originale migliorato
class MANUTOOLS_OT_SetAddonName(bpy.types.Operator):
    """Imposta il nome dell'addon nel campo di input"""
    bl_idname = "manutools.set_addon_name"
    bl_label = "Set Addon Name"
    
    addon_name: bpy.props.StringProperty(
        name="Addon Name",
        description="Nome dell'addon",
        default=""
    )
    
    def execute(self, context):
        if not hasattr(context.scene, 'reload_addon_props'):
            self.report({'ERROR'}, "ReloadAddonProperties non registrata")
            return {'CANCELLED'}
            
        # Controlla che addon_name non sia None o vuoto
        addon_name = getattr(self, 'addon_name', '') or ''
        
        if not addon_name:
            self.report({'WARNING'}, "Nome addon vuoto")
            return {'CANCELLED'}
            
        context.scene.reload_addon_props.addon_name = addon_name
        self.report({'INFO'}, f"Impostato addon: {addon_name}")
        return {'FINISHED'}

# Nuovo operatore per listare addon attivi
class MANUTOOLS_OT_ListActiveAddons(bpy.types.Operator):
    """Lista tutti gli addon attualmente caricati"""
    bl_idname = "manutools.list_active_addons"
    bl_label = "List Active Addons"
    
    def execute(self, context):
        try:
            import addon_utils
            active_addons = []
            
            for mod in addon_utils.modules():
                if mod.__name__ not in ['bl_ui', 'bl_operators', 'cycles', 'bpy', 'mathutils'] and not mod.__name__.startswith('bl_'):
                    active_addons.append(mod.__name__)
            
            if active_addons:
                print(f"[DEV RELOADER] Addon attivi trovati: {active_addons}")
                self.report({'INFO'}, f"Trovati {len(active_addons)} addon attivi. Vedi console per dettagli.")
            else:
                self.report({'INFO'}, "Nessun addon utente trovato")
                
        except Exception as e:
            self.report({'ERROR'}, f"Errore nel listing addon: {e}")
            
        return {'FINISHED'}

# Nuovo operatore per reload ultra-sicuro
class MANUTOOLS_OT_SafeReloadAddon(bpy.types.Operator):
    """Reload ultra-sicuro che disabilita temporaneamente l'addon"""
    bl_idname = "manutools.safe_reload_addon"
    bl_label = "Safe Reload Addon"
    
    def execute(self, context):
        if not hasattr(context.scene, 'reload_addon_props'):
            self.report({'ERROR'}, "ReloadAddonProperties non registrata")
            return {'CANCELLED'}
            
        addon_name = context.scene.reload_addon_props.addon_name.strip()
        if not addon_name:
            self.report({'WARNING'}, "Inserisci il nome della cartella dell'addon.")
            return {'CANCELLED'}
        
        try:
            import addon_utils
            
            # Step 1: Trova l'addon e disabilitalo se abilitato
            addon_module = None
            for mod in addon_utils.modules():
                if mod.__name__ == addon_name:
                    addon_module = mod
                    break
            
            was_enabled = False
            if addon_module:
                was_enabled = addon_utils.check(addon_name)[1]
                if was_enabled:
                    print(f"[SAFE RELOADER] Disabilitando addon {addon_name}")
                    addon_utils.disable(addon_name)
                    time.sleep(0.3)  # Pausa più lunga per la disabilitazione
            
            # Step 2: Pulisci tutto
            gc.collect()
            
            # Step 3: Riabilita se era abilitato
            if was_enabled and addon_module:
                print(f"[SAFE RELOADER] Riabilitando addon {addon_name}")
                addon_utils.enable(addon_name)
                time.sleep(0.2)
            
            # Step 4: Aggiorna UI
            for area in context.screen.areas:
                area.tag_redraw()
            
            self.report({'INFO'}, f"Safe reload di '{addon_name}' completato")
            
        except Exception as e:
            print(f"[SAFE RELOADER] Errore: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Errore durante safe reload: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# Nuovo operatore per reload ultra-sicuro con nome
class MANUTOOLS_OT_SafeSetAndReloadAddon(bpy.types.Operator):
    """Safe reload con set del nome"""
    bl_idname = "manutools.safe_set_and_reload_addon"
    bl_label = "Safe Set and Reload Addon"
    
    addon_name: bpy.props.StringProperty(
        name="Addon Name",
        description="Nome dell'addon da ricaricare in modo sicuro"
    )
    
    def execute(self, context):
        if not hasattr(context.scene, 'reload_addon_props'):
            self.report({'ERROR'}, "ReloadAddonProperties non registrata")
            return {'CANCELLED'}
            
        if not self.addon_name:
            self.report({'ERROR'}, "Nome addon non specificato")
            return {'CANCELLED'}
            
        # Imposta il nome nel campo
        context.scene.reload_addon_props.addon_name = self.addon_name
        
        # Chiama l'operatore di safe reload
        return bpy.ops.manutools.safe_reload_addon()

def dev_reloader_register():
    bpy.utils.register_class(ReloadAddonProperties)
    bpy.utils.register_class(ReloadAddonOperator)
    bpy.utils.register_class(MANUTOOLS_OT_SetAddonName)
    bpy.utils.register_class(MANUTOOLS_OT_SetAndReloadAddon)
    bpy.utils.register_class(MANUTOOLS_OT_ListActiveAddons)
    bpy.utils.register_class(MANUTOOLS_OT_SafeReloadAddon)  # NUOVO
    bpy.utils.register_class(MANUTOOLS_OT_SafeSetAndReloadAddon)  # NUOVO
    bpy.types.Scene.reload_addon_props = bpy.props.PointerProperty(type=ReloadAddonProperties)

def dev_reloader_unregister():
    bpy.utils.unregister_class(MANUTOOLS_OT_SafeSetAndReloadAddon)  # NUOVO
    bpy.utils.unregister_class(MANUTOOLS_OT_SafeReloadAddon)  # NUOVO
    bpy.utils.unregister_class(MANUTOOLS_OT_ListActiveAddons)
    bpy.utils.unregister_class(MANUTOOLS_OT_SetAndReloadAddon)
    bpy.utils.unregister_class(MANUTOOLS_OT_SetAddonName)
    bpy.utils.unregister_class(ReloadAddonOperator)
    bpy.utils.unregister_class(ReloadAddonProperties)
    if hasattr(bpy.types.Scene, 'reload_addon_props'):
        del bpy.types.Scene.reload_addon_props