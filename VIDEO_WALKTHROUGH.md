# Luma & Thread Interested Buyer Automation Walkthrough

## Goal

Create a short screen recording that shows how Luma & Thread captures interested fashion and lifestyle buyers, saves them to a tracker, alerts the sales team, and follows up with ready-to-buy shoppers.

## Recommended Length

30 to 45 seconds.

## Recording Setup

- Open the buyer desk: `http://localhost:3210`
- Open the workflow canvas: `https://devtones.app.n8n.cloud/workflow/anSd0GnuD9zYGiLD`
- Open the Google Sheet: `Interested Buyers`
- Keep the browser zoom at 90-100%.
- Hide unrelated browser tabs if possible.
- Start with the local buyer desk visible.

## Storyboard

### 1. Problem Frame

Screen: buyer desk form.

Voiceover:

> Fashion and lifestyle stores get interest from Instagram, messages, product links, and quick inquiries. The problem is that serious buyers can get mixed in with casual browsing, and the sales team has to manually sort, follow up, and update the tracker.

On-screen action:

- Hover over the form fields.
- Keep the prefilled buyer visible.

### 2. Submit a Buyer

Screen: buyer desk form.

Voiceover:

> This workflow gives the team a single intake point. A shopper submits what they want, their budget, size, style preferences, and urgency.

On-screen action:

- Click `Submit interest`.
- Pause on the status message: `Live workflow accepted the buyer submission.`
- Show the production webhook response: `{"message":"Workflow was started"}`.

### 3. Show Local Output

Screen: buyer desk output.

Voiceover:

> The buyer is immediately segmented. High-intent shoppers are marked ready-to-buy, missing details are flagged, and the recommended next action is generated for the team.

On-screen action:

- Scroll or point to `Buyer Tracker`.
- Show segment, priority, budget, size, action, and flags.
- Show the email outbox cards.

### 4. Show The Workflow Backbone

Screen: n8n workflow canvas.

Voiceover:

> Behind the form is an n8n workflow. It receives the buyer submission, normalizes the fields, saves the buyer to Google Sheets, sends a confirmation email, alerts the sales team, and routes ready-to-buy shoppers into a personal shopping follow-up.

On-screen action:

- Open the n8n canvas.
- Keep the canvas steady in a 16:9 frame.
- Pause briefly on:
  - `Buyer Interest Webhook`
  - `Normalize and Segment Buyer`
  - `Save Buyer to Google Sheet`
  - `Alert Sales Team`
  - `Ready to Buy?`
  - `Send Personal Shopping Offer`
  - `Mark Offer Sent`

### 5. Show The Tracker

Screen: Google Sheet.

Voiceover:

> The team gets a clean buyer tracker with contact details, preferences, urgency, segment, priority, status, and recommended action.

On-screen action:

- Open the Google Sheet.
- Show the newest buyer row.
- Briefly move across the segment, priority, status, and recommendation columns.

### 6. Close With Value

Screen: back to workflow canvas or buyer desk.

Voiceover:

> Instead of manually sorting interested shoppers, Luma & Thread gets a structured buyer record, faster sales alerts, and a clear follow-up path for the shoppers most likely to buy.

On-screen action:

- End on the n8n canvas or the local buyer desk output.

## Short Caption Version

Use this if recording without voice:

1. Interested buyer submits product, budget, size, style, and urgency.
2. Workflow accepts the submission instantly.
3. Buyer is segmented and saved to the tracker.
4. Sales receives the key details and recommended action.
5. Ready-to-buy shoppers enter a personal shopping follow-up path.
6. Google Sheets stays updated for the team.

## n8n Editor Note

The orange `Execute workflow` button listens for the temporary test webhook URL. If the editor says `Waiting for you to call the Test URL`, send the buyer payload to the test URL shown inside the webhook node while the listener is active.

The published workflow uses:

```text
https://devtones.app.n8n.cloud/webhook/buyer-interest
```

The production success response is:

```json
{"message":"Workflow was started"}
```

## Post Copy

Managing interested buyers should not feel like chasing scattered messages.

For Luma & Thread, I built a fashion and lifestyle buyer intake workflow that turns a shopper inquiry into a structured sales record.

The flow:

`Buyer form -> n8n -> Google Sheets -> Gmail -> follow-up path`

It captures buyer details, segments intent, flags missing preferences, alerts the sales team, and routes ready-to-buy shoppers toward a personal shopping offer.

The goal is simple: help the team move faster on serious buyer interest without losing context in messages, spreadsheets, or manual follow-ups.

Built with n8n, Google Sheets, and Gmail.

## Hashtags

`#n8n #workflowautomation #businessautomation #retailautomation #fashiontech #nocode #salesautomation`

## Recording Checklist

- Submit one buyer with a size included.
- Submit one buyer with the size field empty to show the missing-size flag.
- Show the n8n workflow canvas after the form submission.
- Show the newest Google Sheet row.
- Keep the recording under 90 seconds.
- Do not show private inbox content.
- Do not show credential settings.
