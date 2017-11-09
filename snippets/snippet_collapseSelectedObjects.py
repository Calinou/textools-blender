
    
    
    # then apply them individually.
    for modifier in target_obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name)