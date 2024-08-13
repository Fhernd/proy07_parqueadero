import json
from sqlalchemy.inspection import inspect
from datetime import datetime

def to_json(instance):
    """
    Convert a SQLAlchemy model instance to a JSON string, including only the model's own attributes.

    :param instance: The SQLAlchemy model instance to convert to a JSON string.

    :return: A JSON string representing the model instance.
    """
    if instance is None:
        return None
    
    # Get the class of the instance
    cls = type(instance)
    
    # Get the mapper for the class
    mapper = inspect(cls)
    
    # Initialize a dictionary to hold the instance's data
    instance_dict = {}
    
    # Iterate over the columns in the model's mapper
    for column in mapper.columns:
        # Get the column name
        column_name = column.name
        
        # Get the column value from the instance
        value = getattr(instance, column_name)
        
        # Convert datetime objects to ISO 8601 strings
        if isinstance(value, datetime):
            value = value.isoformat()
        
        # Add the column name and value to the dictionary
        instance_dict[column_name] = value
    
    # Convert the dictionary to a JSON string
    return json.dumps(instance_dict, ensure_ascii=False)
