from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# Create metadata with schema naming convention
metadata = MetaData(schema="app")

# Create Base with schema explicitly set to 'app'
Base = declarative_base(metadata=metadata)
