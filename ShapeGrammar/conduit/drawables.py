import Rhino
import System

class Drawable:

    def __init__(self):
        self.shaded=True
        self.wired=True
        self.points_on=False
        self.material = Rhino.Display.DisplayMaterial(
            System.Drawing.Colors.Blue)

    def draw(self, e):
        raise NotImplementedError


class DMesh(Drawable):
    def __init__(self,mesh,color=None):
        super(DMesh,self).__init__()
        self.mesh=mesh
        if not color:
            color=System.Drawing.Colors.White
        self.material=Rhino.Display.DisplayMaterial(color)
    def draw(self,e):
        e.Display.DrawMeshShaded(self.mesh)

class DPivot(Drawable):
    def draw(self,e):
        pass
