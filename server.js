import express from 'express';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataDir = path.join(__dirname, 'store-data');
const buyersPath = path.join(dataDir, 'interested-buyers.json');
const emailsPath = path.join(dataDir, 'email-outbox.json');
const n8nWebhookUrl = process.env.N8N_WEBHOOK_URL || 'https://devtones.app.n8n.cloud/webhook/buyer-interest';

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function normalizeInput(raw) {
  const entries = Object.entries(raw ?? {}).map(([key, value]) => [String(key).trim().toLowerCase(), value]);
  const get = (names, fallback = '') => {
    const found = names
      .map((name) => String(name).trim().toLowerCase())
      .map((name) => entries.find(([key]) => key === name))
      .find(Boolean);
    return String(found?.[1] ?? fallback).trim();
  };
  const money = (value) => {
    const numeric = String(value ?? '').replace(/[^0-9.]/g, '');
    return numeric ? Number(numeric) : 0;
  };
  const list = (value) => String(value ?? '').split(/[,;|]/).map((item) => item.trim()).filter(Boolean);

  const budget = money(get(['budget', 'price range', 'target budget', 'spend']));
  const urgency = get(['urgency', 'when do you need it', 'timeline'], 'browsing').toLowerCase();
  const highIntentWords = ['today', 'now', 'urgent', 'this week', 'asap', 'ready', 'checkout'];
  const highIntent = highIntentWords.some((word) => urgency.includes(word)) || budget >= 150;
  const email = get(['email', 'email address']);
  const phone = get(['phone', 'phone number', 'whatsapp', 'mobile']);
  const preferredSizes = list(get(['size', 'sizes', 'preferred size']));
  const hasContact = Boolean(email || phone);
  const segment = highIntent ? 'Ready-to-buy' : budget >= 75 ? 'Warm lead' : 'Browsing';
  const priority = highIntent ? 'High' : budget >= 75 ? 'Medium' : 'Standard';
  const missingSizeFlag = preferredSizes.length ? '' : 'Missing size preference - stylist follow-up needed';
  const missingContactFlag = hasContact ? '' : 'Missing contact details - cannot follow up';

  return {
    id: crypto.randomUUID(),
    submittedAt: new Date().toISOString(),
    name: get(['full name', 'name', 'customer name'], 'New buyer'),
    email,
    phone,
    productInterest: get(['product interest', 'item', 'items', 'interested item', 'collection']),
    category: get(['category', 'style category'], 'Fashion & lifestyle'),
    budget,
    preferredSizes: preferredSizes.join(', '),
    styleTags: list(get(['style', 'style preference', 'occasion', 'vibe'])).join(', '),
    urgency: urgency || 'browsing',
    source: get(['source', 'how did you hear about us'], 'Interest form'),
    notes: get(['notes', 'message', 'special request']),
    segment,
    priority,
    highIntent,
    hasContact,
    status: hasContact ? 'Follow-up queued' : 'Saved for review',
    recommendedAction: highIntent ? 'Send personal shopping offer' : 'Send lookbook and save for nurture',
    flags: [missingSizeFlag, missingContactFlag].filter(Boolean).join('; '),
    randomDelayMinutes: Math.floor(Math.random() * 111) + 10
  };
}

async function readJson(file, fallback) {
  try {
    return JSON.parse(await fs.readFile(file, 'utf8'));
  } catch {
    return fallback;
  }
}

async function writeJson(file, value) {
  await fs.mkdir(dataDir, { recursive: true });
  await fs.writeFile(file, JSON.stringify(value, null, 2));
}

function buildEmails(buyer) {
  const storeName = process.env.STORE_NAME || 'Luma & Thread';
  const lookbook = process.env.LOOKBOOK_LINK || 'https://yourstore.com/lookbook';
  const shoppingAssist = process.env.SHOPPING_ASSIST_LINK || 'https://wa.me/630000000000';
  const emails = [
    {
      type: 'buyer-confirmation',
      to: buyer.email || buyer.phone || 'missing contact',
      subject: 'We saved your picks',
      body: `Hi ${buyer.name}, thanks for your interest in ${buyer.productInterest || 'our latest pieces'}. We saved your preferences and will help you find the right fit. Lookbook: ${lookbook}`,
      createdAt: new Date().toISOString()
    },
    {
      type: 'sales-alert',
      to: process.env.SALES_ALERT_EMAIL || 'sales@yourstore.com',
      subject: `New ${buyer.priority} Priority Buyer: ${buyer.name}`,
      body: `${buyer.name} is interested in ${buyer.productInterest || 'unspecified items'}. Segment: ${buyer.segment}. Budget: ${buyer.budget}. Sizes: ${buyer.preferredSizes || 'not provided'}. Action: ${buyer.recommendedAction}. Flags: ${buyer.flags || 'None'}`,
      createdAt: new Date().toISOString()
    }
  ];

  if (buyer.highIntent && buyer.hasContact) {
    emails.push({
      type: 'personal-shopping-offer',
      to: buyer.email || buyer.phone,
      subject: 'Want us to reserve this for you?',
      body: `Hi ${buyer.name}, your interest looks time-sensitive. Reply here or use ${shoppingAssist} so ${storeName} can reserve, confirm sizing, or suggest styled alternatives.`,
      createdAt: new Date().toISOString(),
      scheduledDelay: `${buyer.randomDelayMinutes} minutes`
    });
  }

  return emails;
}

app.post('/webhook/buyer-interest', async (req, res) => {
  const buyer = normalizeInput(req.body);
  const buyers = await readJson(buyersPath, []);
  const outbox = await readJson(emailsPath, []);
  const emails = buildEmails(buyer);
  let workflow = {
    ok: false,
    message: 'Workflow endpoint not reached'
  };

  try {
    const response = await fetch(n8nWebhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    const text = await response.text();
    workflow = {
      ok: response.ok,
      status: response.status,
      message: text
    };
  } catch (error) {
    workflow = {
      ok: false,
      message: error instanceof Error ? error.message : 'Workflow request failed'
    };
  }

  await writeJson(buyersPath, [buyer, ...buyers]);
  await writeJson(emailsPath, [...emails, ...outbox]);

  res.json({
    ok: true,
    message: 'Interest saved',
    status: buyer.status,
    workflow,
    buyer,
    emails
  });
});

app.get('/api/buyers', async (_req, res) => {
  res.json(await readJson(buyersPath, []));
});

app.get('/api/emails', async (_req, res) => {
  res.json(await readJson(emailsPath, []));
});

app.post('/api/reset', async (_req, res) => {
  await writeJson(buyersPath, []);
  await writeJson(emailsPath, []);
  res.json({ ok: true });
});

const port = Number(process.env.PORT || 3210);
app.listen(port, () => {
  console.log(`Fashion buyer automation: http://localhost:${port}`);
});
