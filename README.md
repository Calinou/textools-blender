# TexTools for Blender #

TexTools is a collection of tools for UV and Texture related tasks within Blender. Back in 2009 I released the [Original TexTools](http://renderhjs.net/textools/) for 3dsMax.


## Installation ##

1. Download [Blender TexTools 0.3.0.zip](https://bitbucket.org/tutorials/markdowndemo)
2. In Blender open **Blender User Preferences** (Ctrl + Alt + U) and go to the **Add-ons** tab.
3. Hit **Install Addon-on from File...** and Select the zip file.
4. The TexTools panel can be found in the UV editor view in the left Tool Panel.

---

## Features ##


#### Align #### 
![](http://renderhjs.net/textools/blender/img/op_align.png)

In UV vertex mode ![Vert mode](http://renderhjs.net/textools/blender/img/selection_uv_vertex.png) it Aligns selected UV verts to either side of the initial selection bounds.
In the UV face mode ![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png) selected UV islands are aligned to either side of the initial selection bounds.


#### Align Edge ####
![](http://renderhjs.net/textools/blender/img/op_island_align_edge.png)

Aligns the UV island of the selected UV edge ![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) to the closest 90 degree angle


#### Rotate 90° ####
![](http://renderhjs.net/textools/blender/img/op_turn_left_right.png)

Rotates the UV selection in 90 degree steps left or right


#### Sort & Align ####
![](http://renderhjs.net/textools/blender/img/op_islands_align_sort.png)

Sorts the selected UV islands by longest side and aligns them vertically or horizontally in a row.


#### Mirror ####
![](http://renderhjs.net/textools/blender/img/op_island_symmetry.png)

Select the mirror UV edge loop ![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) and both sides will be mirrored and averaged in symetry. Alternatively you can select half of the UV island in UV face mode ![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png) and it's layout will be transferred to the other side.


#### Iron Faces ####
![](http://renderhjs.net/textools/blender/img/op_faces_iron.png)

Unwraps selected viewpoert faces ![Face mode](http://renderhjs.net/textools/blender/img/selection_view_face.png) into a single UV island.

---

#### Select Similar ####
![](http://renderhjs.net/textools/blender/img/op_select_islands_identical.png)

Selects similar UV islands based on the UV island input selection.


#### Select Overlap ####
![](http://renderhjs.net/textools/blender/img/op_select_islands_overlap.png)

Collects all UV islands that overlap each other and select of each group all except for one island.


#### Select Island Bounds ####
![](http://renderhjs.net/textools/blender/img/op_select_islands_outline.png)

Selects the edge bounds of all UV Islands in the 3D viewport.

---

#### Checker Map ####
![](http://renderhjs.net/textools/blender/img/op_texture_checker.png)

Assigns and or cycles through 2 checker maps and previous material. When a checker map is assigned it changes the view to texture mode.


#### Reload Textures ####
![](http://renderhjs.net/textools/blender/img/op_textures_reload.png)

Reload all textures in the *.blend file
