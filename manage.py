#!/usr/bin/env python3
import typer
import uvicorn
from subprocess import call

from app.auth.utils import superadmincreation

app = typer.Typer()
migrate_app = typer.Typer()

app.add_typer(migrate_app, name="migrate")


import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)


# ==========================================================
# RUN FASTAPI SERVER  (like: python manage.py runserver)
# ==========================================================

@app.command()
def runserver(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = True
):
    """Run FastAPI server."""
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )

@app.command()
def createsuperuser():
    """Create a super admin user (Django-style)."""
    superadmincreation()




# ==========================================================
# MAKEMIGRATIONS  (Django-like)
# ==========================================================
@app.command()
def makemigrations(m: str = "auto commit"):
    """
    Auto-generate Alembic migration like Django's makemigrations.
    """
    typer.echo("Generating migration…")
    call(["alembic", "revision", "--autogenerate", "-m", m])


# ==========================================================
# MIGRATE  (Django-like)
# ==========================================================
@migrate_app.command("apply")
def migrate_apply():
    """
    Apply all pending migrations (like: python manage.py migrate)
    """
    typer.echo("Applying migrations…")
    call(["alembic", "upgrade", "head"])


# ==========================================================
# ROLLBACK (Optional)
# ==========================================================
@migrate_app.command("rollback")
def migrate_rollback(steps: int = 1):
    """
    Roll back the last migration.
    Equivalent to Django's migrate <previous>
    """
    revision = f"-{steps}"
    typer.echo(f"Rolling back last {steps} migration(s) …")
    call(["alembic", "downgrade", revision])


if __name__ == "__main__":
    app()
