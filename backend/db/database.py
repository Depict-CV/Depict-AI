from sqlmodel import SQLModel, create_engine

# SQLite in-memory (for quick test) or file-based
DATABASE_URL = "sqlite:///./mydatabase.db"
# DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/mydb" # todo setup PostgresSQL instead of sqlite

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    # create tables
    SQLModel.metadata.create_all(engine)
