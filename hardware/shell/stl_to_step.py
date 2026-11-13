# Convert an STL to STEP with FreeCAD (run with FreeCADCmd): stl_to_step.py in.stl out.step
import sys, Mesh, Part
src, out = sys.argv[-2], sys.argv[-1]
mesh = Mesh.Mesh(src)
shape = Part.Shape()
shape.makeShapeFromMesh(mesh.Topology, 0.05)
solid = Part.makeSolid(Part.Shell(shape.Faces).removeSplitter()) if shape.Faces else shape
solid.exportStep(out)
print("wrote", out, "faces", len(solid.Faces), "volume", round(solid.Volume, 1))
