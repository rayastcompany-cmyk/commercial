from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"
for d in (DATA_DIR, IMAGES_DIR, OUTPUT_DIR, TEMPLATES_DIR):
    d.mkdir(exist_ok=True, parents=True)
DB_PATH = DATA_DIR / "commercial.db"

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db():
    import models as m
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        if not session.query(m.User).first():
            session.add(m.User(username="admin", password=m.hash_pw("admin"), role="Admin",
                                full_name="مدیر سیستم"))
        if not session.query(m.MyCompany).first():
            session.add(m.MyCompany(id=1, name="نام شرکت من"))
        session.commit()
    finally:
        session.close()
