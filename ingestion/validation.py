from typing import Any
import jsonschema
import logging

logger = logging.getLogger(__name__)

class SchemaValidator:
    def __init__(self, schema: dict):
        self.schema = schema
    
    def validate(self, record: dict) -> tuple[bool, list[str]]:
        """Returns (is_valid, error_messages)"""
        try:
            jsonschema.validate(instance=record, schema=self.schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [e.message]
        except jsonschema.SchemaError as e:
            logger.error(f"Invalid schema: {e}")
            return False, [str(e)]

class MultiSchemaValidator:
    """Validate against multiple schemas (e.g., for different source types)"""
    def __init__(self):
        self.validators: dict[str, SchemaValidator] = {}
    
    def add_schema(self, name: str, schema: dict) -> None:
        self.validators[name] = SchemaValidator(schema)
    
    def validate(self, record: dict, schema_name: str) -> tuple[bool, list[str]]:
        validator = self.validators.get(schema_name)
        if not validator:
            logger.warning(f"No validator for schema: {schema_name}, skipping validation")
            return True, []
        return validator.validate(record)