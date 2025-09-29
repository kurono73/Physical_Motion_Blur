# Physical_Motion_Blur


import bpy
import math
from bpy.props import EnumProperty, StringProperty, FloatProperty, BoolProperty
from bpy.app.handlers import persistent

# --- Utility Functions ---
def get_frame_rate(scene):
    """Calculate the final frame rate from fps and fps_base."""
    fps = scene.render.fps
    base = scene.render.fps_base if scene.render.fps_base != 0 else 1.0
    return fps / base

def parse_shutter_speed_string(s: str) -> float:
    """Parse shutter speed input like '1/125' or '0.008' into seconds."""
    s = s.strip().lower().replace("s", "")
    if "/" in s:
        try:
            num, den = s.split("/")
            return float(num) / float(den)
        except (ValueError, ZeroDivisionError):
            raise ValueError("Invalid fraction format")
    return float(s)

# --- Core Logic & Callbacks ---
def apply_shutter(scene):
    """Compute and apply motion blur shutter value."""
    if not scene or not scene.shutter_control_is_active or not scene.render.use_motion_blur:
        return
        
    try:
        if scene.shutter_control_mode == "SPEED":
            shutter_seconds = parse_shutter_speed_string(scene.shutter_control_speed)
            shutter_fraction = shutter_seconds * get_frame_rate(scene)
        else:  # ANGLE mode
            shutter_fraction = scene.shutter_control_angle / 360.0
    except (ValueError, TypeError):
        return
    scene.render.motion_blur_shutter = max(0.0, shutter_fraction)

@persistent
def on_depsgraph_update(scene, depsgraph):
    """Handler to react to scene changes like FPS updates."""
    apply_shutter(scene)

def update_shutter(self, context):
    """Callback for when the addon's own properties are changed."""
    if context.scene:
        apply_shutter(context.scene)

# --- Base Panel for UI ---
class SHUTTER_CONTROL_PT_base(bpy.types.Panel):
    bl_label = "" 
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED', 'HEADER_LAYOUT_EXPAND'}
    
    @classmethod
    def poll(cls, context):
        # --- CHANGE: Always return True to ensure the panel header is always visible. ---
        return True

    def draw_header(self, context):
        scene = context.scene
        self.layout.prop(scene, "shutter_control_is_active", text="Camera Shutter Control")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render
        
        # --- CHANGE: Gray out the UI if the master switch OR global motion blur is off. ---
        layout.active = scene.shutter_control_is_active and rd.use_motion_blur
        layout.use_property_split = True
        
        main_col = layout.column(align=True)
        
        row = main_col.row()
        row.prop(scene, "shutter_control_mode", expand=True)
        
        if scene.shutter_control_mode == "SPEED":
            main_col.prop(scene, "shutter_control_speed")
        else: # ANGLE
            main_col.prop(scene, "shutter_control_angle")
        
        main_col.separator()
        
        col = main_col.column(heading="Frame Rate")
        
        format_panel = getattr(bpy.types, "RENDER_PT_format", None)
        preset_menu = getattr(bpy.types, "RENDER_MT_framerate_presets", None)
        label_text = f"{get_frame_rate(scene):.2f} FPS"
        show_custom_ui = False
        if format_panel and preset_menu and hasattr(format_panel, "_draw_framerate_label"):
            try:
                args = (rd.fps, rd.fps_base, preset_menu.bl_label)
                label_text, show_custom_ui = format_panel._draw_framerate_label(*args)
            except Exception:
                pass
        
        col.menu("RENDER_MT_framerate_presets", text=label_text)
        
        if show_custom_ui:
            sub_col = col.column(align=True)
            sub_col.prop(rd, "fps")
            sub_col.prop(rd, "fps_base", text="Base")

# --- Registration ---
panel_classes = []

def register():
    """Register all parts of the addon."""
    bpy.types.Scene.shutter_control_is_active = BoolProperty(name="Enable Camera Shutter Control",description="Globally enable or disable this addon's automatic calculations",default=True,update=update_shutter)
    bpy.types.Scene.shutter_control_mode = EnumProperty(name="Mode",description="Select how to define shutter duration",items=[("SPEED", "Speed", "Use seconds like 1/48s"),("ANGLE", "Angle", "Use degrees like 180°")],default="ANGLE",update=update_shutter,options=set())
    bpy.types.Scene.shutter_control_speed = StringProperty(name="Shutter Speed (s)",description="Enter an absolute shutter time, e.g., '1/48' for video or '2s' for a still photo",default="1/48",update=update_shutter)
    bpy.types.Scene.shutter_control_angle = FloatProperty(name="Shutter Angle (°)",description="Shutter angle in degrees (0–360)",min=0.0,max=360.0,default=180.0,update=update_shutter,options=set())

    if on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)

    parent_panels = {
        'CYCLES': 'CYCLES_RENDER_PT_motion_blur',
        'BLENDER_EEVEE': 'RENDER_PT_eevee_motion_blur',
        'BLENDER_EEVEE_NEXT': 'RENDER_PT_eevee_next_motion_blur',
    }

    for engine_id, parent_id in parent_panels.items():
        if getattr(bpy.types, parent_id, None) is None:
            continue
        class_name = f"SHUTTER_CONTROL_PT_{engine_id}"
        new_panel = type(
            class_name,
            (SHUTTER_CONTROL_PT_base,),
            {"bl_idname": f"RENDER_PT_{class_name}","bl_parent_id": parent_id,"COMPAT_ENGINES": {engine_id},}
        )
        bpy.utils.register_class(new_panel)
        panel_classes.append(new_panel)

def unregister():
    """Unregister all parts of the addon."""
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
        
    for cls in panel_classes:
        bpy.utils.unregister_class(cls)
    panel_classes.clear()
    
    props = ("shutter_control_mode", "shutter_control_speed", "shutter_control_angle", "shutter_control_is_active")
    for p in props:
        if hasattr(bpy.types.Scene, p):
            delattr(bpy.types.Scene, p)