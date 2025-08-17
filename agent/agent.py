import hashlib, json, os, platform, random, subprocess, sys, time, uuid, pathlib
from datetime import datetime, timezone

CONFIG_PATH = os.environ.get("SYSHEALTH_CONFIG", "config.json")
STATE_DIR = os.path.join(pathlib.Path.home(), ".system-health-agent")
ID_PATH = os.path.join(STATE_DIR, "id")
LAST_HASH_PATH = os.path.join(STATE_DIR, "last_hash")


def read_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def ensure_machine_id():
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(ID_PATH):
        with open(ID_PATH, "w") as f:
            f.write(str(uuid.uuid4()))
    return pathlib.Path(ID_PATH).read_text().strip()


def sh(cmd, shell=True):
    try:
        out = subprocess.check_output(
            cmd, shell=shell, stderr=subprocess.STDOUT, text=True, timeout=30
        )
        return out.strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()
    except Exception as e:
        return f"ERROR: {e}"


def detect_disk_encryption():
    osname = platform.system().lower()
    if "windows" in osname:
        out = sh("manage-bde -status C:")
        encrypted = (
            "Percentage Encrypted: 100%" in out
            or "Conversion Status:    Fully Encrypted" in out
        )
        return {"provider": "BitLocker", "encrypted": encrypted, "raw": out[:1000]}
    if "darwin" in osname:
        out = sh("fdesetup status")
        encrypted = "FileVault is On." in out
        return {"provider": "FileVault", "encrypted": encrypted, "raw": out}
    # linux
    lsblk = sh("lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINT")
    crypttab = os.path.exists("/etc/crypttab") and open("/etc/crypttab").read().strip()
    encrypted = "crypt" in lsblk or (crypttab and len(crypttab) > 0)
    return {"provider": "dm-crypt/LUKS", "encrypted": encrypted, "raw": (lsblk[:600])}


def detect_os_updates():
    osname = platform.system().lower()
    if "windows" in osname:
        ps = r'''powershell -NoProfile -Command "$sess = New-Object -ComObject Microsoft.Update.Session; $searcher=$sess.CreateUpdateSearcher(); $res=$searcher.Search('IsInstalled=0'); $res.Updates.Count"'''
        out = sh(ps)
        try:
            pending = int(out.splitlines()[-1].strip())
        except:
            pending = -1
        return {"pending_updates": pending if pending >= 0 else None, "raw": out}
    if "darwin" in osname:
        out = sh("softwareupdate -l")
        up_to_date = "No new software available." in out
        pending = 0 if up_to_date else max(1, out.count("*"))
        return {"pending_updates": pending, "raw": out[:1000]}
    # linux
    if shutil.which("apt-get"):
        out = sh("apt-get -s upgrade | grep '^Inst ' | wc -l")
        try:
            pending = int(out.strip())
        except:
            pending = None
        return {"pending_updates": pending, "raw": out}
    if shutil.which("dnf"):
        out = sh("dnf -q check-update | wc -l")
        try:
            pending = max(0, int(out.strip()) - 1)
        except:
            pending = None
        return {"pending_updates": pending, "raw": out}
    if shutil.which("pacman"):
        out = sh("pacman -Sup 2>/dev/null | wc -l")
        try:
            pending = int(out.strip())
        except:
            pending = None
        return {"pending_updates": pending, "raw": out}
    return {"pending_updates": None, "raw": "unknown package manager"}


# agent/agent.py (rest)
import shutil, requests


def detect_antivirus():
    osname = platform.system().lower()
    if "windows" in osname:
        ps = r'''powershell -NoProfile -Command "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object -Property displayName,productState"'''
        out = sh(ps)
        enabled = "displayName" in out and len(out.strip()) > 0
        return {"enabled": enabled, "raw": out[:1000]}
    # macOS/Linux stub
    return {"enabled": False, "raw": "Not implemented"}


def detect_sleep_minutes():
    osname = platform.system().lower()
    if "windows" in osname:
        out = sh("powercfg -query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE")
        # parse the AC/DC timeout values if present
        try:
            lines = [line for line in out.splitlines() if "AC Setting Index" in line]
            if lines:
                val = int(lines[0].split()[-1], 16)  # hex to int
                return {"sleep_minutes": val, "raw": out[:1000]}
        except Exception:
            pass
        return {"sleep_minutes": None, "raw": out[:1000]}
    # stub for macOS/Linux
    return {"sleep_minutes": 5, "raw": "not implemented"}


def detect_os():
    system = platform.system()
    release = platform.release()
    version = platform.version()

    # Special case: detect Windows 11 based on build number
    if system == "Windows" and release == "10":
        try:
            build = int(version.split(".")[2])
            if build >= 22000:  # Windows 11 builds start here
                release = "11"
        except Exception:
            pass

    return {
        "system": system,
        "release": release,
        "version": version,
        "architecture": platform.machine(),
    }


def collect_snapshot():
    return {
        "machine_id": ensure_machine_id(),
        "hostname": platform.node(),
        "os": detect_os(),
        "checks": {
            "disk_encryption": detect_disk_encryption(),
            "os_updates": detect_os_updates(),
            "antivirus": detect_antivirus(),
            "sleep": detect_sleep_minutes(),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def payload_hash(payload: dict) -> str:
    h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return h


def load_last_hash():
    if os.path.exists(LAST_HASH_PATH):
        return pathlib.Path(LAST_HASH_PATH).read_text().strip()
    return ""


def save_last_hash(h):
    pathlib.Path(LAST_HASH_PATH).write_text(h)


def post_update(cfg, payload):
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    url = cfg["server_url"].rstrip("/") + "/ingest"
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
    r.raise_for_status()


def main():
    cfg = read_config()
    random.seed()
    while True:
        snap = collect_snapshot()
        # derive "issues" as booleans for quick server/UI flagging
        issues = {
            "unencrypted_disk": not (
                snap["checks"]["disk_encryption"].get("encrypted") is True
            ),
            "outdated_os": (snap["checks"]["os_updates"].get("pending_updates") or 0)
            > 0,
            "no_antivirus": not (snap["checks"]["antivirus"].get("enabled") is True),
            "idle_sleep_too_high": (
                snap["checks"]["sleep"].get("sleep_minutes") or 9999
            )
            > 10,
        }
        snap["issues"] = issues
        h = payload_hash(snap)
        if h != load_last_hash():
            try:
                post_update(cfg, snap)
                save_last_hash(h)
            except Exception as e:
                # swallow errors to keep daemon light
                sys.stderr.write(f"[agent] post failed: {e}\n")
        # jittered sleep
        # mins = random.randint(
        #     cfg.get("interval_min_minutes", 15), cfg.get("interval_max_minutes", 60)
        # )
        mins = 0.1  # 6 seconds

        time.sleep(mins * 60)


if __name__ == "__main__":
    main()
