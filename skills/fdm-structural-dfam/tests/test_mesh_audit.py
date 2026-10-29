import importlib.util
from pathlib import Path
import tempfile
import unittest
import numpy as np
import trimesh

SCRIPT = Path(__file__).resolve().parents[1]/'scripts'/'mesh_audit.py'
spec = importlib.util.spec_from_file_location('mesh_audit', SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class MeshAuditTests(unittest.TestCase):
    def test_closed_box(self):
        result=audit.audit_mesh(trimesh.creation.box(extents=(10,20,30)), 'mm')
        self.assertEqual(result['status'], 'geometry_screened')
        self.assertEqual(result['structural_validation'], 'not_performed')
        self.assertAlmostEqual(result['signed_volume_mm3'], 6000)

    def test_open_box_is_not_screened(self):
        mesh=trimesh.creation.box()
        mesh.update_faces(np.arange(len(mesh.faces)-1))
        self.assertEqual(audit.audit_mesh(mesh,'mm')['status'],'geometry_issues')

    def test_unit_conversion(self):
        result=audit.audit_mesh(trimesh.creation.box(extents=(1,2,3)), 'cm')
        np.testing.assert_allclose(result['extents_mm'],[10,20,30])

    def test_scene_rejected(self):
        with self.assertRaises(ValueError):
            audit.audit_mesh(trimesh.Scene(), 'mm')

    def test_nan_rejected(self):
        mesh=trimesh.creation.box()
        mesh.vertices[0,0]=np.nan
        with self.assertRaises(ValueError):
            audit.audit_mesh(mesh, 'mm')

    def test_bad_units(self):
        with self.assertRaises(ValueError):
            audit.audit_mesh(trimesh.creation.box(), 'unknown')

    def test_inverted_volume(self):
        mesh=trimesh.creation.box()
        mesh.invert()
        result=audit.audit_mesh(mesh,'mm')
        self.assertIn('nonpositive_signed_volume',result['issues'])

    def test_original_is_unchanged(self):
        mesh=trimesh.creation.box()
        old=mesh.vertices.copy()
        audit.audit_mesh(mesh,'m')
        np.testing.assert_array_equal(mesh.vertices,old)

    def test_stl_cli(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'box.stl'
            output=Path(d)/'report.json'
            trimesh.creation.box().export(source)
            code=audit.main([str(source),'--units','mm','--json',str(output)])
            self.assertEqual(code,0)
            self.assertIn('not_performed', output.read_text())

    def test_no_overwrite_source(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'box.stl'
            trimesh.creation.box().export(source)
            original=source.read_bytes()
            code=audit.main([str(source),'--units','mm','--json',str(source)])
            self.assertEqual(code,2)
            self.assertEqual(source.read_bytes(),original)

if __name__=='__main__':
    unittest.main()
