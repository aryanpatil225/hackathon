from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import SeedResponse
from seed import seed_database

router = APIRouter(prefix="/api", tags=["seed"])


@router.post("/seed", response_model=SeedResponse)
def seed_endpoint(db: Session = Depends(get_db)):
    """Seed the database with sample rules."""
    rules_created = seed_database(db)
    return SeedResponse(
        message="Database seeded successfully",
        rules_created=rules_created,
    )
