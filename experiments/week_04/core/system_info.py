"""
System information gathering for compiler optimization.

This module detects system properties (OS, CPU, compilers, Rust toolchain)
to help LLMs generate optimized code for the target platform.
"""

import os
import platform
import shutil
import subprocess
from typing import Dict, Any, List


def _run(cmd, timeout=3):
    """Run a command safely. Returns stdout text or ''.
    Accepts either a string (shell) or list (no shell).
    """
    try:
        if isinstance(cmd, str):
            return subprocess.check_output(
                cmd, shell=True, text=True, stderr=subprocess.DEVNULL, timeout=timeout
            ).strip()
        else:
            return subprocess.check_output(
                cmd, shell=False, text=True, stderr=subprocess.DEVNULL, timeout=timeout
            ).strip()
    except Exception:
        return ""


def _first_line(s: str) -> str:
    s = (s or "").strip()
    return s.splitlines()[0].strip() if s else ""


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _bool_from_output(s: str) -> bool:
    return s.strip() in {"1", "true", "True", "YES", "Yes", "yes"}


def retrieve_system_info() -> Dict[str, Any]:
    """
    Returns a compact dict with enough info for an LLM to:
      - Pick an install path (winget/choco/scoop, Homebrew/Xcode CLT, apt/dnf/...),
      - Choose a compiler family (MSVC/clang/gcc),
      - Suggest safe optimization flags (e.g., -O3/-march=native or MSVC /O2),
      - Decide on a build system (cmake+ninja) and parallel -j value.
    """
    sysname = platform.system()
    machine = platform.machine() or ""
    release = platform.release() or ""
    version = platform.version() or ""
    kernel = release if sysname == "Windows" else (_run(["uname", "-r"]) or release)

    distro = {"name": "", "version": ""}
    if sysname == "Linux":
        try:
            with open("/etc/os-release", "r") as f:
                data = {}
                for line in f:
                    if "=" in line:
                        k, v = line.rstrip().split("=", 1)
                        data[k] = v.strip('"')
                distro["name"] = data.get("PRETTY_NAME") or data.get("NAME", "")
                distro["version"] = data.get("VERSION_ID") or data.get("VERSION", "")
        except Exception:
            pass

    wsl = False
    if sysname != "Windows":
        try:
            with open("/proc/version", "r") as f:
                v = f.read().lower()
                wsl = ("microsoft" in v) or ("wsl" in v)
        except Exception:
            wsl = False

    rosetta = False
    if sysname == "Darwin":
        rosetta = _bool_from_output(_run(["sysctl", "-in", "sysctl.proc_translated"]))

    target = ""
    for cc in ("clang", "gcc"):
        if _which(cc):
            out = _run([cc, "-dumpmachine"])
            if out:
                target = _first_line(out)
                break

    pms = []
    if sysname == "Windows":
        for pm in ("winget", "choco", "scoop"):
            if _which(pm):
                pms.append(pm)
    elif sysname == "Darwin":
        if _run(["xcode-select", "-p"]):
            pms.append("xcode-select (CLT)")
        for pm in ("brew", "port"):
            if _which(pm):
                pms.append(pm)
    else:
        for pm in ("apt", "dnf", "yum", "pacman", "zypper", "apk", "emerge"):
            if _which(pm):
                pms.append(pm)

    brand = ""
    if sysname == "Linux":
        brand = _run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    elif sysname == "Darwin":
        brand = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
    elif sysname == "Windows":
        brand = _run('powershell -NoProfile -Command "(Get-CimInstance Win32_Processor).Name"')
        if not brand:
            brand = _run("wmic cpu get Name /value").replace("Name=", "").strip()

    cores_logical = os.cpu_count() or 0
    cores_physical = 0
    if sysname == "Darwin":
        cores_physical = int(_run(["sysctl", "-n", "hw.physicalcpu"]) or "0")
    elif sysname == "Windows":
        cores_physical = int(
            _run('powershell -NoProfile -Command "(Get-CimInstance Win32_Processor).NumberOfCores"')
            or "0"
        )
    elif sysname == "Linux":
        try:
            mapping = _run("LC_ALL=C lscpu -p=CORE,SOCKET | grep -v '^#'").splitlines()
            unique = set(tuple(line.split(",")) for line in mapping if "," in line)
            cores_physical = len(unique) or 0
        except Exception:
            cores_physical = 0

    simd = []
    if sysname == "Linux":
        flags = _run("grep -m1 'flags' /proc/cpuinfo | cut -d: -f2")
        if flags:
            fset = set(flags.upper().split())
            for x in ("AVX512F", "AVX2", "AVX", "FMA", "SSE4_2", "NEON", "SVE"):
                if x in fset:
                    simd.append(x)
    elif sysname == "Darwin":
        feats = (
            (
                _run(["sysctl", "-n", "machdep.cpu.features"])
                + " "
                + _run(["sysctl", "-n", "machdep.cpu.leaf7_features"])
            )
            .upper()
            .split()
        )
        for x in ("AVX512F", "AVX2", "AVX", "FMA", "SSE4_2", "NEON", "SVE"):
            if x in feats:
                simd.append(x)

    def ver_line(exe, args=("--version",)):
        p = _which(exe)
        if not p:
            return ""
        out = _run([p, *args])
        return _first_line(out)

    gcc = ver_line("gcc")
    gpp = ver_line("g++")
    clang = ver_line("clang")

    msvc_cl = ""
    cl_path = _which("cl")
    if cl_path:
        msvc_cl = _first_line(_run("cl 2>&1"))

    cmake = ver_line("cmake")
    ninja = _first_line(_run([_which("ninja"), "--version"])) if _which("ninja") else ""
    make = ver_line("make")
    lld = ver_line("ld.lld")

    return {
        "os": {
            "system": sysname,
            "arch": machine,
            "release": release,
            "version": version,
            "kernel": kernel,
            "distro": distro if sysname == "Linux" else None,
            "wsl": wsl,
            "rosetta2_translated": rosetta,
            "target_triple": target,
        },
        "package_managers": pms,
        "cpu": {
            "brand": brand.strip(),
            "cores_logical": cores_logical,
            "cores_physical": cores_physical,
            "simd": sorted(set(simd)),
        },
        "toolchain": {
            "compilers": {"gcc": gcc, "g++": gpp, "clang": clang, "msvc_cl": msvc_cl},
            "build_tools": {"cmake": cmake, "ninja": ninja, "make": make},
            "linkers": {"ld_lld": lld},
        },
    }


