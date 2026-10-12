import gzip
import importlib.util
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("boundary", ROOT / "scripts/check-linux-boundary.py")
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)


def zip_bytes(name, content):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr(name, content)
    return output.getvalue()


class LinuxBoundaryTests(unittest.TestCase):
    def test_ignore_rules_cover_accidental_apple_files_and_reference_cache(self):
        paths = ["Main.swift", "nested/MAIN.SWIFT", "Demo.xcodeproj/project.pbxproj",
                 "Demo.xcworkspace/contents.xcworkspacedata", "Icons.xcassets/Contents.json",
                 ".swiftpm/configuration.json", "Package.resolved", "Window.storyboard",
                 "reference/sources/reference.tar.gz", "reference/capture/new-file.txt",
                 ".cache/reference-sources/reference.tar.gz"]
        result = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=ROOT,
                                input="\n".join(paths) + "\n", text=True, capture_output=True, check=True)
        self.assertEqual(set(result.stdout.splitlines()), set(paths))

    def test_forced_add_is_rejected_from_index_even_if_working_file_changes(self):
        with tempfile.TemporaryDirectory() as clean:
            root = Path(clean)
            subprocess.run(["git", "init", "-q", root], check=True)
            (root / ".gitignore").write_text("*.swift\n")
            (root / "Main.swift").write_bytes(b"fixture")
            subprocess.run(["git", "add", "-f", "Main.swift"], cwd=root, check=True)
            (root / "Main.swift").unlink()
            self.assertTrue(boundary.check_index(root))

    def test_tar_and_zip_reject_swift_and_apple_projects(self):
        for name in ["Sources/Main.swift", "Sources/MAIN.SWIFT", "Project.xcodeproj/project.pbxproj",
                     "Package.resolved"]:
            with self.subTest(name=name):
                self.assertTrue(boundary.inspect_payload("disguised.dat", zip_bytes(name, b"fixture")))
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w:gz") as archive:
            member = tarfile.TarInfo("Sources/Main.swift")
            member.size = 7
            archive.addfile(member, io.BytesIO(b"fixture"))
        self.assertTrue(boundary.inspect_payload("reference.tar.gz", output.getvalue()))

    def test_nested_and_single_file_compression_are_inspected(self):
        nested = zip_bytes("inner.bin", zip_bytes("Main.swift", b"fixture"))
        self.assertTrue(boundary.inspect_payload("outer.bin", nested))
        self.assertTrue(boundary.inspect_payload("Main.swift.gz", gzip.compress(b"fixture")))

    def test_linux_archives_pass_and_uninspectable_archives_fail(self):
        self.assertEqual(boundary.inspect_payload("linux.zip", zip_bytes("src/main.cpp", b"fixture")), [])
        self.assertTrue(boundary.inspect_payload("unknown.7z", b"fixture"))


if __name__ == "__main__":
    unittest.main()
