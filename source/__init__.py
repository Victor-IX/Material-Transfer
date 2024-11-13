import bpy


class OBJECT_OT_add_data_transfer(bpy.types.Operator):
    bl_idname = "object.add_data_transfer"
    bl_label = "Add Data Transfer"
    bl_description = "Select the Main object, the base material will be transferred to all child decal objects"

    def execute(self, context):
        main_texture_group = None

        for obj in bpy.context.selected_objects:
            # Get the main texture group
            if not obj.material_slots:
                self.report({"ERROR"}, "Object has no material slots")
                return {"CANCELLED"}
            for mat_slot in obj.material_slots:
                material = mat_slot.material
                if material and material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == "GROUP" and "materialtransfer" in node.node_tree.name.lower():
                            main_texture_group = node.node_tree.name
                else:
                    self.report({"ERROR"}, "Material has no nodes")
                    return {"CANCELLED"}
            if not main_texture_group:
                self.report({"ERROR"}, "No main texture group found")
                return {"CANCELLED"}

            # Child Iteration
            for child in obj.children:
                if "decal" in child.name.lower() and child.type == "MESH":
                    has_modifier = any(mod.type == "DATA_TRANSFER" and mod.name == "N_Decal" for mod in child.modifiers)

                    if "MaterialTransfer" not in child.data.uv_layers:
                        child.data.uv_layers.new(name="MaterialTransfer")
                        self.report({"INFO"}, f"UV map 'MaterialTransfer' added to {child.name}")

                    index_0 = child.data.uv_layers[0]

                    max_repetitions = 50
                    counter = 0

                    # Ensure that index 0 is the transfer UV map
                    while "MaterialTransfer" not in index_0.name:
                        if counter >= max_repetitions:
                            self.report({"WARNING"}, "Max repetitions reached. Exiting loop.")
                            break
                        child.data.uv_layers.active_index = 0
                        tmpuvmap = child.data.uv_layers.active
                        tmpuvmap_name = tmpuvmap.name
                        child.data.uv_layers.remove(tmpuvmap)
                        child.data.uv_layers.new(name=tmpuvmap_name)
                        index_0 = child.data.uv_layers[0]
                        counter += 1

                    if not has_modifier:
                        modifier = child.modifiers.new(name="N_Decal", type="DATA_TRANSFER")
                        modifier.use_loop_data = True
                        modifier.data_types_loops = {"UV"}
                        modifier.loop_mapping = "POLYINTERP_NEAREST"
                        modifier.object = obj
                        modifier.layers_uv_select_src = "UVMap"
                        modifier.layers_uv_select_dst = "INDEX"

                        self.report({"INFO"}, f"Added 'N_Decal' modifier to {child.name}")
                    else:
                        self.report(
                            {"INFO"},
                            f"'{child.name}' already has the 'N_Decal' modifier",
                        )

                    # Transfer the material
                    if not child.material_slots:
                        self.report({"ERROR"}, "Object has no material slots")
                        return {"CANCELLED"}

                    for mat_slot in child.material_slots:
                        material = mat_slot.material
                        if material and material.use_nodes:
                            node_tree = material.node_tree

                            main_material_group = material.node_tree.nodes.new(type="ShaderNodeGroup")
                            main_material_group.node_tree = bpy.data.node_groups[main_texture_group]

                            for node in node_tree.nodes:
                                if node.type == "GROUP":
                                    if node.node_tree.name == ".subset.decal_group":
                                        decal_group = node

                            if main_material_group and decal_group:
                                # output_socket = None
                                # input_socket = None

                                # for item in main_material_group.interface.items_tree:
                                #     if item.item_type == "SOCKET" and item.in_out == "OUTPUT" and item.name == "BC":
                                #         output_socket = item

                                # for item in decal_group.interface.items_tree:
                                #     if (
                                #         item.item_type == "SOCKET"
                                #         and item.in_out == "INPUT"
                                #         and item.name == "Material Base Color"
                                #     ):
                                #         input_socket = item

                                node_tree = material.node_tree.links
                                node_tree.new(
                                    main_material_group.outputs["BC"],
                                    decal_group.inputs["Material Base Color"],
                                )

                else:
                    self.report(
                        {"INFO"},
                        f"'{child.name}' does not contain 'Decal' or is not a mesh, skipping.",
                    )

        return {"FINISHED"}


class OBJECT_PT_tools_panel(bpy.types.Panel):
    bl_label = "Decal Tools"
    bl_idname = "OBJECT_PT_tools_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.add_data_transfer", text="Add Material to Decal")


def register():
    bpy.utils.register_class(OBJECT_OT_add_data_transfer)
    bpy.utils.register_class(OBJECT_PT_tools_panel)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_data_transfer)
    bpy.utils.unregister_class(OBJECT_PT_tools_panel)


if __name__ == "__main__":
    register()
