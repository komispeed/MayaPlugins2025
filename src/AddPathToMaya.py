import sys

prjPath = "C:/ercano/Desktop/MayaPlugins2025-master/src"
moduleDir = "C:/ercano"
if prjPath not in sys.path:
    sys.path.append(prjPath)
print("adding path")