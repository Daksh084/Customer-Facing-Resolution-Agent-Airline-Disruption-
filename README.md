
# AIONOS Customer Resolution Agent — Assignment 3

A clickable, locally runnable prototype for the **Customer-Facing Resolution Agent (Airline Disruption)** assignment.

## What the prototype demonstrates

The app handles all three required scenarios:

1. **Priya Nair — Gold / SK4821X**
   - Cancelled SK-204, Delhi → Goa
   - Offers the policy-supported choice: free next-available rebooking within 24 hours OR full refund.
   - Correctly refuses to invent a free Business Class upgrade.
   - Escalates the out-of-policy upgrade request.

2. **Arvind Kulkarni — Silver / TR1190B**
   - SK-118 delayed 4 hours.
   - Applies meal voucher + lounge access.
   - Does not grant hotel accommodation because the hotel rule starts at more than 5 hours.

3. **Meher Kaur — Platinum / WL7742**
   - SK-305 delayed 6 hours.
   - Applies meal voucher + lounge access + hotel accommodation for delayed hours only.
   - Does not grant a full-night hotel stay.
   - Detects the ₹2,000 higher-fare difference and escalates because waiver above ₹1,500 requires supervisor approval.

## Run locally

### macOS / Linux

```bash
cd customer_resolution_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Windows

```powershell
cd customer_resolution_agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, normally:

`http://localhost:8501`

## Architecture

```text
                    ┌─────────────────────┐
                    │  Streamlit UI       │
                    │  Customer Chat      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Resolution Engine   │
                    │ intent + policy     │
                    │ decision + guardrail │
                    └───────┬─────┬───────┘
                            │     │
                 ┌──────────┘     └───────────┐
                 ▼                            ▼
        ┌────────────────┐          ┌──────────────────┐
        │ Source Data    │          │ Human Escalation │
        │ JSON           │          │ rules            │
        └────────────────┘          └──────────────────┘
```

## Design choices worth explaining in the interview

### 1. Policy-first instead of hallucination-first
The assignment explicitly says to use only its supplied material. Therefore this prototype treats the provided data pack as the source of truth and keeps the decision logic deterministic.

### 2. Separation of response and authorization
The agent can explain a policy and prepare an action, but it does not silently approve prohibited exceptions.

### 3. Explainability
Every resolution exposes:
- decision status
- actions
- policy basis
- escalation reason where applicable

### 4. Customer-aware but not over-privileged
Loyalty tier is used only where the data pack says it matters: Gold/Platinum get priority rebooking, with no extra compensation.

## Suggested interview demo flow

1. Open the app.
2. Select **Priya Nair**.
3. Click **Run assigned scenario**.
4. Point out that refund is policy-supported while the free Business Class upgrade is not.
5. Select **Arvind Kulkarni** and run the scenario.
6. Point out the 4-hour threshold: meal + lounge, no hotel.
7. Select **Meher Kaur**.
8. Point out the 6-hour rule and the separate ₹2,000 fare-difference escalation.
9. Open **Policy basis** and explain that the agent can show why it made each decision.

## Important scope

This is a prototype, not a live airline booking system. The supplied assignment data does not contain a real flight inventory/search API, payment API, or customer authentication system, so the prototype does not invent those capabilities.

## Optional next step

For a production architecture, the deterministic policy engine can be replaced or wrapped by an LLM-based intent layer, while keeping the policy engine as the authorization/guardrail layer. This prevents an LLM from granting benefits outside the airline's configured policy.
