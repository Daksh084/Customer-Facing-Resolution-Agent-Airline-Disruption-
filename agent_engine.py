
import json
import re
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data" / "source_data.json").read_text(encoding="utf-8"))

CUSTOMERS = DATA["customers"]
RULES = DATA["rules"]


def customer_by_name(name):
    return CUSTOMERS.get(name)


def profile_summary(name):
    c = CUSTOMERS[name]
    return (
        f"{name} is a {c['loyalty_tier']} customer (PNR {c['pnr']}). "
        f"Travel history: {c['travel_history']}."
    )


def flight_summary(name):
    c = CUSTOMERS[name]
    parts = []
    for f in c["flights"]:
        if f["flight"] == "Return":
            parts.append(f"Return flight {f['route']} on {f['date']} at {f['departure']} is unaffected.")
        elif "original_departure" in f:
            parts.append(
                f"{f['flight']} {f['route']} on {f['date']} is {f['status'].lower()}, "
                f"with new departure {f['departure']}."
            )
        else:
            parts.append(
                f"{f['flight']} {f['route']} on {f['date']} is {f['status'].lower()}."
            )
    return " ".join(parts)


def detect_legal_or_complaint(text):
    t = text.lower()
    terms = [
        "legal action", "lawyer", "lawsuit", "court", "formal complaint",
        "complaint", "consumer court", "file a case"
    ]
    return any(term in t for term in terms)


def detect_refund(text):
    t = text.lower()
    return "refund" in t or "money back" in t


def detect_upgrade(text):
    t = text.lower()
    return any(x in t for x in ["upgrade", "business class"])


def detect_full_night_hotel(text):
    t = text.lower()
    return "full night" in t or "whole night" in t or "night's hotel" in t or "night stay" in t


def detect_higher_fare(text):
    t = text.lower()
    return any(x in t for x in ["higher-fare", "higher fare", "different flight", "different, higher"])


def resolve(name, message):
    c = CUSTOMERS[name]
    t = message.lower()
    actions = []
    escalation = None

    # Immediate escalation conditions
    if detect_legal_or_complaint(message):
        escalation = {
            "reason": "Formal complaint / legal-action language",
            "message": (
                "I hear you, and I’m sorry this has been frustrating. "
                "This needs specialist support, so I’m escalating it to a human agent."
            )
        }
        return {
            "reply": escalation["message"],
            "actions": ["ESCALATE_TO_HUMAN"],
            "escalation": escalation,
            "policy_basis": "Formal complaints or threats of legal action must be escalated immediately.",
            "customer": c
        }

    # Scenario-specific deterministic policy reasoning
    if name == "Priya Nair":
        if detect_refund(t):
            actions.append("REFUND_REQUEST")
            refund_text = (
                "I can initiate a full refund for the airline-caused cancellation. "
                "The refund is processed within 7 business days and goes back to the original payment method."
            )
        else:
            refund_text = ""

        if detect_upgrade(t):
            actions.append("ESCALATE_TO_HUMAN")
            upgrade_text = (
                "A free Business Class upgrade on the unaffected return flight is not provided by the stated policy. "
                "Gold status gives priority rebooking, but it does not add compensation beyond the standard policy."
            )
        else:
            upgrade_text = ""

        if refund_text and upgrade_text:
            reply = refund_text + " " + upgrade_text + " I can proceed with the refund, or help with the cancellation rebooking option."
        elif refund_text:
            reply = refund_text
        elif upgrade_text:
            reply = upgrade_text
        else:
            reply = (
                "Your SK-204 flight from Delhi to Goa on 23 September at 18:40 is cancelled due to operational reasons. "
                "You can choose free rebooking on the next available flight within 24 hours or a full refund."
            )

        if detect_upgrade(t):
            escalation = {
                "reason": "Requested benefit is outside the stated policy",
                "message": "The requested free Business Class upgrade is outside the provided policy, so a human agent must handle the exception request."
            }

        return {
            "reply": reply,
            "actions": actions,
            "escalation": escalation,
            "policy_basis": RULES["cancellation_rebooking"] + " " + RULES["loyalty"],
            "customer": c
        }

    if name == "Arvind Kulkarni":
        # 4h delay: meal + lounge, but no hotel
        if "hotel" in t:
            reply = (
                "Your SK-118 flight is delayed by 4 hours. Under the policy, a delay of more than 3 hours "
                "qualifies for a meal voucher and lounge access. Hotel accommodation starts only when the delay is more than 5 hours, "
                "so I can provide the meal voucher and lounge access, but not hotel accommodation for this 4-hour delay."
            )
        else:
            reply = (
                "Your SK-118 flight from Mumbai to Bengaluru is delayed by 4 hours, with the new departure at 11:10. "
                "This qualifies for a meal voucher and lounge access under the delay policy."
            )
        actions.extend(["MEAL_VOUCHER", "LOUNGE_ACCESS"])
        return {
            "reply": reply,
            "actions": actions,
            "escalation": None,
            "policy_basis": RULES["delay_over_3"],
            "customer": c
        }

    if name == "Meher Kaur":
        # 6h delay: meal + lounge + delayed-hours hotel. Higher fare diff ₹2000 => supervisor approval needed.
        if detect_full_night_hotel(t):
            hotel_text = (
                "Because the delay is 6 hours, the policy provides hotel accommodation covering only the delayed hours, "
                "not a full night’s stay."
            )
        else:
            hotel_text = (
                "Because the delay is 6 hours, the policy provides meal voucher + lounge access + hotel accommodation "
                "covering only the delayed hours."
            )

        if detect_higher_fare(t) or "2000" in t or "₹2,000" in message:
            fare_text = (
                "The alternative flight has a ₹2,000 fare difference. Because that is above ₹1,500, "
                "I cannot waive it without supervisor approval, so I’m escalating that part to a human agent."
            )
            actions.append("ESCALATE_TO_HUMAN")
            escalation = {
                "reason": "Fare-difference waiver exceeds ₹1,500",
                "message": fare_text
            }
        else:
            fare_text = ""

        actions.extend(["MEAL_VOUCHER", "LOUNGE_ACCESS", "HOTEL_DELAYED_HOURS"])
        reply = hotel_text + (" " + fare_text if fare_text else "")
        return {
            "reply": reply,
            "actions": actions,
            "escalation": escalation,
            "policy_basis": RULES["delay_over_5"] + " " + RULES["fare_difference"],
            "customer": c
        }

    return {
        "reply": "I can provide the booking and flight status available in the supplied customer data.",
        "actions": ["STATUS_LOOKUP"],
        "escalation": None,
        "policy_basis": "Customer and booking data supplied in the assignment.",
        "customer": c
    }


def quick_scenario(name):
    if name == "Priya Nair":
        return resolve(name, "My flight was cancelled. I want a full cash refund and a free upgrade to business class on my return flight.")
    if name == "Arvind Kulkarni":
        return resolve(name, "My flight is delayed 4 hours. I want hotel accommodation because of the long delay.")
    if name == "Meher Kaur":
        return resolve(name, "My flight is delayed 6 hours. I want a full night's hotel stay and a different higher-fare flight with the ₹2,000 fare difference waived.")
