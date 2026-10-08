# n8n Import Guide

Use `fashion-buyer-interest-workflow.json` as the workflow import file.

## Import

1. Open your n8n workspace.
2. Create a new workflow.
3. Open the workflow menu.
4. Choose import from file or paste JSON.
5. Select `fashion-buyer-interest-workflow.json`.
6. Save the workflow as `Fashion Store Interested Buyer Automation`.

## Required Credentials

Connect these credentials inside n8n after import:

- Google Sheets credential for the buyer tracker.
- Gmail credential for buyer confirmation, sales alert, and personal shopping offer.

## Required Variables

Set these in n8n environment variables or replace them directly in the nodes:

```text
GOOGLE_SHEET_ID=your_google_sheet_id
SALES_ALERT_EMAIL=sales@example.com
LOOKBOOK_LINK=https://yourstore.com/lookbook
SHOPPING_ASSIST_LINK=https://wa.me/your-number
STORE_NAME=Your Store Name
```

## Google Sheet

Create a sheet tab named `Interested Buyers` with these columns:

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

## Test Payload

Use this payload against the webhook test URL:

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
