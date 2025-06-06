import struct
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox
import os
import math
from collections import OrderedDict
from obj_loader import OBJ

class hex_file:
    def __init__(self, file_obj):
        self.file_obj = file_obj

    def read_int(self, offset, size):
        self.file_obj.seek(offset)
        result = int.from_bytes(self.file_obj.read(size), byteorder='little')
        return result

    def read_string(self, offset, size):
        self.file_obj.seek(offset)
        result = self.file_obj.read(size).decode('utf-8').rstrip('\x00')
        return result

    def read_float(self, offset, size):
        self.file_obj.seek(offset)
        result = struct.unpack('f', self.file_obj.read(size))[0]
        return result

    def float_to_string(self, value, byte_size=4):
        """Convert a float to its byte string representation."""
        if byte_size == 4:
            return struct.pack('<f', value)  # Convert to 4-byte float
        elif byte_size == 8:
            return struct.pack('<d', value)  # Convert to 8-byte double
        else:
            raise ValueError("Unsupported byte size")

    def write_string(self, offset, value):
        self.file_obj.seek(offset)
        self.file_obj.write(value)

# Implementasi string_shortener function
def string_shortener(s):
    return s.split('\x00', 1)[0] if '\x00' in s else s

def rotate_3d_x(x, y, z, degree):
    q = degree * (math.pi / 180)
    new_y = y * math.cos(q) - z * math.sin(q)
    new_z = y * math.sin(q) + z * math.cos(q)
    new_x = x
    return (new_x, new_y, new_z)

