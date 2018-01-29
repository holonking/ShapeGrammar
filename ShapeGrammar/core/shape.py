import System
import rhinoscriptsyntax as rs
from Rhino.Geometry import *
import ShapeGrammar.core.rhgeo_tools as rhgt
import math

SYSCOLORS = {
    'Red': System.Drawing.Color.Red,
    'Green': System.Drawing.Color.Green,
    'Blue': System.Drawing.Color.Blue,

}



class Drawable(object):
    def __init__(self):
        self.visible = True
    def draw(self, e):
        raise NotImplementedError

class Pivot(object):
    display_size = 1

    def __init__(self, pos=None, vects=None):
        if pos is None:
            pos = Point3d(0, 0, 0)
        if vects is None:
            vects = (
                Vector3d(1, 0, 0),
                Vector3d(0, 1, 0),
                Vector3d(0, 0, 1)
            )
        self.visible = True
        self.pos = pos
        self.vects = [None, None, None]
        if isinstance(vects, Vector3d):
            self.vects[0] = vects
            self.vects[2] = Vector3d(0, 0, 1)
            self.vects[1] = Vector3d.CrossProduct(self.vects[0], self.vects[2]) * -1
        elif len(vects) == 2:
            self.vects[0] = vects[0]
            self.vects[1] = vects[1]
            self.vects[2] = Vector3d(0, 0, 1)
        else:
            self.vects[0] = vects[0]
            self.vects[1] = vects[1]
            self.vects[2] = vects[2]

        self.vects[0].Unitize()
        self.vects[1].Unitize()
        self.vects[2].Unitize()

    def __str__(self):
        txt = '<p({}) x({}) y({}) z({})>'.format(
            str(self.pos),
            str(self.vects[0]),
            str(self.vects[1]),
            str(self.vects[2])
        )
        return txt

    def rotate(self, degree):
        radian = math.radians(degree)
        tr = Transform.Rotation(radian, Point3d(0, 0, 0))
        for i in range(len(self.vects)):
            self.vects[i].Transform(tr)
        return tr

    def move(self, vect):
        self.pos += vect

    def clone(self):
        pos = Point3d(self.pos)
        vects = []
        for i in range(len(self.vects)):
            vects.append(self.vects[i])
        return Pivot(pos, vects)

    def draw(self, e):
        if self.visible:
            p1 = Point3d(self.pos)
            px = (self.pos + self.vects[0]) * Pivot.display_size
            py = (self.pos + self.vects[1]) * Pivot.display_size
            pz = (self.pos + self.vects[2]) * Pivot.display_size

            e.Display.DrawPoint(p1, System.Drawing.Color.White)
            e.Display.DrawArrow(Line(p1, Point3d(px)), System.Drawing.Color.Red)
            e.Display.DrawArrow(Line(p1, Point3d(py)), System.Drawing.Color.Green)
            e.Display.DrawArrow(Line(p1, Point3d(pz)), System.Drawing.Color.Blue)

