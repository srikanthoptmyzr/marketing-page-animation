# Schemas

JSON Schemas (draft 2020-12) for the intermediate artifacts. Structure only; semantic checks (ids resolve, one final state, timeline references, content keys) are done by `scripts/validate/validate_scene.py`.

| File | Describes | Notes |
|---|---|---|
| `scene.schema.json` | One scene definition (an entry of `spec/scenes.json`) | Authority for the fields: `references/ui-scene-system.md`. `responsive.designWidth` is the design width |
| `content.schema.json` | The content layer for one language | Every entry has `role`, `translate`, `sensitivity` |
| `privacy-map.schema.json` | `spec/privacy-map.json`: replacements only | `additionalProperties: false`, so an `original` field is rejected. Optional `format.keep` lists generic segments that may stay |
| `originals.schema.json` | `.private/originals.json` (never shared) | Used only by the leak scanner |

A brief schema is not planned: the brief is a template (`templates/brief.template.md`).

Validate with any JSON Schema library, for example `python3 -c "import json,jsonschema; jsonschema.validate(json.load(open('scene.json')), json.load(open('scene.schema.json')))"`. A worked example is in `templates/example-scene/`.
