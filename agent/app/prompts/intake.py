INTAKE_SYSTEM_PROMPT = """Extract the user's Chicago day-trip constraints into the provided TripRequest schema. Use null for unknown scalar fields and empty lists for unknown list fields. Never invent facts."""
UPDATE_SYSTEM_PROMPT = """Extract only newly supplied trip information into TripRequestUpdate. Leave unspecified fields null."""
