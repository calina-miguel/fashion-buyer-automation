const form = document.querySelector('#buyer-form');
const buyersEl = document.querySelector('#buyers');
const outboxEl = document.querySelector('#outbox');
const totalEl = document.querySelector('#total');
const readyEl = document.querySelector('#ready');
const emailsEl = document.querySelector('#emails');
const resetButton = document.querySelector('#reset');

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  })[char]);
}

async function refresh() {
  const [buyers, emails] = await Promise.all([
    fetch('/api/buyers').then((response) => response.json()),
    fetch('/api/emails').then((response) => response.json())
  ]);

  totalEl.textContent = buyers.length;
  readyEl.textContent = buyers.filter((buyer) => buyer.segment === 'Ready-to-buy').length;
  emailsEl.textContent = emails.length;

  buyersEl.classList.toggle('empty', buyers.length === 0);
  buyersEl.innerHTML = buyers.length ? buyers.map((buyer) => `
    <article class="card">
      <header>
        <div>
          <div class="name">${escapeHtml(buyer.name)}</div>
          <div class="sub">${escapeHtml(buyer.productInterest || 'No product listed')} · ${escapeHtml(buyer.category)}</div>
        </div>
        <span class="badge ${buyer.priority === 'High' ? 'high' : ''}">${escapeHtml(buyer.priority)}</span>
      </header>
      <dl class="details">
        <div><strong>Segment:</strong> ${escapeHtml(buyer.segment)}</div>
        <div><strong>Budget:</strong> ${escapeHtml(buyer.budget)}</div>
        <div><strong>Size:</strong> ${escapeHtml(buyer.preferredSizes || 'Not provided')}</div>
        <div><strong>Action:</strong> ${escapeHtml(buyer.recommendedAction)}</div>
        <div><strong>Flags:</strong> ${escapeHtml(buyer.flags || 'None')}</div>
      </dl>
    </article>
  `).join('') : 'No buyers yet.';

  outboxEl.classList.toggle('empty', emails.length === 0);
  outboxEl.innerHTML = emails.length ? emails.map((email) => `
    <article class="email">
      <header>
        <div>
          <div class="name">${escapeHtml(email.subject)}</div>
          <div class="sub">To: ${escapeHtml(email.to)} · ${escapeHtml(email.type)}</div>
        </div>
      </header>
      <p>${escapeHtml(email.body)}</p>
    </article>
  `).join('') : 'No emails yet.';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  const button = form.querySelector('button');
  button.disabled = true;
  button.textContent = 'Running automation...';
  await fetch('/webhook/buyer-interest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  button.disabled = false;
  button.textContent = 'Submit interest';
  await refresh();
});

resetButton.addEventListener('click', async () => {
  await fetch('/api/reset', { method: 'POST' });
  await refresh();
});

refresh();
