import sys
from OCP.XCAFDoc import XCAFDoc_ShapeTool, XCAFDoc_DocumentTool, XCAFDoc_ColorTool
for cls in (XCAFDoc_ShapeTool,):
    print("### ", cls.__name__)
    print([m for m in dir(cls) if not m.startswith("__")])
from OCP.TDF import TDF_Label
print("### TDF_Label"); print([m for m in dir(TDF_Label) if not m.startswith("__")])
from OCP.TCollection import TCollection_ExtendedString
print("### EStr"); print([m for m in dir(TCollection_ExtendedString) if not m.startswith("__")])
