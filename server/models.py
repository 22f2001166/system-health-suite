from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True)
    machine_id = Column(String, unique=True, index=True, nullable=False)
    hostname = Column(String, index=True)
    os_system = Column(String, index=True)
    os_release = Column(String)
    os_version = Column(String)
    architecture = Column(String)
    reports = relationship(
        "Report", back_populates="machine", cascade="all, delete-orphan"
    )


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    machine_id_fk = Column(Integer, ForeignKey("machines.id"), index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    checks = Column(JSON)
    issues = Column(JSON)
    machine = relationship("Machine", back_populates="reports")