class Scope(object):
    def __init__(self, pivot=None, size=None):
        self.visible = True
        self.show_frame = True
        if not pivot:
            self._pivot = Pivot()
        else:
            self._pivot = pivot
        if size:
            self._size = size
        else:
            self._size = Vector3d(1, 1, 1)
        self.points = []
        self._set_points()
        self.color = System.Drawing.Color.Yellow

    @property
    def size(self):
        return self._size

    @property
    def pivot(self):
        return self._pivot

    def set_size(self, size, set_points=True):
        self._size = size
        if set_points:
            self._set_points()

    def set_pivot(self, pivot, set_points=True):
        self._pivot = pivot
        if set_points:
            self._set_points()

    def set_dir_amp(self,direct,amp,clone=False):
        if clone:
            nscope = self.scope.clone()
        else:
            nscope=self
        pushindice = []
        refindice = []
        if direct == 'x':
            pushindice = [1, 2, 5, 6]
            refindice = [0, 3, 4, 7]
            vect=self.pivot.vects[0]
        elif direct == 'y':
            pushindice = [2, 3, 6, 7]
            refindice = [1, 0, 5, 4]
            vect = self.pivot.vects[1]
        else:
            pushindice = [4, 5, 6, 7]
            refindice = [0, 1, 2, 3]
            vect = self.pivot.vects[2]

        for r,p in zip(refindice,pushindice):
            self.points[p]=self.points[r]+vect

        if clone:
            return nscope
        return None

    def rotate(self, degree):
        self.pivot.rotate(degree)
        self._set_points()

    def move(self, vect):
        # for i in range(len(self.points)):
        #   self.points[i] += vect
        self.pivot.move(vect)
        self._set_points()

    def flip(self, axis=0):
        # axis can be 0:x,1:y,2:z
        vect = self.pivot.vects[axis] * self.size[axis]
        self.pivot.move(vect)
        self.pivot.vects[axis] *= -1

    def turn(self, count=1):
        # count=1 rotate 90 degree
        # count can be 0-n
        for i in range(count):
            vects = [None] * 3
            pos = self.pivot.pos + (self.pivot.vects[0] * self.size[0])
            vects[0] = self.pivot.vects[1]
            vects[1] = self.pivot.vects[0] * -1
            vects[2] = self.pivot.vects[2]
            self.pivot.pos = pos
            self.pivot.vects = vects
            size = Vector3d(self.size[1], self.size[0], self.size[2])
            self._size = size

        self._set_points()

    def clone(self):
        pivot = self.pivot.clone()
        size = Vector3d(self.size)
        scope = Scope(pivot, size)
        return scope



    def _set_points(self):
        self.points = []
        pos = self.pivot.pos
        vx = self.pivot.vects[0]
        vy = self.pivot.vects[1]
        vz = self.pivot.vects[2]
        sx = self.size[0]
        sy = self.size[1]
        sz = self.size[2]
        # bottom points
        self.points.append(pos)  # 0
        self.points.append(pos + (vx * sx))
        self.points.append(self.points[1] + (vy * sy))
        self.points.append(pos + (vy * sy))

        # top points
        svz = vz * sz
        for i in range(4):
            self.points.append(self.points[i] + svz)

    def draw(self, e):
        pts = self.points
        color = self.color
        if self.visible:
            if self.show_frame:
                e.Display.DrawLine(pts[0], pts[1], color)
                e.Display.DrawLine(pts[1], pts[2], color)
                e.Display.DrawLine(pts[2], pts[3], color)
                e.Display.DrawLine(pts[3], pts[0], color)

                e.Display.DrawLine(pts[4], pts[5], color)
                e.Display.DrawLine(pts[5], pts[6], color)
                e.Display.DrawLine(pts[6], pts[7], color)
                e.Display.DrawLine(pts[7], pts[4], color)

                e.Display.DrawLine(pts[0], pts[4], color)
                e.Display.DrawLine(pts[1], pts[5], color)
                e.Display.DrawLine(pts[2], pts[6], color)
                e.Display.DrawLine(pts[3], pts[7], color)

                for i in range(len(pts)):
                    txt = str(i)
                    e.Display.Draw2dText(txt, System.Drawing.Color.Black,
                                         pts[i], True, 20)
            self.pivot.draw(e)

        # following 2 lines do not work
        # e.Display.EnableDepthWriting(False)
        # e.Display.EnDepthTesting(False)

    @staticmethod
    def create_from_bbox(bbox):
        s = Scope()
        vects = []
        pos = bbox[0]
        vects.append(bbox[1] - bbox[0])
        vects.append(bbox[2] - bbox[1])
        vects.append(bbox[4] - bbox[0])
        size = Vector3d(vects[0].Length, vects[1].Length, vects[2].Length)

        s.set_pivot(Pivot(pos, vects), False)
        s.set_size(size)
        return s

    @staticmethod
    def create_from_brepid(brepid):
        brep = rs.coercebrep(brepid)
        maxLength = 0
        maxs = None
        maxe = None
        for e in brep.Edges:
            if abs(e.PointAtStart.Z - e.PointAtEnd.Z) < 0.001:
                length = e.GetLength()
                if length > maxLength:
                    maxLength = length
                    maxs = e.PointAtStart
                    maxe = e.PointAtEnd

        vx = maxe - maxs
        vy = Vector3d.CrossProduct(vx, Vector3d(0, 0, 1))
        vy *= -1
        pln = Plane(maxs, vx, vy)
        bbox = rs.BoundingBox(brepid, pln)
        s = Scope.create_from_bbox(bbox)
        return s

    @staticmethod
    def _create_from_mesh_group(self,meshs,plane_vect=None):
        pass

