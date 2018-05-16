import bpy
import math
from bpy import context
from mathutils import Matrix
from mathutils import Quaternion
from mathutils import Euler
from mathutils import Vector

PFOBJ_VER = 1.0

def mesh_triangulate(mesh):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

def save(operator, context, filepath, global_matrix, export_bbox):
    with open(filepath, "w", encoding="ascii") as ofile:

        mesh_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        meshes = [obj.data for obj in mesh_objs]
        arms   = [obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE']

        textured_mats = [material for material in bpy.data.materials if material.active_texture]

        for mesh in meshes:
            mesh_triangulate(mesh)
            mesh.calc_normals_split()

        num_verts = 0
        for mesh in meshes: 
            num_verts += sum([face.loop_total for face in mesh.polygons])

        num_joints    = sum([len(arm.pose.bones) for arm in arms])
        num_as        = len(bpy.data.actions.items())
        num_materials = sum([len(mesh.materials) for mesh in meshes])
        frame_counts  = [str(int(a.frame_range[1] - a.frame_range[0] + 1)) for a in bpy.data.actions]

        #####################################################################
        # Write header
        #####################################################################

        ofile.write("version        " + str(PFOBJ_VER) + "\n")
        ofile.write("num_verts      " + str(num_verts) + "\n")
        ofile.write("num_joints     " + str(num_joints) + "\n")
        ofile.write("num_materials  " + str(num_materials) + "\n")
        ofile.write("num_as         " + str(num_as) + "\n")
        ofile.write("frame_counts   " + " ".join(frame_counts) + "\n")
        ofile.write("has_collision  " + str(1 if export_bbox is True else 0) + "\n")

        #####################################################################
        # Write vertices and their attributes 
        #####################################################################

        for obj in mesh_objs:
            mesh = obj.data

            for face in mesh.polygons:
                for loop_idx in face.loop_indices:

                    trans = global_matrix * obj.matrix_world

                    v = mesh.vertices[mesh.loops[loop_idx].vertex_index]
                    v_co_world = trans * v.co

                    line = "v {v.x:.6f} {v.y:.6f} {v.z:.6f}\n"
                    line = line.format(v=v_co_world)
                    ofile.write(line)

                    uv_coords = mesh.uv_layers.active.data[loop_idx].uv
                    line = "vt {uv.x:.6f} {uv.y:.6f}\n"
                    line = line.format(uv=uv_coords)
                    ofile.write(line)

                    # The following line will give per-face normals instead
                    # Make it an option at some point ...
                    #normal = global_matrix * mesh.loops[loop_idx].normal
                    normal = global_matrix * v.normal
                    line = "vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n"
                    line = line.format(n=normal)
                    ofile.write(line)

                    line = "vw ";
                    for vg in v.groups:

                        if vg.weight == 0:
                            continue

                        bone_name = obj.vertex_groups[vg.group].name
                        if bone_name not in arms[0].data.bones.keys():
                            continue

                        joint = arms[0].data.bones[bone_name]
                        joint_idx = arms[0].data.bones.values().index(joint)

                        next_elem = " {g}/{w:.6f}"
                        next_elem = next_elem.format(g=joint_idx, w=vg.weight)
                        line += next_elem

                    line += "\n"
                    ofile.write(line)

                    mat_idx = textured_mats.index( mesh.materials[face.material_index] )
                    line = "vm {idx}\n"
                    line = line.format(idx=mat_idx)
                    ofile.write(line)

        #####################################################################
        # Write materials 
        #####################################################################

        for material in textured_mats:

            ofile.write("material " + material.name + "\n")

            line = "    ambient {a:.6f}\n"
            line = line.format(a=material.ambient)
            ofile.write(line)

            line = "    diffuse {c[0]:.6f} {c[1]:.6f} {c[2]:.6f}\n"
            line = line.format(c=(material.diffuse_intensity * material.diffuse_color))
            ofile.write(line)

            line = "    specular {c[0]:.6f} {c[1]:.6f} {c[2]:.6f}\n"
            line = line.format(c=(material.specular_intensity * material.specular_color))
            ofile.write(line)

            line = "    texture " + material.active_texture.image.name + "\n"
            ofile.write(line)

        #####################################################################
        # Write joints
        #####################################################################

        for obj in arms:
            arm = obj.data

            # write Joints
            for bone in arm.bones:

                line = "j {parent_idx} {name}" 
                parent_idx = arm.bones.values().index(bone.parent) + 1 if bone.parent is not None else 0
                line = line.format(parent_idx=parent_idx, name=bone.name)

                # Root bones are given in world coordinates - the rest of the bones'
                # positions are given relative to the parent
                if bone.parent is not None:
                    mat_final = bone.parent.matrix_local.inverted() * bone.matrix_local
                else:
                    mat_final = global_matrix * obj.matrix_world * bone.matrix_local

                line += " {s.x:.6f}/{s.y:.6f}/{s.z:.6f}"
                line = line.format(s=mat_final.to_scale())

                # Unsure why we have to invert the quaternion here...
                # If we convert the quaternion to a matrix using standard algorithms in the engine
                # we get the transpose of the matrix we were supposed to get 
                line += " {q.x:.6f}/{q.y:.6f}/{q.z:.6f}/{q.w:.6f}"
                line = line.format(q=mat_final.to_quaternion().inverted())

                line += " {t.x:.6f}/{t.y:.6f}/{t.z:.6f}"
                line = line.format(t=mat_final.to_translation())

                tip = bone.matrix_local.inverted() * bone.tail_local
                line += " {v.x:.6f}/{v.y:.6f}/{v.z:.6f}"
                line = line.format(v=tip)

                line += "\n"
                ofile.write(line)

        #####################################################################
        # Write animation sets
        #####################################################################

        for action in bpy.data.actions:

            frame_cnt = action.frame_range[1] - action.frame_range[0] + 1;
            ofile.write("as " + action.name + " " + str(int(frame_cnt)) + "\n")

            # Set the current action
            for obj in arms:
                obj.animation_data.action = action

            for f in range(int(action.frame_range[0]), int(action.frame_range[1]+1)):

                bpy.context.scene.frame_set(f)

                obj = arms[0]
                for bone in obj.data.bones:
                    pbone = obj.pose.bones[bone.name]

                    line = "        {idx} {s.x:.6f}/{s.y:.6f}/{s.z:.6f} {q.x:.6f}/{q.y:.6f}/{q.z:.6f}/{q.w:.6f} {t.x:.6f}/{t.y:.6f}/{t.z:.6f}\n"
                    idx = obj.data.bones.values().index(bone) + 1

                    # Root bones are given in world coordinates - the rest of the bones'
                    # positions are given relative to the parent
                    if bone.parent is not None:
                        mat_final = pbone.parent.matrix.inverted() * pbone.matrix
                    else:
                        mat_final = global_matrix * obj.matrix_world * pbone.matrix

                    line = line.format(idx=idx, s=mat_final.to_scale(), q=mat_final.to_quaternion().inverted(), t=mat_final.to_translation())

                    ofile.write(line)

        #####################################################################
        # Write bounding box data
        #####################################################################

        bpy.ops.object.mode_set(mode='EDIT')

        # We build a single bounding box encapsulating all objects - this only works
        # if a single entity is composed of multiple objects - otherwise they must be 
        # exported one at a time
        bbox_verts = []
        for obj in mesh_objs:
            bbox_verts += [global_matrix * obj.matrix_world * Vector(b) for b in obj.bound_box]

        min_x = min(p.x for p in bbox_verts)
        max_x = max(p.x for p in bbox_verts)
        min_y = min(p.y for p in bbox_verts)
        max_y = max(p.y for p in bbox_verts)
        min_z = min(p.z for p in bbox_verts)
        max_z = max(p.z for p in bbox_verts)

        line = "{a:.6f} {b:.6f}\n".format(a=min_x, b=max_x)
        ofile.write(line)
        line = "{a:.6f} {b:.6f}\n".format(a=min_y, b=max_y)
        ofile.write(line)
        line = "{a:.6f} {b:.6f}\n".format(a=min_z, b=max_z)
        ofile.write(line)

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

