KG_TRIPLET_EXTRACT_TMPL = """
-Goal-
Given a text document, identify all entities and their entity types from the text and all relationships among the identified entities.
Given the text, extract up to {max_knowledge_triplets} entity-relation triplets.

-Steps-
1. Identify all entities. Prefer entities that are involved in meaningful relationships described in the text. Avoid extracting vague entities. For each identified entity, extract the following information:
- entity_name:  Use the **most complete, canonical, and standardized form** of the entity name as explicitly mentioned in the text. Always **capitalize properly**. For example:
  - Use **"Microsoft Word"**, not "ms word", "MSWORD", or "Word".
  - Use **"John Smith"**, not "John", "J. Smith", or "he".
  - Avoid abbreviations, nicknames, or partially mentioned forms.
  - Avoid using lowercase-only or incomplete names.
  - If the same entity appears in different forms across documents (e.g., "Google Inc." and "Google"), **always use the most descriptive and complete form**.

- entity_type: Use only standard high-level types such as:
  - "Person"
  - "Company"
  - "Product"
  - "Award"
  - "Scientific Theory"
  - "Characteristic"
  Avoid overly specific or custom types (e.g., "Software Engineer"/ "Scientist"/ "Sister" should always be classified as "Person").

  - entity_description: A concise explanation of the entity’s properties, significance, or role, as inferred directly from the text.

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relation: Use lowercase snake_case format (e.g., "works_for", "has_award", "produced_by"). Use general and timeless relationships.
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other

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