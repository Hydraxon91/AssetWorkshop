#!/usr/bin/env python3
"""Run an approved script in an owned, time-limited disposable Blender process."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

from mesh_preflight import validate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def terminate_owned(child):
    """Terminate the owned process tree.

    Windows has no os.killpg/SIGKILL, so the tree is removed with taskkill.
    Only the PID created above is ever targeted, never the interactive Blender.
    """
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(child.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        os.killpg(child.pid, signal.SIGKILL)


def run(args):
    # Refuse reuse so failures and baselines cannot be silently overwritten.
    directory = Path(args.run_dir).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    report = {"status": "preparing", "started_at": datetime.now(timezone.utc).isoformat(),
              "script_sha256": None, "process_exit_code": None,
              "geometry_verified": False, "shape_accepted": False,
              "integration_authorized": False}
    start = time.monotonic()
    child = None
    try:
        source = Path(args.script).read_bytes()
        script = directory / "construction.py"
        script.write_bytes(source)
        mesh = directory / "mesh.json"
        mesh.write_bytes(Path(args.mesh).read_bytes())
        report.update(script_sha256=digest(script), mesh_sha256=digest(mesh))
        report["preflight"] = validate(json.loads(mesh.read_text()), closed=not args.allow_boundary)
        if not report["preflight"]["passed"]:
            report["status"] = "preflight_failed"
            return 2
        command = [str(Path(args.blender).resolve()), "--background", "--factory-startup",
                   "--disable-autoexec", "--threads", str(args.threads),
                   "--python-exit-code", "1", "--python", str(script), "--", str(mesh)]
        report["command"] = command
        with (directory / "stdout.log").open("wb") as stdout, (directory / "stderr.log").open("wb") as stderr:
            child = subprocess.Popen(command, cwd=directory, stdout=stdout, stderr=stderr,
                                     start_new_session=True)
            report["owned_pid"] = child.pid
            try:
                child.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                report["status"] = "timed_out"
                # Only the process group created above; never the interactive Blender PID.
                terminate_owned(child)
                child.wait()
            report["process_exit_code"] = child.returncode
        if report["status"] != "timed_out":
            report["status"] = "process_completed" if child.returncode == 0 else "process_failed"
        return 0 if report["status"] == "process_completed" else 1
    except KeyboardInterrupt:
        report["status"] = "interrupted"
        return 130
    except Exception as error:
        report.update(status="runner_error", error=str(error))
        return 1
    finally:
        if child is not None:
            # Also remove lingering descendants in this owned group after normal exit.
            try:
                terminate_owned(child)
            except ProcessLookupError:
                pass
            child.wait()
        report["elapsed_seconds"] = time.monotonic() - start
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True)
    parser.add_argument("--script", required=True)
    parser.add_argument("--mesh", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--allow-boundary", action="store_true")
    args = parser.parse_args()
    if not 0 < args.timeout <= 120 or not 1 <= args.threads <= 2:
        parser.error("timeout must be >0 and <=120 seconds; threads must be 1 or 2")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
