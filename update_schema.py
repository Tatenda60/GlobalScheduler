"""
Script to update the database schema with new columns for the User model
"""
from app import db, app
from models import User, LoanApplication, RiskAssessment
from sqlalchemy import inspect

def add_column(engine, table_name, column):
    """
    Add a column to a table if it doesn't exist
    """
    # Get the inspector
    inspector = inspect(engine)
    
    # Get existing column names
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    
    # Check if the column already exists
    if column.name not in columns:
        # Get the column type
        column_type = column.type.compile(engine.dialect)
        
        # Create the ALTER TABLE statement
        column_name = column.name
        if column.nullable:
            nullable = "NULL"
        else:
            nullable = "NOT NULL"
            
        # Add default value if present
        default = ""
        if column.default is not None:
            if isinstance(column.default.arg, str):
                default = f" DEFAULT '{column.default.arg}'"
            else:
                default = f" DEFAULT {column.default.arg}"
                
        # In PostgreSQL 'user' is a reserved keyword, so we need to quote it
        if table_name == 'user':
            quoted_table_name = '"user"'
        else:
            quoted_table_name = table_name
        
        sql = f"ALTER TABLE {quoted_table_name} ADD COLUMN {column_name} {column_type} {nullable}{default};"
        
        # Execute the ALTER TABLE statement
        with engine.connect() as conn:
            conn.execute(db.text(sql))
            conn.commit()
            print(f"Added column {column_name} to {table_name}")
    else:
        print(f"Column {column.name} already exists in {table_name}")

def update_schema():
    """
    Update the database schema with new columns
    """
    print("Updating database schema...")
    
    # Get the database engine
    engine = db.engine
    
    # Add role column to User model if it doesn't exist
    add_column(engine, 'user', User.__table__.c.role)
    
    # Add is_staff column to User model if it doesn't exist
    add_column(engine, 'user', User.__table__.c.is_staff)
    
    # Add handled_by_id column to LoanApplication if it doesn't exist
    add_column(engine, 'loan_application', LoanApplication.__table__.c.handled_by_id)
    
    # Add handled_at column to LoanApplication if it doesn't exist
    add_column(engine, 'loan_application', LoanApplication.__table__.c.handled_at)
    
    # Add decision_notes column to LoanApplication if it doesn't exist
    add_column(engine, 'loan_application', LoanApplication.__table__.c.decision_notes)
    
    print("Schema update complete!")

if __name__ == "__main__":
    with app.app_context():
        update_schema()