# Contributing

1. Open an issue with the problem, affected product/release, exact reproduction
   steps, sources and expected behaviour. For security issues, use `SECURITY.md`.
2. Discuss changes to evidence semantics, adapter contracts, applicability rules
   and governance before large PRs. Never expose private issue data or raw CLI
   output.
3. Add or update tests and documentation. Keep synthetic fixtures identified and
   record provenance for real fixtures.
4. Run the checks on a clean checkout:

   ```sh
   python3 -m pip install -e '.[yaml]'   # or export PYTHONPATH=src
   python3 -m unittest discover -s tests -v
   python3 -m compileall -q src
   ```

5. If you change the report or explorer, render at 320 CSS px, run axe-core,
   test keyboard-only operation (skip link, `<details>`) and confirm the report
   is usable with JavaScript disabled.
6. Submit a focused PR with test results and an accessibility statement.

## Pull request checklist

- [ ] Data provenance, target, observation time and digest preserved
- [ ] Does not infer conformance from issue status, counts or commit inclusion
- [ ] Applicability rule changes are reflected in `docs/EVIDENCE-MODEL.md` and tests
- [ ] Tests added, run and documented
- [ ] Keyboard tested: yes / no (with reason)
- [ ] 320 px reflow and no-JavaScript checks recorded for UI changes
- [ ] Public/private output boundaries reviewed; no raw evidence committed
- [ ] Documentation updated, including `AUDIT.md` if defects remain
- [ ] Dependency licences and environmental impact considered
- [ ] AI use disclosed; no unreviewed model output presented as evidence

Review decisions follow `GOVERNANCE.md`. Contributors should avoid unsolicited
AI-generated changes presented as independently verified work. Disclose model
use in code or evidence analyses where it materially affected the result.
