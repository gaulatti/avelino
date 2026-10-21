#!/usr/bin/env python3
"""Run real indexed-search input tests on a private bus and controlled tree."""
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import tempfile
import time


def stop_private_session(group):
    """Reap the owned bus/indexer process group before deleting its files."""
    for termination in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(group, termination)
        except ProcessLookupError:
            return
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                os.killpg(group, 0)
            except ProcessLookupError:
                return
            time.sleep(0.02)
    raise RuntimeError("The private search session did not stop; fixture cleanup is unsafe")


def main():
    arguments = sys.argv[1:]
    unavailable = bool(arguments and arguments[0] == "--no-index")
    if unavailable:
        arguments.pop(0)
    if not arguments:
        raise SystemExit("Pass the search test or installed consumer command")
    # Tracker excludes /tmp even when configured explicitly. Use a new, owned
    # directory without changing HOME or any existing user's index settings.
    with tempfile.TemporaryDirectory(prefix="avelino-search-test-", dir=Path.home()) as temporary:
        root = Path(temporary)
        inside, peer = root / "inside", root / "inside-peer"
        (inside / "nested").mkdir(parents=True)
        peer.mkdir()
        token = "avelinoulnacerulean"
        files = {
            inside / (token + "-name.txt"): "Controlled filename-only match.\n",
            inside / "pine-only.txt": "Controlled content token: " + token + "\n",
            inside / "nested" / (token + "-child.txt"): "Controlled child name.\n",
            inside / (token + "-image.png"): "Controlled filename/type association.\n",
            peer / (token + "-outside.txt"): "Controlled other-root filename.\n",
            peer / "pine-peer.txt": "Controlled outside-folder content token: " + token + "\n",
        }
        for path, text in files.items():
            path.write_text(text)
        environment = dict(os.environ, GSETTINGS_BACKEND="keyfile")
        for key, folder in [("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache"),
                            ("XDG_DATA_HOME", "data")]:
            path = root / folder
            path.mkdir(mode=0o700)
            environment[key] = str(path)
        # Keep the compositor/accessibility runtime supplied by a GUI session.
        # Private configuration/cache/data and the private bus isolate indexing.
        runtime = environment.get("XDG_RUNTIME_DIR")
        if runtime:
            if not Path(runtime).is_dir():
                raise SystemExit("The supplied GUI runtime directory does not exist")
        else:
            path = root / "runtime"
            path.mkdir(mode=0o700)
            environment["XDG_RUNTIME_DIR"] = str(path)
        schema = "org.freedesktop.Tracker3.Miner.Files"
        for key, value in [("index-recursive-directories", json.dumps([str(inside), str(peer)])),
                           ("index-single-directories", "[]"), ("initial-sleep", "0")]:
            subprocess.run(["gsettings", "set", schema, key, value], env=environment, check=True)
        bus = ["dbus-run-session"]
        if unavailable:
            # An ordinary private session bus with no activation directories.
            # This tests a missing provider, rather than substituting fake data.
            configuration = root / "no-index.conf"
            configuration.write_text('''<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig><type>session</type><listen>unix:tmpdir=/tmp</listen><auth>EXTERNAL</auth>
<policy context="default"><allow send_destination="*"/><allow receive_sender="*"/><allow own="*"/></policy>
</busconfig>
''')
            bus += ["--config-file", str(configuration)]
            arguments += ["--file-input-search-no-index"]
        command = bus + ["--"] + arguments + ["--file-input-search-root", str(inside)]
        print(json.dumps({"fixture": str(inside), "peer": str(peer), "providerUnavailable": unavailable,
                          "privateIndexConfiguration": True, "hostIndexSettingsChanged": False}), flush=True)
        # Activated miners inherit this new process group. The bus can finish
        # before they do, so wait for this group rather than deleting a live
        # database or terminating other sessions' Tracker processes.
        process = subprocess.Popen(command, env=environment, start_new_session=True)
        try:
            result = process.wait()
        finally:
            stop_private_session(process.pid)
            process.wait()
        print(json.dumps({"privateSessionStopped": True, "clientExitCode": result}), flush=True)
        return result


if __name__ == "__main__":
    raise SystemExit(main())
