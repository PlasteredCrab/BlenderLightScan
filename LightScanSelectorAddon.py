bl_info = {
    "name": "Light Scan Selector",
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy
import math
import mathutils

class LightScanOperator(bpy.types.Operator):
    """Perform light scan to select objects hit by lights in the selected collection"""
    bl_idname = "object.light_scan"
    bl_label = "Perform Light Scan"
    
    # Operator properties for latitude and longitude ray settings
    rays_per_latitude: bpy.props.IntProperty(
        name="Rays Per Latitude",
        default=200,
        min=1,
        description="Number of raycasts in the latitude direction"
    )
    
    rays_per_longitude: bpy.props.IntProperty(
        name="Rays Per Longitude",
        default=100,
        min=1,
        description="Number of raycasts in the longitude direction"
    )

    def raycast_from_light(self, light_obj):
        context = bpy.context
        scene = context.scene
        depsgraph = context.evaluated_depsgraph_get()

        light_pos = light_obj.location

        # Create a set to store hit objects
        hit_objects = set()

        # Cast rays in a spherical pattern around the light
        for i in range(self.rays_per_latitude):
            lat_angle = math.pi * i / self.rays_per_latitude  # Sweep latitude angle (0 to pi)
            for j in range(self.rays_per_longitude):
                long_angle = 2 * math.pi * j / self.rays_per_longitude  # Sweep longitude angle (0 to 2*pi)

                # Convert spherical coordinates to a direction vector
                direction = mathutils.Vector((
                    math.sin(lat_angle) * math.cos(long_angle),
                    math.sin(lat_angle) * math.sin(long_angle),
                    math.cos(lat_angle)
                ))

                # Cast ray from the light in this direction
                result, location, normal, index, obj, matrix = scene.ray_cast(depsgraph, light_pos, direction)

                # If the ray hits something, add it to the hit_objects set
                if result and obj:
                    hit_objects.add(obj)

        return hit_objects
    
    def execute(self, context):
        collection = context.collection
        
        if not collection:
            self.report({'ERROR'}, "No collection selected!")
            return {'CANCELLED'}
        
        # Clear any existing selection
        bpy.ops.object.select_all(action='DESELECT')
        
        hit_objects = set()

        # Iterate through all objects in the selected collection
        for obj in collection.objects:
            # Check if the object is a light
            if obj.type == 'LIGHT':
                # Perform raycasting from the light
                hit_objects.update(self.raycast_from_light(obj))
        
        # Select all hit objects
        for obj in hit_objects:
            obj.select_set(True)
        
        # Deselect all lights in the collection
        for obj in collection.objects:
            if obj.type == 'LIGHT':
                obj.select_set(False)
        
        return {'FINISHED'}

class LightScanPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Light Scan"
    bl_idname = "OBJECT_PT_light_scan"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Light Scan'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "rays_per_latitude")
        layout.prop(scene, "rays_per_longitude")
        
        row = layout.row()
        row.operator("object.light_scan")

def register():
    # Register custom properties in the scene for user input
    bpy.types.Scene.rays_per_latitude = bpy.props.IntProperty(
        name="Rays Per Latitude",
        default=200,
        min=1,
        description="Number of raycasts in the latitude direction"
    )
    
    bpy.types.Scene.rays_per_longitude = bpy.props.IntProperty(
        name="Rays Per Longitude",
        default=100,
        min=1,
        description="Number of raycasts in the longitude direction"
    )

    bpy.utils.register_class(LightScanOperator)
    bpy.utils.register_class(LightScanPanel)

def unregister():
    # Unregister custom properties
    del bpy.types.Scene.rays_per_latitude
    del bpy.types.Scene.rays_per_longitude

    bpy.utils.unregister_class(LightScanOperator)
    bpy.utils.unregister_class(LightScanPanel)

if __name__ == "__main__":
    register()
