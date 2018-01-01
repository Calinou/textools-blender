# TexTools for Blender #

TexTools is a free addon for Blender with a collection of UV and Texture related tools. Back in 2009 I released the [Original TexTools](http://renderhjs.net/textools/) for 3dsMax. Currently this is an early development release and more features will be added in the future. Most of the tools are context sensitive or perform 2 actions at once.

![](http://renderhjs.net/textools/blender/img/screenshot_version_0.3.0.png)

## Additional links ##
* [Git repository](https://bitbucket.org/renderhjs/textools-blender) on BitBucket
* [3dsMax version](http://renderhjs.net/textools/) of TexTools
* Blenderartist [discussion](https://blenderartists.org/forum)
* personal website [discussion](renderhjs.net)

---

## Installation ##

1. **Download** [Blender TexTools 0.3.0.zip](https://...)
2. In Blender from the **File** menu open **User Preferences** ![](http://renderhjs.net/textools/blender/img/installation_open_preferences.png) 
3. Go to the **Add-ons** tab ![](http://renderhjs.net/textools/blender/img/installation_addons.png).
4. Hit **Install Addon-on from File...** ![](http://renderhjs.net/textools/blender/img/installation_install_addon_from_file.png) and Select the zip file.
5. Enable the TexTools Addon
6. The TexTools panel can be found in the **UV/Image Editor** view ![](http://renderhjs.net/textools/blender/img/installation_uv_image_editor.png) in the left Tool Panel.

---

# Manual #

## Layout ##


#### Align
![](http://renderhjs.net/textools/blender/img/op_align.png)

In UV vertex mode ![Vert mode](http://renderhjs.net/textools/blender/img/selection_uv_vertex.png) it Aligns selected UV verts to either side of the initial selection bounds.
In the UV face mode ![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png) selected UV islands are aligned to either side of the initial selection bounds.

**Shortcut**: ALT + Arrow keys

#### Align Edge
![](http://renderhjs.net/textools/blender/img/op_island_align_edge.png)

Aligns the UV island of the selected UV edge ![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) to the closest 90 degree angle.

#### Rotate 90°
![](http://renderhjs.net/textools/blender/img/op_island_rotate_90.png)

Rotates the UV island 90 degrees left or right and aligns the island to the initial bounding box's top left or right.


#### Sort & Align
![](http://renderhjs.net/textools/blender/img/op_islands_align_sort.png)

Sorts the selected UV islands by longest side and aligns them vertically or horizontally in a row.


#### Mirror
![](http://renderhjs.net/textools/blender/img/op_island_symmetry.png)

Select the mirror UV edge loop ![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) and both sides will be mirrored and averaged in symetry. Alternatively you can select half of the UV island in UV face mode ![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png) and it's layout will be transferred to the other side.


#### Iron Faces
![](http://renderhjs.net/textools/blender/img/op_faces_iron.png)

Unwraps selected viewpoert faces ![Face mode](http://renderhjs.net/textools/blender/img/selection_view_face.png) into a single UV island. This is often a quicker approach of unwrapping as opposed to marking the boundary edges (mark seams).

---
## Select ##

#### Select Similar
![](http://renderhjs.net/textools/blender/img/op_select_islands_identical.png)

Selects similar UV islands based on the UV island input selection and matching UV Island topology.


#### Select Overlap
![](http://renderhjs.net/textools/blender/img/op_select_islands_overlap.png)

Collects all UV islands that overlap each other and select of each group all except for one island.


#### Select Island Bounds
![](http://renderhjs.net/textools/blender/img/op_select_islands_outline.png)

Selects the edge bounds of all UV Islands in the 3D viewport.

---
## Textures ##

#### Checker Map
![](http://renderhjs.net/textools/blender/img/op_texture_checker.png)

Assigns a checker map to the selected object or cycles through 2 checker maps. When a checker map is assigned it changes the view to texture mode.

![](http://renderhjs.net/textools/blender/img/checker_maps.png)


#### Reload Textures
![](http://renderhjs.net/textools/blender/img/op_textures_reload.png)

Reload all textures in the current blend file
