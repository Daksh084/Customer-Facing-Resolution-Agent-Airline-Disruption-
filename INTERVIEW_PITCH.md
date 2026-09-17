
# Interviewer Pitch — 60 seconds

"I built this as a policy-grounded customer resolution agent rather than a generic chatbot.
The key design decision is that the assignment data pack is the source of truth. The agent first
identifies the disruption and customer request, then maps it to an explicit policy rule. It can
execute supported resolutions, but when a request crosses an authorization boundary — such as a
₹2,000 fare-difference waiver when the agent limit is ₹1,500 — it escalates instead of hallucinating
a benefit.

I also made the decision trace visible: the reviewer can see the action, policy basis and escalation
reason. That makes the prototype easier to audit and demonstrates how I would separate an LLM's
conversation layer from a deterministic policy/authorization layer in a production system."
