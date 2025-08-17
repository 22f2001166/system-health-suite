import os, csv, io
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Machine, Report
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

DB_URL = os.getenv("DB_URL", "sqlite:///./syshealth.db")
API_KEY = os.getenv("API_KEY", "DEV_AGENT_KEY")
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_auth(req: Request):
    auth = req.headers.get("authorization", "")
    if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


class IngestPayload(BaseModel):
    machine_id: str
    hostname: str
    os: dict
    checks: dict
    issues: dict
    timestamp: str


@app.post("/ingest")
def ingest(p: IngestPayload, db: Session = Depends(get_db), _=Depends(require_auth)):
    m = db.query(Machine).filter_by(machine_id=p.machine_id).first()
    if not m:
        m = Machine(
            machine_id=p.machine_id,
            hostname=p.hostname,
            os_system=p.os.get("system"),
            os_release=p.os.get("release"),
            os_version=p.os.get("version"),
            architecture=p.os.get("architecture"),
        )
        db.add(m)
        db.flush()
    else:
        m.hostname = p.hostname
        m.os_system = p.os.get("system")
        m.os_release = p.os.get("release")
        m.os_version = p.os.get("version")
        m.architecture = p.os.get("architecture")
    r = Report(machine=m, checks=p.checks, issues=p.issues)
    db.add(r)
    db.commit()
    return {"ok": True}


@app.get("/machines")
def machines(
    os: str | None = None,
    issue: str | None = None,
    q: str | None = None,
    sort_by: str | None = None,
    order: str = "asc",
    db: Session = Depends(get_db),
):
    data = []
    for m in db.query(Machine).all():
        latest = (
            db.query(Report)
            .filter_by(machine_id_fk=m.id)
            .order_by(desc(Report.created_at))
            .first()
        )
        if not latest:
            continue
        if os and (m.os_system or "").lower() != os.lower():
            continue
        if issue and not (latest.issues or {}).get(issue, False):
            continue
        if q and q.lower() not in (m.hostname or "").lower():
            continue
        data.append(
            {
                "machine_id": m.machine_id,
                "hostname": m.hostname,
                "os": {
                    "system": m.os_system,
                    "release": m.os_release,
                    "version": m.os_version,
                    "arch": m.architecture,
                },
                "issues": latest.issues,
                "checks": latest.checks,
                "last_check_in": latest.created_at.isoformat(),
            }
        )

    # Sorting logic
    if sort_by:
        reverse = order == "desc"
        if sort_by == "hostname":
            data.sort(key=lambda x: x["hostname"] or "", reverse=reverse)
        elif sort_by == "os":
            data.sort(key=lambda x: (x["os"]["system"] or ""), reverse=reverse)
        elif sort_by == "last_check_in":
            data.sort(key=lambda x: x["last_check_in"], reverse=reverse)

    return {"items": data, "count": len(data)}


@app.get("/machines.csv")
def machines_csv(
    os: str | None = None,
    issue: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(
        [
            "machine_id",
            "hostname",
            "os",
            "unencrypted_disk",
            "outdated_os",
            "no_antivirus",
            "idle_sleep_too_high",
            "last_check_in",
        ]
    )

    for m in db.query(Machine).all():
        latest = (
            db.query(Report)
            .filter_by(machine_id_fk=m.id)
            .order_by(desc(Report.created_at))
            .first()
        )
        if not latest:
            continue
        if os and (m.os_system or "").lower() != os.lower():
            continue
        if issue and not (latest.issues or {}).get(issue, False):
            continue
        if q and q.lower() not in (m.hostname or "").lower():
            continue
        i = latest.issues or {}
        w.writerow(
            [
                m.machine_id,
                m.hostname,
                m.os_system,
                i.get("unencrypted_disk"),
                i.get("outdated_os"),
                i.get("no_antivirus"),
                i.get("idle_sleep_too_high"),
                latest.created_at,
            ]
        )

    out.seek(0)
    headers = {"Content-Disposition": "attachment; filename=machines.csv"}
    return StreamingResponse(
        iter([out.getvalue()]), media_type="text/csv", headers=headers
    )