# Class YOBJReader
class YOBJReader:
    def __init__(self, filename):
        self.filename = filename
        print(f"Read File: {self.filename}")
        self.file_obj = open(filename, 'rb+')
        self.file = hex_file(self.file_obj)

        self.offset_to_pof0 = self.file.read_int(4, 4) + 8
        print(f"Read POF0 offset: {self.offset_to_pof0}")

        self.size_entry = self.offset_to_pof0 - 8
        print(f"Read Size Entry?: {self.size_entry}")

        self.mesh_count = self.file.read_int(24, 4)
        if self.mesh_count > 2147483647:
            self.mesh_count = self.file.read_int(52, 4)
        print(f"Read Mesh Count: {self.mesh_count}")

        self.texture_count = self.file.read_int(32, 4)
        print(f"Read Texture Count: {self.texture_count}")

        self.texture_start_offset = self.file.read_int(44, 4) + 8
        self.texture_end_offset = self.texture_start_offset + 16 * self.texture_count
        print(f"Read Texture Start Offset: {self.texture_start_offset}")
        print(f"Read Texture End Offset: {self.texture_end_offset}")

        print(f"Get Texture:")
        self.texture_list = self.get_texture_list()

        self.bone_count = self.file.read_int(28, 4)
        print(f"Read Bone Count: {self.bone_count}")

        self.mesh_header_offset = self.file.read_int(36, 4)
        print(f"Read Mesh Header Offset: {self.mesh_header_offset}")

        self.bone_offset = self.file.read_int(40, 4) + 8
        print(f"Read Bone Offset: {self.bone_offset}")

        self.mesh_material_count = []
        self.offset_to_material = []
        self.offset_to_vertex_data = []
        self.mesh_vertices_count = []
        self.mesh_vertice_lenght = []
        self.mesh_flag = []
        self.offset_to_uv_data = []
        print(f"Read Mesh Header:")
        for x in range(self.mesh_count):
            print(f"Object {x}")
            value = self.file.read_int(self.mesh_header_offset + 36 + 64 * x, 4)
            print(f"Read Mesh Flag: {value}")
            flag = value & 1536 != 0
            print(f"Read Mesh Flag Boolean: {flag}")
            binary_val = format(value, '032b')[::-1]
            print(f"Read Mesh Flag Binary: {binary_val}")
            value1 = int(binary_val[16:13:-1], 2)
            print(f"Read Mesh Flag Integer: {value1}")
            offset = self.file.read_int(self.mesh_header_offset + 32 + 64 * x, 4) + 8
            offset = self.file.read_int(offset, 4) + 8
            print(f"Read Mesh Offset: {offset}")
            if flag:
                uv_offset = offset + (value1 + 1) * 4
            else:
                uv_offset = offset
            print(f"Read UV Offset: {uv_offset}")
            self.offset_to_uv_data.append(uv_offset)
            if flag:
                vertex_offset = offset + (value1 + 1 + 3) * 4
            else:
                vertex_offset = offset + 12
            print(f"Read Vertex Offset: {vertex_offset}")
            self.offset_to_vertex_data.append(vertex_offset)
            if flag:
                self.mesh_vertice_lenght.append((value1 + 10) * 4)
            else:
                self.mesh_vertice_lenght.append(36)
            print(f"Read Vertice Lenght: {self.mesh_vertice_lenght[x]}")
            self.mesh_flag.append(flag)
            self.mesh_vertices_count.append(self.file.read_int(self.mesh_header_offset + 48 + 64 * x, 4))
            print(f"Read Vertice Count: {self.mesh_vertices_count[x]}")
            self.offset_to_material.append(self.file.read_int(self.mesh_header_offset + 20 + 64 * x, 4) + 8)
            print(f"Read Offset To Material: {self.offset_to_material[x]}")
            self.mesh_material_count.append(self.file.read_int(self.mesh_header_offset + 12 + 64 * x, 4))
            print(f"Read Mesh Material Count: {self.mesh_material_count[x]}")

    def get_vertex_data(self, mesh_id):
        print(f"Get Vertex Data: Object {mesh_id}")
        vertex_list = []
        offset = self.offset_to_vertex_data[mesh_id]
        vertice_lenght = self.mesh_vertice_lenght[mesh_id]
        for x in range(self.mesh_vertices_count[mesh_id]):  # Ubah xrange ke range
            vertex_x = self.file.read_float(offset + vertice_lenght * x + 12, 4)
            vertex_y = self.file.read_float(offset + vertice_lenght * x + 16, 4)
            vertex_z = self.file.read_float(offset + vertice_lenght * x + 20, 4)
            print(f"Vertice {x}: x {vertex_x}, y {vertex_y}, z {vertex_z}")
            vertex_list.append([vertex_x, vertex_y, vertex_z])
        return vertex_list

    def get_uv_data(self, mesh_id):
        print(f"Get UV Data: Object {mesh_id}")
        uv_list = []
        offset = self.offset_to_uv_data[mesh_id]
        vertice_lenght = self.mesh_vertice_lenght[mesh_id]
        for x in range(self.mesh_vertices_count[mesh_id]):
            uv_x = self.file.read_float(offset + vertice_lenght * x + 0, 4)
            uv_y = self.file.read_float(offset + vertice_lenght * x + 4, 4)
            print(f"UV {x}: x {uv_x}, y {uv_y}")
            uv_list.append([uv_x, uv_y])
        return uv_list

    def get_face_data(self, mesh_id):
        print(f"Get Face Data: Object {mesh_id}")
        face_list = []
        offset = self.offset_to_material[mesh_id]
        material_count = self.mesh_material_count[mesh_id]
        face_data = []
        for x in range(0, material_count):
            print(f"Material {x}")
            faces_header_count = self.file.read_int(offset + 132, 4)
            print(f"Face Header Count: {faces_header_count}")
            faces_header_start = self.file.read_int(offset + 136, 4) + 8
            print(f"Face Header Start: {faces_header_start}")
            face_data.append([faces_header_count, faces_header_start])
            offset += 144

        for i, j in face_data:
            for x in range(i):
                face_count = self.file.read_int(j + 8 + 16 * x, 4)
                face_offset = self.file.read_int(j + 12 + 16 * x, 4) + 8
                print(f"Face {x}: Count {face_count}, Offset {face_offset}")
                offset = face_offset
                v1 = -1
                v2 = -1
                direct = -1
                for y in range(face_count):
                    direct *= -1
                    v3 = self.file.read_int(offset, 2)
                    print(f"Face {y}: direct {direct}, v1 {v1}, v2 {v2}, v3 {v3}")
                    if v1 != -1 and v2 != -1:
                        if direct > 0:
                            face_list.append([v1, v2, v3])
                            print(f"[{v1+1}, {v2+1}, {v3+1}]")
                        else:
                            face_list.append([v1, v3, v2])
                            print(f"[{v1+1}, {v3+1}, {v2+1}]")
                    v1 = v2
                    v2 = v3
                    offset += 2

        return face_list

    def get_face_data_log(self, mesh_id):
        face_list = []
        offset = self.offset_to_material[mesh_id]
        material_count = self.mesh_material_count[mesh_id]
        face_data = []
        for x in range(0, material_count):
            faces_header_count = self.file.read_int(offset + 132, 4)
            print(f"Face Header Count: {faces_header_count}")
            faces_header_start = self.file.read_int(offset + 136, 4) + 8
            print(f"Face Header Start: {faces_header_start}")
            face_data.append([faces_header_count, faces_header_start])
            offset += 144

        for i, j in face_data:
            temp_face = []
            for x in range(i):
                face_count = self.file.read_int(j + 8 + 16 * x, 4)
                face_offset = self.file.read_int(j + 12 + 16 * x, 4) + 8
                print(f"Face {x}: Count {face_count}, Offset {face_offset}")
                offset = face_offset
                v1 = -1
                v2 = -1
                direct = -1
                for y in range(face_count):
                    direct *= -1
                    v3 = self.file.read_int(offset, 2)
                    print(f"Face {y}: direct {direct}, v1 {v1}, v2 {v2}, v3 {v3}")
                    if v1 != -1 and v2 != -1:
                        if direct > 0:
                            temp_face.append([v1, v2, v3])
                            print(f"[{v1+1}, {v2+1}, {v3+1}]")
                        else:
                            temp_face.append([v1, v3, v2])
                            print(f"[{v1+1}, {v3+1}, {v2+1}]")
                    v1 = v2
                    v2 = v3
                    offset += 2

            face_list.append(temp_face)

        return face_list

    def get_texture_pointed(self, mesh_id):
        print(f"Read Object {mesh_id} Texture")
        material_count = self.mesh_material_count[mesh_id]
        offset = self.offset_to_material[mesh_id]
        texture_list = []
        for x in range(material_count):
            texture_id = self.file.read_int(offset + 22, 2)
            texture_list.append(texture_id)
            print(f"Material {x}, Texture: {texture_id}")
            offset += 144

        return texture_list

    def get_unknown_float(self, mesh_id):
        print(f"Read Object {mesh_id} Unknown Float")
        material_count = self.mesh_material_count[mesh_id]
        offset = self.offset_to_material[mesh_id]
        float_list = []
        for x in range(material_count):
            unknown_float = self.file.read_float(offset + 16, 4)
            print(f"Material {x}, Value: {unknown_float} * 0.01 = {unknown_float *0.01}")
            unknown_float *= 0.01
            float_list.append(unknown_float)
            offset += 144

        return float_list

    def get_face_data_and_tex(self, mesh_id):
        print(f"Read Object {mesh_id} Faces")
        face_dict = OrderedDict()
        offset = self.offset_to_material[mesh_id]
        material_count = self.mesh_material_count[mesh_id]
        texture_list = self.get_texture_pointed(mesh_id)
        float_list = self.get_unknown_float(mesh_id)
        face_data = []
        for x in range(0, material_count):
            faces_header_count = self.file.read_int(offset + 132, 4)
            print(f"Face Header Count: {faces_header_count}")
            faces_header_start = self.file.read_int(offset + 136, 4) + 8
            print(f"Face Header Start: {faces_header_start}")
            face_data.append([faces_header_count, faces_header_start])
            offset += 144

        for z, (i, j) in enumerate(face_data):
            face_list = []
            for x in range(i):
                face_count = self.file.read_int(j + 8 + 16 * x, 4)
                face_offset = self.file.read_int(j + 12 + 16 * x, 4) + 8
                print(f"Face {x}: Count {face_count}, Offset {face_offset}")
                offset = face_offset
                v1 = -1
                v2 = -1
                direct = -1
                for y in range(face_count):
                    direct *= -1
                    v3 = self.file.read_int(offset, 2)
                    print(f"Face {y}: direct {direct}, v1 {v1}, v2 {v2}, v3 {v3}")
                    if v1 != -1 and v2 != -1:
                        if direct:
                            face_list.append([v1, v2, v3])
                            print(f"[{v1+1}, {v2+1}, {v3+1}]")
                        else:
                            face_list.append([v1, v3, v2])
                            print(f"[{v1+1}, {v3+1}, {v2+1}]")
                    v1 = v2
                    v2 = v3
                    offset += 2

            face_dict[z] = [
             face_list, texture_list[z], float_list[z]]

        return face_dict

    def get_obj_details(self):
        obj_details = []
        for i in range(self.mesh_count):
            vertex_count = self.mesh_vertices_count[i]
            obj_details.append(f"Object {i}. Vertice Count: {vertex_count}")
        return obj_details

    def get_texture_list(self):
        texture = []
        for offset in range(self.texture_start_offset, self.texture_end_offset, 16):
            name = string_shortener(self.file.read_string(offset, 16))
            texture.append(name)
        return texture

    def export_as_one_obj(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.dirname(self.filename)
        obj_filename = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(self.filename))[0]}.obj')
        mtl_filename = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(self.filename))[0]}.mtl')

        with open(obj_filename, 'w') as obj_file, open(mtl_filename, 'w') as mtl_file:
            obj_file.write('# Exported by YOBJReader\n')
            obj_file.write(f'mtllib {os.path.basename(mtl_filename)}\n')

            line_count = 0
            mat_count = 0
            texture_list = self.get_texture_list()

            for mesh_id in range(self.mesh_count):
                obj_file.write(f'# Mesh {mesh_id}\n')
                vertex_list = self.get_vertex_data(mesh_id)
                for vertex in vertex_list:
                    coord_x, coord_y, coord_z = rotate_3d_x(vertex[0], vertex[1], vertex[2], 180)
                    obj_file.write(f'v {round(coord_x, 6) + 0.0} {round(-coord_z, 6) + 0.0} {round(coord_y, 6) + 0.0}\n')

                uv_list = self.get_uv_data(mesh_id)
                for uv in uv_list:
                    coord_x, coord_y = uv
                    obj_file.write(f'vt {round(coord_x, 6) + 0.0} {round(coord_y, 6) + 0.0}\n')

                face_dict = self.get_face_data_and_tex(mesh_id)
                for mat_id in face_dict:
                    obj_file.write(f'usemtl mat{mat_id + mat_count}\n')
                    face_list = face_dict[mat_id][0]
                    for face in face_list:
                        obj_file.write(f'f {face[0] + 1 + line_count}/{face[0] + 1 + line_count} '
                                       f'{face[1] + 1 + line_count}/{face[1] + 1 + line_count} '
                                       f'{face[2] + 1 + line_count}/{face[2] + 1 + line_count}\n')

                    mtl_file.write(f'newmtl mat{mat_id + mat_count}\n')
                    mtl_file.write('Kd 0.984 0.984 1.000\n')
                    mtl_file.write('Ks 0.502 0.502 0.502\n')
                    mtl_file.write(f'map_Kd {texture_list[face_dict[mat_id][1]]}.png\n')

                line_count += len(vertex_list)
                mat_count += max(face_dict.keys()) + 1

        print(f'OBJ and MTL files exported to {output_dir}')

    def batch_export_as_one_obj(self, input_folder):
        # Gunakan os.walk untuk mendapatkan semua folder, subfolder, dan file di dalamnya
        for root, dirs, files in os.walk(input_folder):
            yobj_files = [f for f in files if f.lower().endswith('.yobj')]
            if not yobj_files:
                continue  # Skip folder jika tidak ada file .yobj

            for file_name in yobj_files:
                file_path = os.path.join(root, file_name)
                yobj_reader = YOBJReader(file_path)
                yobj_reader.export_as_one_obj(output_dir=root)  # Simpan hasil di folder yang sama

        messagebox.showinfo("Sukses", "Semua file YOBJ dan subfolder telah diekspor ke format OBJ dan MTL.")


    def inject_obj(self, mesh_id, filename):
        obj_file = OBJ(filename)
        vertex_list = obj_file.vertex
        normal_list = obj_file.normal
        face_list = obj_file.face  # Pastikan face tidak berubah
        offset = self.offset_to_vertex_data[mesh_id]
        vertice_lenght = self.mesh_vertice_lenght[mesh_id]

        if len(vertex_list) != self.mesh_vertices_count[mesh_id]:
            raise AssertionError("This function only supports injecting OBJ with the same amount of vertices")

        # Inject vertex data
        for x in range(self.mesh_vertices_count[mesh_id]):
            vertex_x, vertex_y, vertex_z = rotate_3d_x(vertex_list[x][0], vertex_list[x][2], -vertex_list[x][1], -180)
            vertex_offset = offset + 12  # Pastikan offset tetap akurat
            data_v_x = self.file.float_to_string(vertex_x, 4)
            data_v_y = self.file.float_to_string(vertex_y, 4)
            data_v_z = self.file.float_to_string(vertex_z, 4)
            self.file.write_string(vertex_offset, data_v_x)
            self.file.write_string(vertex_offset + 4, data_v_y)
            self.file.write_string(vertex_offset + 8, data_v_z)
            offset += vertice_lenght

        # UV tidak disentuh, pastikan tidak diubah
        # Jika masih rusak, cek apakah face_list tetap sama setelah inject

        self.file.file_obj.flush()



    def get_object_count(self):
        return self.mesh_count

