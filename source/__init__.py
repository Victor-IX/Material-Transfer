import bpy


class OBJECT_OT_add_data_transfer(bpy.types.Operator):
    bl_idname = "object.add_data_transfer"
    bl_label = "Add Data Transfer"
    bl_description = "Select the Main object, the base material will be transferred to all child decal objects"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for child in obj.children:
                if "Decal" in child.name and child.type == "MESH":
                    has_modifier = any(mod.type == "DATA_TRANSFER" and mod.name == "N_Decal" for mod in child.modifiers)

                    if "MaterialTransfer" not in child.data.uv_layers:
                        child.data.uv_layers.new(name="MaterialTransfer")
                        self.report({"INFO"}, f"UV map 'MaterialTransfer' added to {child.name}")

                    child.data.uv_layers.active_index = 0
                    tmpuvmap = child.data.uv_layers.active
                    tmpuvmap_name = tmpuvmap.name

                    newuvmap = child.data.uv_layers.new()
                    child.data.uv_layers.remove(tmpuvmap)
                    newuvmap.name = tmpuvmap_name

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
