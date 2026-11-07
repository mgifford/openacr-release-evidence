# Contributing

1. Open an issue with the problem, affected product/release, exact reproduction
   steps, sources, and expected behavior. For security issues, use SECURITY.md.
2. Discuss changes to evidence semantics, adapter contracts and governance
   before large PRs. Avoid exposing private issue data.
3. Add or update tests and documentation; keep synthetic fixtures identified.
4. Run `python -m unittest discover -s tests -v` and inspect generated site.
5. Submit a focused PR with test results and an accessibility statement.

## Pull request checklist

- [ ] Data provenance and target scope preserved
- [ ] Does not infer conformance from issue status alone
- [ ] Tests added, run and documented
- [ ] Keyboard tested: yes / no (with reason)
- [ ] Public/private output boundaries reviewed
- [ ] Documentation and migrations updated where needed
- [ ] Dependency licences and environmental impact considered

Review decisions follow GOVERNANCE.md. Contributors should avoid unsolicited
AI-generated changes presented as independently verified work. Disclose model
use in code or evidence analyses where it materially affected the result.
