# Changelog

## 0.4.0

- License the Stevens Group's own work under MIT. Copied skills keep their authors' terms, as the README's Licence section explains.
- Note that this repo's automatic PR review is turned off until there's an API key.

## 0.3.0

- Add `socratic-tutor` from Jane Street's [agent_skills](https://github.com/janestreet/agent_skills) (MIT), unchanged with its licence. It teaches a topic by asking questions, tracks a 0-5 skill map and ends with a final assessment.
- The validator now accepts quoted frontmatter values, such as `name: "socratic-tutor"`.

## 0.2.0

- Include all thirteen Softnano workflows under the Stevens Group namespace, preserving the existing SG cluster instructions and untangle-codebase skill.
- Adapt migrated workflows to portable agent interfaces, installed skill paths and safer handoff environment inspection.
- Deprecate the Softnano plugin in favour of stevens@stevens-group.
- Version both plugin manifests together. Require a major or minor release for every merged change and publish it automatically after validation.

## 0.1.0

- Initial Stevens Group skill collection.