class Topology(dict):
    def __init__(self, *args, **kwargs):
        super(Topology, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.top = Mesh()
        self.bot = Mesh()
        self.left = Mesh()
        self.right = Mesh()
        self.front = Mesh()
        self.back = Mesh()

    def get_color(self, index):
        if index == 'top':
            return System.Drawing.Color.LawnGreen
        elif index == 'bot':
            return System.Drawing.Color.Gray
        elif index == 'left':
            return System.Drawing.Color.DodgerBlue
        elif index == 'right':
            return System.Drawing.Color.Plum
        elif index == 'front':
            return System.Drawing.Color.Orange
        elif index == 'back':
            return System.Drawing.Color.OrangeRed

class Shape(Drawable):
    def __init__(self, poly=None, height=None, scope=None, pivot=None):
        #super(ExtrBlock, self).__init__()

        self.name = ''
        self.base = poly
        self._init_height = height
        self._init_pivot = pivot
        self.topo = None
        self.visible = True
        self.visible_topo=True
        self.scope = scope

        # topology
        self.sides = None
        self.topo = None

        # representations
        self.representations = dict(mesh=None, brep=None, visible=True)
        # source is the rhino object id
        # where this extrusion in created from
        self.source_id = None

        # makeform
        if self.base:
            self.make_topology()
            if self.scope is None:
                self.make_scope()

    # properties
    @property
    def height(self):
        if self.scope:
            return self.scope.size[2]
        return self._init_height

    @property
    def vects(self):
        if self.scope:
            if self.scope.pivot:
                return self.scope.pivot.vects
        if self._init_pivot:
            return self._init_pivot.vects

    @property
    def position(self):
        return self.scope.pivot.pos

    @property
    def size(self):
        return self.scope.size

    def set_scope(self, scope):
        self.scope = scope
        # if reset scope, do we have to remake the topology?
        # self.make_topology()

    def scale(self,scalevect):
        print('ExtrBlock.scale({})'.format(str(scalevect)))
        #TODO: implement scale
        pass

    def turn(self):
        print('ExtrBlock.turn()')
        if self.scope:
            self.scope.turn()
        else:
            print('scope not found in ExtrBlock.turn()')

    def rotate(self, degree):
        # TODO: implement rotate
        print('ExtrBlock.rotate({})'.format(degree))
        self.scope.rotate(degree)
        radian = math.radians(degree)
        tr = Transform.Rotation(radian, self.position)
        self.base.Transform(tr)
        self.make_topology()

    def _extrude_from_base(self):
        base = self.base
        pts = rhgt.curve_points(base)
        sides = rhgt.extrude_points_to_mesh(pts, self.height, cap=False)
        self.sides = sides
        self.make_topology()

    def determine_topology(self):
        pass

    def make_scope(self):
        if self.representations['mesh']:
            if self._init_pivot:
                pivot=self._init_pivot
                bplane=Plane(pivot.pos,pivot.vects[0],pivot.vects[1])
            else:
                bplane=rs.WorldXYPlane()
            bbox=rs.BoundingBox(self.representations['mesh'],bplane)
            scope = Scope.create_from_bbox(bbox)
            self.scope = scope
        pass

    def make_topology(self):
        # if self.scope is None:
        #     print('Scope is not set for this extrusion')
        #     raise SyntaxError
        base = self.base
        pts = rhgt.curve_points(base)
        self.representations['mesh']=Mesh()

        # make top and bottom
        bottompl = Polyline(pts)
        bottom = Mesh.CreateFromClosedPolyline(bottompl)
        top = Mesh.CreateFromClosedPolyline(bottompl)
        top.Translate(0, 0, self.height)

        self.topo = Topology()
        self.topo.bot = bottom
        self.topo.top = top
        self.representations['mesh'].Append(top)
        self.representations['mesh'].Append(bottom)
        # make sides
        for i in range(len(pts) - 1):
            vect = pts[i + 1] - pts[i]
            n = Vector3d.CrossProduct(vect, Vector3d(0, 0, 1))
            n = rs.VectorUnitize(n)
            ns_dot = rs.VectorDotProduct(n, self.vects[1])
            ew_dot = rs.VectorDotProduct(n, self.vects[0])
            threshold = 0.7
            side = 'front'
            if ns_dot <= -threshold:
                side = 'front'
            elif ns_dot >= threshold:
                side = 'back'
            elif ew_dot < -threshold:
                side = 'left'
            else:
                side = 'right'

            # TODO:test how to determin direction from dot product
            # rs.AddTextDot(side,(pts[i]+pts[i+1])/2)

            # create face
            #print('self.height=', self.height)
            extr = Vector3d(0, 0, self.height)
            face = Mesh()
            face.Vertices.Add(pts[i])
            face.Vertices.Add(pts[i + 1])
            face.Vertices.Add(pts[i + 1] + extr)
            face.Vertices.Add(pts[i] + extr)
            face.Faces.AddFace(0, 1, 2, 3)

            # add to defined side
            self.topo[side].Append(face)
            self.representations['mesh'].Append(face)

        # Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(self.topo.front)
        # Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(self.topo.top)

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
        #base = rhgt.get_poly_from_crv(base)

        if base:
            height = scope.size[2]
            extr = ExtrBlock(base, scope=scope)
            extr.representations['brep'] = brep
            extr.source_id = brepid
            return extr
        return None

    def _split_dir_amp(self, dir=0, amp=1):
        if self.scope is None:
            print('scope is not set for', self)
            raise SyntaxError
        # split the geometry and reset the scope
        # split the geometry
        #poly=rhgt.get_poly_from_crv(self.base)
        pts=rhgt.curve_points(self.base)

        if dir == 2:
            # z trim is treated differently
            # TODO: implement vertical split
            pass

        else:
            #leaving dir == 0 or 1
            trim_pos = self.position + (self.vects[dir] * amp)
            if dir == 0:
                trim_vect = self.vects[1] * -1
            else:
                trim_vect = self.vects[0]
            trim_plane=Plane(trim_pos,trim_vect, Vector3d(0,0,1))
            close_base = rhgt.trim_poly_by_plane(pts,trim_plane,reverse=True)
            far_base = rhgt.trim_poly_by_plane(pts, trim_plane, reverse=False)
            ShapeType=type(self)

            if close_base:
                #close=ExtrBlock(close_base,self.height, pivot=self.scope.pivot)
                #close = Shape(close_base, self.height, pivot=self.scope.pivot)
                close=ShapeType(close_base, self.height, pivot=self.scope.pivot)
            else:
                close=None
            if far_base:
                #far = ExtrBlock(far_base, self.height, pivot=self.scope.pivot)
                far = ShapeType(far_base, self.height, pivot=self.scope.pivot)
            else:
                far=None
            return (close,far)

        # TODO: fix bug, id split at exact amptitude
    pass

