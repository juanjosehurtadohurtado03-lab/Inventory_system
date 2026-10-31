from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models import product
from app.models import sale
from app.models import sale_details
from app.models import employee
