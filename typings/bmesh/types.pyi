from typing import Optional

from bpy.types import Mesh
from mathutils import Matrix

class BMEdgeSeq: ...
class BMFaceSeq: ...

class BMesh:
    edges: BMEdgeSeq
    faces: BMFaceSeq
    is_valid: bool
    is_wrappes: bool

    def from_mesh(
        self,
        mesh: Mesh,
        face_normals: bool = True,
        vertex_normals: bool = True,
        use_shape_key: bool = False,
        shape_key_index: int = 0,
    ) -> None: ...
    def clear(self) -> None: ...
    def copy(self) -> BMesh: ...
    def free(self) -> None: ...
    def to_mesh(self, mesh: Mesh) -> None: ...
    def transform(self, matrix: Matrix, filter: Optional[set[str]] = None) -> None: ...
