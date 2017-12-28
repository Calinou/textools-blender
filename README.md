# TexTools for Blender #

TexTools is a collection of tools for UV and Texture related tasks within Blender.

---

#### Download ####

* [Blender TexTools 0.3.0](https://bitbucket.org/tutorials/markdowndemo)

---

## Features ##

#### Align #### 
![](http://renderhjs.net/textools/blender/img/op_align.png)

![Vert mode](http://renderhjs.net/textools/blender/img/selection_uv_vertex.png) Aligns selected UV verts to either side of the initial selection bounds.

![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png) Aligns selected UV islands to either side of the initial selection bounds.

#### Align Edge ####
![](http://renderhjs.net/textools/blender/img/op_island_align_edge.png)

![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) Aligns the UV island of the selected edge to the closest 90 degree angle

#### Rotate 90° ####
![](http://renderhjs.net/textools/blender/img/op_turn_left_right.png)

Rotates the UV selection in 90 degree steps left or right

#### Sort Horizontal / Vertical ####
![](http://renderhjs.net/textools/blender/img/op_islands_align_sort.png)

Sorts the selected UV islands by longest side and aligns them vertically or horizontally in a row.

#### Mirror ####
![](http://renderhjs.net/textools/blender/img/op_island_symmetry.png)

![Edge mode](http://renderhjs.net/textools/blender/img/selection_uv_edge.png) Select the mirror UV edge loop and both sides will be mirrored and averaged in symetry.

![Face mode](http://renderhjs.net/textools/blender/img/selection_uv_face.png)  ...

#### Iron Faces ####
![](http://renderhjs.net/textools/blender/img/op_faces_iron.png)

![Face mode](http://renderhjs.net/textools/blender/img/selection_view_face.png)
Unwrap selected viewpoert faces into a single UV island

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
