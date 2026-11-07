const scope = document.querySelector('#scope');
const findings = document.querySelector('#findings');
const filter = document.querySelector('#status-filter');
const count = document.querySelector('#count');
const el = (name, content, className) => {
  const node = document.createElement(name);
  if (className) node.className = className;
  node.textContent = content == null ? 'Not recorded' : String(content);
  return node;
};
const p = (name, value) => {
  const line = document.createElement('p');
  line.append(el('strong', `${name}: `), document.createTextNode(String(value ?? 'Unknown')));
  return line;
};
function link(url, text) {
  const a = el('a', text);
  try {
    const target = new URL(url);
    if (target.protocol === 'https:') { a.href = target.href; a.rel = 'noopener noreferrer'; }
  } catch (_) { /* invalid URLs are displayed as unlinked text */ }
  return a;
}
function render(data) {
  const target = data.assessment;
  scope.replaceChildren(
    p('Product', target.product), p('Release', target.release),
    p('Assessment identifier', target.id),
    p('Components', (target.components || []).join(', ')),
    p('Baseline', (target.standards || []).join(', ')),
    p('Generated', data.generated_at),
    p('Evidence digest', data.evidence_digest)
  );
  const all = data.findings || [];
  function update() {
    const shown = all.filter(item => filter.value === 'all' || item.applicability === filter.value);
    count.textContent = `${shown.length} of ${all.length} findings shown. No WCAG conformance determination has been made.`;
    const cards = shown.map(item => {
      const card = document.createElement('article'); card.className = 'finding';
      card.append(el('h3', item.title));
      const source = document.createElement('p');
      source.append(el('strong', 'Source: '), link(item.source_url, item.issue_id));
      card.append(source, p('Release applicability', item.applicability),
        p('Evidence basis', item.basis), p('Reason', item.reason),
        p('Tracker status (not release status)', item.tracker_status),
        p('Candidate WCAG criteria (not verified)', item.wcag_candidates.join(', ') || 'None'),
        p('Review state', item.review_status));
      if (item.evidence_urls.length) {
        const refs = document.createElement('p'); refs.append(el('strong', 'Evidence links: '));
        item.evidence_urls.forEach((u, i) => { if (i) refs.append(document.createTextNode('; ')); refs.append(link(u, u)); });
        card.append(refs);
      }
      return card;
    });
    findings.replaceChildren(...cards);
    if (!cards.length) findings.append(el('p', 'No findings match the selected status.', 'empty'));
  }
  filter.addEventListener('change', update);
  update();
}
fetch('./evidence.json', {cache:'no-store'})
  .then(response => {if (!response.ok) throw Error(`HTTP ${response.status}`); return response.json();})
  .then(render)
  .catch(error => { scope.textContent = 'Unable to load assessment data.'; findings.textContent = `Unable to load evidence: ${error.message}`; count.textContent = 'No findings available.'; });