class YOBJ_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Export/Import YOBJ to/from OBJ")

        self.create_widgets()

    def create_widgets(self):
        # Label
        tk.Label(self.root, text="Pilih folder yang berisi file YOBJ:").pack(pady=10)

        # Tombol untuk batch export
        tk.Button(self.root, text="Batch Export YOBJ", command=self.browse_folder_export).pack(pady=5)

        # Tombol untuk batch import
        tk.Button(self.root, text="Batch Import YOBJ", command=self.browse_folder_import).pack(pady=5)

    def browse_folder_export(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.batch_export_as_one_obj(folder_selected)

    def browse_folder_import(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.batch_import_obj_to_yobj(folder_selected)

    def batch_export_as_one_obj(self, input_folder):
        # Gunakan os.walk untuk mendapatkan semua folder, subfolder, dan file di dalamnya
        for root, dirs, files in os.walk(input_folder):
            yobj_files = [f for f in files if f.lower().endswith('.yobj')]
            if not yobj_files:
                continue  # Skip folder jika tidak ada file .yobj

            for file_name in yobj_files:
                file_path = os.path.join(root, file_name)
                yobj_reader = YOBJReader(file_path)
                yobj_reader.export_as_one_obj(output_dir=root)  # Simpan hasil di folder yang sama

        messagebox.showinfo("Sukses", "Semua file YOBJ dan subfolder telah diekspor ke format OBJ dan MTL.")


    def batch_import_obj_to_yobj(self, input_folder):
        yobj_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.yobj')]
        if not yobj_files:
            messagebox.showinfo("Info", "Tidak ada file YOBJ ditemukan di folder yang dipilih.")
            return

        for yobj_file in yobj_files:
            yobj_path = os.path.join(input_folder, yobj_file)
            yobj_reader = YOBJReader(yobj_path)

            if yobj_reader.get_object_count() == 1:  # Mengecek apakah hanya ada satu objek
                obj_path = os.path.join(input_folder, yobj_file.replace('.yobj', '.obj'))
                if os.path.exists(obj_path):
                    yobj_reader.inject_obj(0, obj_path)
                    print("Sukses", f"OBJ {obj_path} berhasil diimpor ke {yobj_file}.")
                else:
                    messagebox.showwarning("Warning", f"File OBJ {obj_path} tidak ditemukan.")
            else:
                print("Warning", f"File YOBJ {yobj_file} memiliki lebih dari satu objek dan dilewati.")

if __name__ == "__main__":
    root = tk.Tk()
    app = YOBJ_GUI(root)
    root.mainloop()
