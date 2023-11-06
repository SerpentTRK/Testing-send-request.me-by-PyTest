ApiCompanies_200 = {
"type": "object",
  "properties": {
    "data": {
      "type": "array",
      "items":
        {
          "type": "object",
          "properties": {
              "company_id": {"type": "integer"},
              "company_name": {"type": "string"},
              "company_address": {"type": "string"},
              "company_status": {"type": "string", "enum": ["ACTIVE", "CLOSED", "BANKRUPT"]},
          },
          "required": ["company_id", "company_name", "company_address", "company_status"]
        }
    },
    "meta": {
      "type": "object",
      "properties": {
        "total": {"type": "integer"}
      },
      "required": ["total"]
    }
  },
  "required": ["data", "meta"]
}