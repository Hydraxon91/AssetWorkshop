import argparse
import json
import os
from pathlib import Path
import tempfile
import unittest
from mesh_preflight import validate
from run import run


def stub_body(body):
    """cmd.exe has no sleep, so the POSIX stub bodies need a Windows equivalent.

    Only the timeout case needs one: ping is used as a delay because `timeout`
    refuses redirected input, which is how the runner wires the child.
    """
    if os.name != "nt":
        return body
    return body.replace("sleep 10", "ping -n 11 127.0.0.1 >nul")


def mesh():
    return {"vertices": [[0,0,0],[1,0,0],[0,1,0],[0,0,1]],
            "faces": [[0,2,1],[0,1,3],[1,2,3],[2,0,3]]}


class Tests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(validate(mesh())["passed"])

    def test_branching(self):
        m = mesh()
        m["faces"].append(m["faces"][0])
        self.assertFalse(validate(m)["passed"])
        self.assertEqual(validate(m)["branching_edges"], 3)

    def test_invalid(self):
        for index in (-1, 9, True):
            m = mesh()
            m["faces"][0][0] = index
            self.assertFalse(validate(m)["passed"])

    def test_winding(self):
        m = mesh()
        m["faces"][0].reverse()
        self.assertGreater(validate(m)["winding_errors"], 0)

    def test_collapsed_pillar_ring_regression(self):
        # Round33 produced loops [a,b,a] from zero-width index ranges.
        m = {"vertices": [[0,0,0],[1,0,0]], "faces": [[0,1,0]]}
        result = validate(m, closed=False)
        self.assertFalse(result["passed"])
        self.assertIn("Face 0: repeated vertex", result["errors"])

    def test_nonfinite_and_degenerate(self):
        m = mesh()
        m["vertices"][0][0] = float("nan")
        self.assertFalse(validate(m)["passed"])
        m = {"vertices": [[0,0,0],[1,0,0],[2,0,0]], "faces": [[0,1,2]]}
        self.assertFalse(validate(m, closed=False)["passed"])

    def test_loose_and_disconnected(self):
        m = mesh()
        m["vertices"].append([2,2,2])
        self.assertFalse(validate(m)["passed"])
        m = mesh()
        m["vertices"] += [[x+3,y,z] for x,y,z in mesh()["vertices"]]
        m["faces"] += [[i+4 for i in f] for f in mesh()["faces"]]
        self.assertEqual(validate(m)["components"], 2)
        self.assertFalse(validate(m)["passed"])

    def test_budget(self):
        self.assertFalse(validate(mesh(), max_vertices=3)["passed"])

    def test_boundary(self):
        m = {"vertices": [[0,0,0],[1,0,0],[0,1,0]], "faces": [[0,1,2]]}
        self.assertFalse(validate(m)["passed"])
        self.assertTrue(validate(m, closed=False)["passed"])

    def exercise(self, body, invalid=False, timeout=2):
        # Lifecycle stub only: never launches Blender.
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            if os.name == "nt":
                # Windows cannot execute the shebang stub; cmd.exe runs a .bat.
                executable = p / "stub.bat"
                executable.write_text("@echo off\r\n" + stub_body(body) + "\r\n")
            else:
                executable = p / "stub"
                executable.write_text("#!/bin/sh\n" + body + "\n")
                executable.chmod(0o700)
            (p / "input.py").write_text("# reviewed script\n")
            m = mesh()
            if invalid:
                m["faces"].append(m["faces"][0])
            (p / "input.json").write_text(json.dumps(m))
            args = argparse.Namespace(blender=str(executable), script=str(p / "input.py"),
                mesh=str(p / "input.json"), run_dir=str(p / "result"), timeout=timeout,
                threads=1, allow_boundary=False)
            code = run(args)
            result = json.loads((p / "result/report.json").read_text())
            with self.assertRaises(FileExistsError):
                run(args)
            return code, result

    def test_success_not_approval(self):
        code, r = self.exercise("exit 0")
        self.assertEqual(code, 0)
        self.assertEqual(r["status"], "process_completed")
        self.assertFalse(r["geometry_verified"])
        self.assertFalse(r["integration_authorized"])

    def test_failure(self):
        code, r = self.exercise("exit 3")
        self.assertEqual(code, 1)
        self.assertEqual(r["status"], "process_failed")

    def test_timeout(self):
        code, r = self.exercise("sleep 10", timeout=0.05)
        self.assertEqual(code, 1)
        self.assertEqual(r["status"], "timed_out")

    def test_gate(self):
        code, r = self.exercise("exit 99", invalid=True)
        self.assertEqual(code, 2)
        self.assertNotIn("owned_pid", r)


if __name__ == "__main__":
    unittest.main()
