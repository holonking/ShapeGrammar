import Rhino
from Rhino.Geometry import *
import rhinoscriptsyntax as rs
#point operations

def is_point_on_plane_top(pt, plane, reverse=False):
    testVect = plane.XAxis
    if plane.XAxis.Z != 0:
        testVect = plane.YAxis

    pp1 = plane.Origin
    pp2 = pp1 + testVect

    v1 = pp1 - pt
    v2 = pp2 - pt
    n = rs.VectorCrossProduct(v1, v2)
    flag = n.Z > 0
    if reverse:
        return not flag
    return flag

def get_split_point(p1,p2,plane):
    line=LineCurve(p1,p2)
    arrx=Rhino.Geometry.Intersect.Intersection.CurvePlane(line,plane,0.001)
    if arrx:
        return arrx[0].PointA
    return None

def curve_points(curve):
    nc = curve.ToNurbsCurve()
    if nc is None: return None
    points = [nc.Points[i].Location for i in range(nc.Points.Count)]
    return points

def trim_poly_by_plane(poly_pts,plane,reverse=False):
    left=[]
    pts=poly_pts
    last_side=''
    for i in range(len(pts)):
        p=pts[i]
        if is_point_on_plane_top(p,plane,reverse):
            if last_side == 'right':
                np = get_split_point(p,pts[i-1],plane)
                if np:
                    left.append(np)
            left.append(p)
            last_side = 'left'
        else:
            if last_side == 'left':
                np = get_split_point(p,pts[i-1],plane)
                if np:
                    left.append(np)
            last_side='right'
    if len(left) < 1:
        return None
    if left[-1].DistanceTo(left[0])<0.01:
        left=left[:-1]
    left.append(left[0])
    return Polyline(left)

def extrude_points_to_mesh(pts,height,uvect=None,cap=False,join=True):
    if not uvect:
        uvect=Vector3d(0,0,1)
    extr=uvect*height
    out_mesh=Mesh()
    out_disjoined_mesh=[]
    for i in range(len(pts)-1):
        face=Mesh()
        face.Vertices.Add(pts[i])
        face.Vertices.Add(pts[i+1])
        face.Vertices.Add(pts[i+1] + extr)
        face.Vertices.Add(pts[i] + extr)
        face.Faces.AddFace(0,1,2,3)
        out_disjoined_mesh.append(face)
        if join:
            out_mesh.append(face)

    if cap:
        bottompl=Polyline(pts)
        bottom=Mesh.CreateFromClosedPolyline(bottompl)
        top=Mesh.CreateFromClosedPolyline(bottompl)
        top.translate(0,0,height)
        out_disjoined_mesh.append(bottom)
        out_disjoined_mesh.append(top)
        if join:
            out_mesh.append(bottom)
            out_mesh.append(top)
    if join:
        return out_mesh
    return out_disjoined_mesh

#breap operations
def get_brep_bottom_boundary(brep):
    boundaries = []
    #iterate each face
    for bFace in brep.Faces:
        bEdges = bFace.AdjacentEdges()
        crvs = []
        flat = True
        #iterate each edge
        for bEdgei in bEdges:
            edge = brep.Edges[bEdgei]
            if abs(edge.PointAtStart.Z - edge.PointAtEnd.Z) > 0.001:
                flat = False
                break
            crv = edge.DuplicateCurve()
            crvs.append(crv)
        if flat:
            boundary = Rhino.Geometry.Curve.JoinCurves(crvs)
            boundaries += boundary

    if len(boundaries) == 2:
        if boundaries[0].PointAtEnd.Z < boundaries[1].PointAtEnd.Z:
            base = boundaries[0]
        else:
            base = boundaries[1]
        return base
    return None

def get_poly_from_crv(crv):
    pts=curve_points(crv)
    poly=Rhino.Geometry.Polyline(pts)
    return poly