def rust_toolchain_info() -> Dict[str, Any]:
    """
    Return a dict with Rust-related settings:
      - presence and paths for rustc / cargo / rustup / rust-analyzer
      - versions
      - active/default toolchain (if rustup is present)
      - installed targets
      - common env vars (CARGO_HOME, RUSTUP_HOME, RUSTFLAGS, CARGO_BUILD_TARGET)
      - simple execution examples
    """
    info = {
        "installed": False,
        "rustc": {"path": "", "version": "", "host_triple": "", "release": "", "commit_hash": ""},
        "cargo": {"path": "", "version": ""},
        "rustup": {
            "path": "",
            "version": "",
            "active_toolchain": "",
            "default_toolchain": "",
            "toolchains": [],
            "targets_installed": [],
        },
        "rust_analyzer": {"path": ""},
        "env": {
            "CARGO_HOME": os.environ.get("CARGO_HOME", ""),
            "RUSTUP_HOME": os.environ.get("RUSTUP_HOME", ""),
            "RUSTFLAGS": os.environ.get("RUSTFLAGS", ""),
            "CARGO_BUILD_TARGET": os.environ.get("CARGO_BUILD_TARGET", ""),
        },
        "execution_examples": [],
    }

    rustc_path = _which("rustc")
    cargo_path = _which("cargo")
    rustup_path = _which("rustup")
    ra_path = _which("rust-analyzer")

    info["rustc"]["path"] = rustc_path or ""
    info["cargo"]["path"] = cargo_path or ""
    info["rustup"]["path"] = rustup_path or ""
    info["rust_analyzer"]["path"] = ra_path or ""

    if rustc_path:
        ver_line = _first_line(_run([rustc_path, "--version"]))
        info["rustc"]["version"] = ver_line
        verbose = _run([rustc_path, "--version", "--verbose"])
        host = release = commit = ""
        for line in verbose.splitlines():
            if line.startswith("host:"):
                host = line.split(":", 1)[1].strip()
            elif line.startswith("release:"):
                release = line.split(":", 1)[1].strip()
            elif line.startswith("commit-hash:"):
                commit = line.split(":", 1)[1].strip()
        info["rustc"]["host_triple"] = host
        info["rustc"]["release"] = release
        info["rustc"]["commit_hash"] = commit

    if cargo_path:
        info["cargo"]["version"] = _first_line(_run([cargo_path, "--version"]))

    if rustup_path:
        info["rustup"]["version"] = _first_line(_run([rustup_path, "--version"]))
        active = _first_line(_run([rustup_path, "show", "active-toolchain"]))
        info["rustup"]["active_toolchain"] = active

        tlist = _run([rustup_path, "toolchain", "list"]).splitlines()
        info["rustup"]["toolchains"] = [t.strip() for t in tlist if t.strip()]
        default_tc = ""
        for line in tlist:
            if "(default)" in line:
                default_tc = line.strip()
                break
        if not default_tc:
            for line in _run([rustup_path, "show"]).splitlines():
                if "default toolchain:" in line:
                    default_tc = line.split(":", 1)[1].strip()
                    break
        info["rustup"]["default_toolchain"] = default_tc

        targets = _run([rustup_path, "target", "list", "--installed"]).split()
        info["rustup"]["targets_installed"] = targets

    exec_examples = []
    if cargo_path:
        exec_examples.append(f'"{cargo_path}" build')
        exec_examples.append(f'"{cargo_path}" run')
        exec_examples.append(f'"{cargo_path}" test')
    if rustc_path:
        exec_examples.append(f'"{rustc_path}" hello.rs -o hello')
    info["execution_examples"] = exec_examples

    info["installed"] = bool(rustc_path or cargo_path or rustup_path)

    def _maybe_default_home(env_val, default_basename):
        if env_val:
            return env_val
        home = os.path.expanduser("~") or ""
        candidate = os.path.join(home, default_basename) if home else ""
        return candidate if candidate and os.path.isdir(candidate) else ""

    info["env"]["CARGO_HOME"] = _maybe_default_home(info["env"]["CARGO_HOME"], ".cargo")
    info["env"]["RUSTUP_HOME"] = _maybe_default_home(info["env"]["RUSTUP_HOME"], ".rustup")

    return info
