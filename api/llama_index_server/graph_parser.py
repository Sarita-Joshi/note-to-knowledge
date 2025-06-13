KG_TRIPLET_EXTRACT_TMPL = """
-Goal-
Given a text document, extract up to {max_knowledge_triplets} knowledge triplets, each consisting of two entities and their relationship.
Strictly follow the rules for entity extraction, naming conventions, and relation extraction as outlined below.

-Steps-

Entity Extraction
Identify all entities that participate in meaningful, explicit relationships in the text.
For each entity, extract:
entity_name:
Use the most complete, canonical, and standardized form of the entity name as explicitly mentioned in the text. Always capitalize properly.
Avoid abbreviations, nicknames, or partially mentioned forms.
If the same entity appears in different forms across documents, always use the most descriptive and complete form.
entity_type: Assign a type or class to the entity, using the most accurate and descriptive label based on the text.
The entity type can be any appropriate category or label that fits the entity as described (e.g., "Person", "Company", "Event", "Technology", "Gene", "Chemical", "Time", "Location", "Product", "Concept", etc.).
entity_description:
Provide a concise explanation of the entity’s properties, significance, or role, as directly supported by the text.
Relation Extraction
For each pair of entities identified in Step 1, extract a relationship ONLY if it is clearly and explicitly described in the text.

For each relationship, extract:
source_entity: Use the canonical entity_name from Step 1.
target_entity: Use the canonical entity_name from Step 1.
relation:
Use lowercase snake_case format (e.g., "works_for", "has_award", "produced_by").
Use general, timeless relationships.
Do NOT invent or infer unstated relationships.
relationship_description:
Briefly explain, using evidence from the text, why the relationship exists.

Examples:
- "Adam" → "Microsoft": relation = "works_for"
- "Adam" → "Best Talent": relation = "has_award"
- "Microsoft Word" → "Microsoft": relation = "produced_by"
- "Microsoft Word" → "lightweight app": relation = "has_characteristic"


3. Output Formatting:
- Return the result in valid JSON format with two keys: 'entities' (list of entity objects) and 'relationships' (list of relationship objects).
- Exclude any text outside the JSON structure (e.g., no explanations or comments).
- If no entities or relationships are identified, return empty lists: { "entities": [], "relationships": [] }.

--Example Output-
{
  "entities": [
    {
      "entity_name": "Adam",
      "entity_type": "Person",
      "entity_description": "Adam is a software engineer who has worked at Microsoft since 2009."
    },
    {
      "entity_name": "Microsoft",
      "entity_type": "Company",
      "entity_description": "Microsoft is a technology company."
    },
    {
      "entity_name": "Microsoft Word",
      "entity_type": "Product",
      "entity_description": "Microsoft Word is a lightweight app accessible offline."
    },
    {
      "entity_name": "lightweight app",
      "entity_type": "Characteristic",
      "entity_description": "Describes Microsoft Word as having low resource usage."
    }
  ],
  "relationships": [
    {
      "source_entity": "Adam",
      "target_entity": "Microsoft",
      "relation": "works_for",
      "relationship_description": "Adam is a software engineer at Microsoft."
    },
    {
      "source_entity": "Microsoft Word",
      "target_entity": "Microsoft",
      "relation": "produced_by",
      "relationship_description": "Microsoft is the producer of Microsoft Word."
    },
    {
      "source_entity": "Microsoft Word",
      "target_entity": "lightweight app",
      "relation": "has_characteristic",
      "relationship_description": "Microsoft Word is described as a lightweight app."
    }
  ]
}


-Real Data-
######################
text: {text}
######################
output:"""

import json
import re
from typing import Any

def parse_fn(response_str: str) -> Any:
    json_pattern = r"\{.*\}"
    match = re.search(json_pattern, response_str, re.DOTALL)
    entities = []
    relationships = []
    if not match:
        return entities, relationships
    json_str = match.group(0)
    try:
        data = json.loads(json_str)
        entities = [
            (
                entity["entity_name"],
                entity["entity_type"],
                entity["entity_description"],
            )
            for entity in data.get("entities", [])
        ]
        relationships = [
            (
                relation["source_entity"],
                relation["target_entity"],
                relation["relation"],
                relation["relationship_description"],
            )
            for relation in data.get("relationships", [])
        ]
        return entities, relationships
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        return entities, relationships