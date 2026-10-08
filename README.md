# Fashion Store Interested Buyer Automation

This is a portable n8n workflow for a fashion and lifestyle store: an end-to-end buyer interest flow that captures leads, reassures shoppers quickly, keeps sales informed, and routes ready-to-buy customers toward personal shopping or reservation.

## What It Does

- Accepts buyer interest through a webhook.
- Normalizes messy form field names, including hidden trailing spaces.
- Saves every interested buyer to Google Sheets before any outbound email runs.
- Sends shoppers an immediate confirmation email with a lookbook link.
- Alerts the sales team with product interest, budget, sizes, style tags, segment, and flags.
- Segments buyers into `Browsing`, `Warm lead`, and `Ready-to-buy`.
- Flags high-intent buyers based on urgency language or budget.
- Flags missing size preferences for stylist follow-up instead of losing the lead.
- Sends ready-to-buy shoppers a personal shopping or reservation link after a randomized delay.
- Updates the tracker after the personal shopping offer is sent.

## Files

- `fashion-buyer-interest-workflow.json` - n8n workflow export.
- `server.js` - local server that runs the buyer intake flow without needing live credentials.
- `public/` - buyer form, live tracker, outbox, and workflow backbone view.

## Local Setup

Run this from `D:\dev\Automations`:

```powershell
npm install
npm start
```

Open:

```text
http://localhost:3210
```

For an operating check:

1. Start on the form with the prefilled high-intent shopper.
2. Click `Submit interest`.
3. Show the tracker: the buyer is saved first with segment, priority, budget, size, action, and flags.
4. Show the outbox: confirmation email, sales alert, and personal shopping offer are generated.
5. Click `Reset`, clear the size field, submit again, and show the missing-size flag.

The local app writes data to:

```text
store-data/interested-buyers.json
store-data/email-outbox.json
```

## Required Setup

Create a Google Sheet named `Interested Buyers` with these columns:

```text
Submitted At
Name
Email
Phone
Product Interest
Category
Budget
Preferred Sizes
Style Tags
Urgency
Segment
Priority
Status
Recommended Action
Flags
Source
Notes
Last Updated
```

Configure these n8n environment variables:

```text
GOOGLE_SHEET_ID=your_google_sheet_id
SALES_ALERT_EMAIL=sales@yourstore.com
LOOKBOOK_LINK=https://yourstore.com/lookbook
SHOPPING_ASSIST_LINK=https://wa.me/your-number
STORE_NAME=Your Store Name
```

After importing the workflow into n8n:

1. Replace the placeholder Google Sheets credential.
2. Replace the placeholder Gmail credential.
3. Activate the workflow.
4. Point your form action to the production webhook URL for `Buyer Interest Webhook`.

## Suggested Form Fields

The workflow accepts flexible field labels, but these names are easiest:

```text
Full Name
Email
Phone
Product Interest
Category
Budget
Preferred Size
Style Preference
Urgency
Source
Notes
```

## Test Payload

Send this to the webhook in test mode:

```json
{
  "Full Name": "Amara Reyes",
  "Email": "amara@example.com",
  "Phone": "+63 900 000 0000",
  "Product Interest": "linen co-ord set",
  "Category": "Resort wear",
  "Budget": "180",
  "Preferred Size": "M",
  "Style Preference": "minimal, neutral, vacation",
  "Urgency": "Need it this week",
  "Source": "Instagram",
  "Notes": "Open to similar pieces if beige is sold out."
}
```

## Upgrade Ideas

- Add WhatsApp or Instagram DM follow-up for shoppers who prefer chat.
- Add a duplicate-buyer check using email or phone before appending to the sheet.
- Add a second Google Sheet tab for analytics by product category and segment.
- Add separate paths for premium, sale, and custom-order shoppers.
- Add inventory checks before sending reservation links.
