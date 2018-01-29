import clr
import System
import Rhino
from ShapeGrammar.core.geometries import Scope
from ShapeGrammar.conduit.monitor import ConduitMonitor

class DisplayEngine(Rhino.Display.DisplayConduit):
    def __init__(self):
        super(DisplayEngine,self).__init__()

        self.drawables={'pre':[],
                        'post':[],
                        'fore':[],
                        'overlay':[]
                        }
        self.vector_display_size=1



    def add(self,obj, group='post'):
        self.drawables[group].append(obj)

    def pop(self,obj, group='post'):
        i=self.drawables[group].index(obj)
        if i >= 0:
            self.drawables[group].pop(i)

    def clear(self, group=None):
        if group:
            self.drawables[group]=[]
        else:
            for key in self.drawables:
                self.drawables[key]=[]


    def CalculateBoundingBox(self, e):
        try:
            for key in self.drawables:
                for o in self.drawables[key]:
                    if isinstance(o, Scope):
                        for p in o.points:
                            bbox=Rhino.Geometry.BoundingBox(o.points)
                            e.IncludeBoundingBox(bbox)


        except Exception as e:
            print(e)
            raise SyntaxError

    def PreDrawObjects(self, e):
        #super().PretDrawObjects(e)
        # Called before every object in the scene is drawn
        try:
            for o in self.drawables['pre']:
                o.draw(e)

        except Exception as e:
            print(e)
            raise SyntaxError

    def PostDrawObjects(self, e):
        #super().PostDrawObjects(e)
        # Called after all non-highlighted objects
        # are drawn. Depth writing and testing are
        # still turned on. If you want to draw without
        # depth writing and testing, see DrawForeground.
        # Here you draw stuff on top of all the objects,
        # like selection wireframes.
        try:
            for o in self.drawables['post']:
                o.draw(e)

        except Exception as e:
            print(e)
            raise SyntaxError


    def DrawForeground(self, e):
        # Called after all non-highlighted objects
        # are drawn and PostDrawObjects called.
        # Depth writing and testing are turned off.
        # If you want to draw with depth writing
        # and testing, see PostDrawObjects.
        # For example, here you could draw objects
        # like the little axis-system in the
        # lower left corner of viewports.
        try:
            for o in self.drawables['fore']:
                o.draw(e)

        except Exception as e:
            print(e)
            raise SyntaxError

    def DrawOverlay(self, e):
        try:
            for o in self.drawables['overlay']:
                o.draw(e)

        except Exception as e:
            print(e)
            raise SyntaxError


    def _draw_vectors(self,e):
        s=self.vector_display_size
        for pos,vect,clr in self.vectors:
            e.Display.DrawArrow(Rhino.Geometry.Line(pos,pos+(vect*s)),clr)

    def _draw_ppoints(self,e):
        for p,clr in self.points:
            e.Display.DrawPoint(p,clr)

    def add_coord(self,pos,vects):
        self.points.append(pos,System.Drawing.Color.White)
        xvect = (pos, vects[0], System.Drawing.Color.Red)
        yvect = (pos, vects[1], System.Drawing.Color.Green)
        zvect = (pos, vects[2], System.Drawing.Color.Blue)


    def create_monitor(self):
        cm = ConduitMonitor(self)

