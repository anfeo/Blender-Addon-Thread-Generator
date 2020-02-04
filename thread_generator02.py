bl_info = {
    "name": "Thread Generator",
    "author": "Alfonso Annarumma, http://otvinta.com/",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Add Thread",
    "description": "Adds a new Thread Object",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator
from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        IntProperty,
        CollectionProperty,
        BoolVectorProperty,
        PointerProperty,
        )
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import *
import bmesh


def RemoveDoubles (mesh,distance):
    
    bm = bmesh.new()   
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
    bm.to_mesh(mesh)
    mesh.update()
    bm.clear()

    bm.free()
    return mesh





def createMeshFromData(self, name, origin, verts, edges, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = False
    # Link object to scene and make active
    #bpy.context.collection.objects.link(ob)
    #ob.select_set(True)
    # Create mesh from given verts, faces.
    me.from_pydata(verts, edges, faces)
    # Update mesh with new data
    me.update()
    return me




    # Code
def thread_generator(VerticesPerLoop,Loops, R, r, h1, h2,h3,h4, falloffRate):
    H = h1 + h2 + h3 + h4

    #build array of profile points
    ProfilePoints = []
    ProfilePoints.append( [r, 0, 0] )
    ProfilePoints.append( [R, 0, h1] )
    if h2 > 0:
        ProfilePoints.append( [R, 0, h1 + h2] )
    ProfilePoints.append( [r, 0, h1 + h2 + h3] )
    if h4 > 0:
        ProfilePoints.append( [r, 0, h1 + h2 + h3 + h4] )

    N = len(ProfilePoints)
    verts = [[0, 0, 0] for _ in range(N * (VerticesPerLoop + 1)  * Loops)]
    faces = [[0, 0, 0, 0] for _ in range(( N - 1) * VerticesPerLoop * Loops) ]

    # go around a cirle. for each point in ProfilePoints array, create a vertex
    angle = 0
    for i in range(VerticesPerLoop * Loops + 1):
        for j in range(N):
            angle = i * 2 * pi / VerticesPerLoop
            # falloff applies to outer rings only
            u = i / (VerticesPerLoop * Loops)
            radius = r + (R - r) * (1 - 6*(pow(2 * u - 1, falloffRate * 4)/2 - pow(2 * u - 1, falloffRate * 6)/3)) if ProfilePoints[j][0] == R else r

            x = radius * cos(angle)
            y = radius * sin(angle)
            z = ProfilePoints[j][2] + i / VerticesPerLoop * H

            verts[N*i + j][0] = x
            verts[N*i + j][1] = y
            verts[N*i + j][2] = z
    # now build face array
    for i in range(VerticesPerLoop * Loops):
        for j in range(N - 1):
            faces[(N - 1) * i + j][0] = N * i + j
            faces[(N - 1) * i + j][1] = N * i + 1 + j
            faces[(N - 1) * i + j][2] = N * (i + 1) + 1 + j
            faces[(N - 1) * i + j][3] =  N * (i + 1) + j
    
    return verts, faces






class OBJECT_OT_add_thread(Operator, AddObjectHelper):
    """Create a new Thread Mesh"""
    bl_idname = "mesh.add_thread"
    bl_label = "Add Thread Mesh "
    bl_options = {'REGISTER', 'UNDO'}
    
    
        # Parameters
    VerticesPerLoop : IntProperty(name="Vertices Per Loop",
        description="Number of Vertices for Loop",
        min=1, max=10000,
        default=32,)
    Loops : IntProperty(name="Loop",
        description="Number of Loops",
        min=1, max=10000,
        default=2,)
    R : FloatProperty(name="Outer Radius",
        description="Outer Radius",
        min=0.01, max=100000.0,
        default=1.2, subtype='DISTANCE', unit='LENGTH') #radius
    r : FloatProperty(name="Inner Radius",
        description="Inner Radius",
        min=0.01, max=100000.0,
        default=1.0, subtype='DISTANCE', unit='LENGTH') # Inner radius
    # thread profile (h1, h2, h3, h4 of the 4 points defining the profile)
    h1 : FloatProperty(name="h1",
        description="thread profile (h1, h2, h3, h4 of the 4 points defining the profile)",
        min=0.01, max=100000.0,
        default=0.2, subtype='DISTANCE', unit='LENGTH')
    h2 : FloatProperty(name="h2",
        description="thread profile (h1, h2, h3, h4 of the 4 points defining the profile)",
        min=0.01, max=100000.0,
        default=0.05, subtype='DISTANCE', unit='LENGTH')
    h3 : FloatProperty(name="h3",
        description="thread profile (h1, h2, h3, h4 of the 4 points defining the profile)",
        min=0.01, max=100000.0,
        default=0.2, subtype='DISTANCE', unit='LENGTH')
    h4 : FloatProperty(name="h4",
        description="thread profile (h1, h2, h3, h4 of the 4 points defining the profile)",
        min=0.01, max=100000.0,
        default=0.05, subtype='DISTANCE', unit='LENGTH')
    falloffRate : IntProperty(name="Fallof Rate",
        description="Fallof Rate",
        min=1, max=100000,
        default=5,)
    removedouble : BoolProperty(name="Remove Double",
        description="Remove Double Vertex By Distance",
        default=True)
    distance : FloatProperty(name="Distance",
        description="Distance from Vertex to join",
        min=0.00001, max=100000.0,
        default = 0.001)
    

    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.prop(self, "VerticesPerLoop")
        col.prop(self, "Loops")
        col.prop(self, "R")
        col.prop(self, "r")
        col.prop(self, "h1")
        col.prop(self, "h2")
        col.prop(self, "h3")
        col.prop(self, "h4")
        col.prop(self, "falloffRate")
        col.prop(self, "removedouble")
        if self.removedouble:
            col.prop(self, "distance")
        
        
        
        
    def execute(self, context):

        verts,faces = thread_generator(self.VerticesPerLoop,self.Loops, self.R, self.r, self.h1, self.h2,self.h3,self.h4, self.falloffRate)
        
        mesh = createMeshFromData( self,'Thread', context.scene.cursor.location, verts, [], faces )
        if self.removedouble:
            #distance = 0.001 # remove doubles tolerance.
            mesh = RemoveDoubles(mesh,self.distance)
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)
        return {'FINISHED'}


# Registration

def add_thread_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_thread.bl_idname,
        text="Add Thread",
        icon='MOD_SCREW')


# This allows you to right click on a button and link to documentation
def add_thread_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_thread", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_thread)
    bpy.utils.register_manual_map(add_thread_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_thread_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_thread)
    bpy.utils.unregister_manual_map(add_thread_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_thread_button)


if __name__ == "__main__":
    register()
