import trimesh
import numpy as np

# Create a simple test mesh
vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
faces = np.array([[0, 1, 2]])
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

print("Testing available export formats...")

# Test the formats that are claimed to be supported in the app
test_formats = ['obj', 'stl', 'ply', 'dae', 'gltf', 'glb', 'off']

for fmt in test_formats:
    try:
        # Try to export to this format
        result = mesh.export(file_type=fmt)
        print(f"✓ {fmt.upper()} - SUPPORTED")
    except Exception as e:
        print(f"✗ {fmt.upper()} - NOT SUPPORTED: {str(e)}")

print("\nTesting mesh.export() method...")
try:
    # Check what methods are available
    print("Available methods:", [m for m in dir(mesh) if 'export' in m.lower()])
except Exception as e:
    print(f"Error: {e}")

print("\nChecking trimesh supported formats...")
try:
    # Check what formats trimesh claims to support
    print("Trimesh supported formats:", trimesh.available_formats())
except Exception as e:
    print(f"Error getting available formats: {e}") 