from typing import Any


class SchemaValidationError(ValueError):
	"""Raised when a value does not conform to its JSON schema."""


def _matches_type(value: Any, expected_type: str) -> bool:
	if expected_type == "array":
		return isinstance(value, list)
	if expected_type == "boolean":
		return isinstance(value, bool)
	if expected_type == "integer":
		return isinstance(value, int) and not isinstance(value, bool)
	if expected_type == "null":
		return value is None
	if expected_type == "number":
		return isinstance(value, (int, float)) and not isinstance(value, bool)
	if expected_type == "object":
		return isinstance(value, dict)
	if expected_type == "string":
		return isinstance(value, str)
	return False


def validar_conforme_schema(
	value: Any,
	schema: dict[str, Any],
	path: str = "diagnostico",
) -> None:
	if not isinstance(schema, dict):
		raise SchemaValidationError(f"Schema inválido em '{path}'.")

	expected_type = schema.get("type")
	if expected_type is not None:
		expected_types = (
			expected_type if isinstance(expected_type, list) else [expected_type]
		)
		if not all(isinstance(item, str) for item in expected_types):
			raise SchemaValidationError(f"Tipos inválidos no schema de '{path}'.")
		if not any(_matches_type(value, item) for item in expected_types):
			raise SchemaValidationError(
				f"O campo '{path}' deve ser do tipo {expected_type}."
			)

	if "enum" in schema:
		allowed_values = schema["enum"]
		if not isinstance(allowed_values, list):
			raise SchemaValidationError(f"Enum inválido no schema de '{path}'.")
		if value not in allowed_values:
			raise SchemaValidationError(
				f"O campo '{path}' possui um valor não permitido."
			)

	if isinstance(value, dict):
		properties = schema.get("properties", {})
		required = schema.get("required", [])

		if not isinstance(properties, dict):
			raise SchemaValidationError(f"Propriedades inválidas no schema de '{path}'.")
		if not isinstance(required, list) or not all(
			isinstance(field, str) for field in required
		):
			raise SchemaValidationError(f"Required inválido no schema de '{path}'.")

		missing_fields = set(required) - value.keys()
		if missing_fields:
			raise SchemaValidationError(
				f"Campos obrigatórios ausentes em '{path}': "
				+ ", ".join(sorted(missing_fields))
			)

		additional_properties = schema.get("additionalProperties", True)
		for field, field_value in value.items():
			field_schema = properties.get(field)
			field_path = f"{path}.{field}"
			if field_schema is not None:
				validar_conforme_schema(field_value, field_schema, field_path)
			elif additional_properties is False:
				raise SchemaValidationError(
					f"Propriedade não permitida em '{path}': '{field}'."
				)
			elif isinstance(additional_properties, dict):
				validar_conforme_schema(
					field_value,
					additional_properties,
					field_path,
				)
			elif not isinstance(additional_properties, bool):
				raise SchemaValidationError(
					f"additionalProperties inválido no schema de '{path}'."
				)

	if isinstance(value, list) and "items" in schema:
		item_schema = schema["items"]
		if not isinstance(item_schema, dict):
			raise SchemaValidationError(f"Items inválido no schema de '{path}'.")
		for index, item in enumerate(value):
			validar_conforme_schema(item, item_schema, f"{path}[{index}]")
