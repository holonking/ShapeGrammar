import Rhino
from Rhino.Geometry import *
import System
import time
import math
import rhinoscriptsyntax as rs
import ShapeGrammar.core.rhgeo_tools as rhgt
from ShapeGrammar.conduit.drawables import Drawable
from ShapeGrammar.core.shape import Shape,Pivot,Scope


class ExtrBlock(Shape):

    def draw(self, e):
        if not self.visible:
            return
        try:
            self.scope.draw(e)
            if self.representations['visible']:
                if self.representations['brep']:
                    brep = self.representations['brep']
                if self.topo and self.visible_topo:
                    for k in self.topo:
                        m = self.topo[k]
                        c = self.topo.get_color(k)
                        mat = Rhino.Display.DisplayMaterial(c)
                        e.Display.DrawMeshShaded(m, mat)

        except Exception as e:
            print(e)
            time.sleep(1)

    @staticmethod
    def create_from_brepid(brepid):
        brep = rs.coercebrep(brepid)
        scope = Scope.create_from_brepid(brepid)
        base = rhgt.get_brep_bottom_boundary(brep)
        if base:
            height = scope.size[2]
            extr = ExtrBlock(base, scope=scope)
            extr.representations['brep'] = brep
            extr.source_id = brepid
            return extr
        return None

