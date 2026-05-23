import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter Client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Load SOP data
with open("sop_data.json", "r") as file:
    sop_data = json.load(file)

# System Prompt
system_prompt = f"""
You are an AI customer support assistant for {sop_data['business']}.

RULES:
- Answer ONLY using the SOP information provided.
- Do NOT make up information.
- If the answer is not found in SOP data, reply EXACTLY:
ESCALATE_REQUIRED

- Escalate for:
    - complaints
    - medical questions
    - pricing negotiation
    - angry customers
    - unknown questions

SOP DATA:
{sop_data}

Tone:
Professional, polite, and friendly.
"""

conversation = []

lead_data = {}

qualified = False

escalation_keywords = [
    "complaint",
    "angry",
    "refund",
    "lawsuit",
    "medical",
    "pain",
    "sue",
    "frustrated"
]

print("AI Support Assistant Started")
print("Type 'exit' to stop.\n")

while True:

    user_input = input("Customer: ")

    if user_input.lower() == "exit":
        break

    # Save user message
    conversation.append({
        "role": "user",
        "content": user_input
    })

    # Keyword Escalation Detection
    escalation_reason = None

    for word in escalation_keywords:
        if word in user_input.lower():
            escalation_reason = word
            break

    # Escalation detected
    if escalation_reason:
        print("\nAI: I’m escalating this conversation to a human agent.")
        print(f"Reason: {escalation_reason}\n")

        conversation.append({
            "role": "assistant",
            "content": f"Escalated because: {escalation_reason}"
        })

        continue

    # AI Response
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            *conversation
        ]
    )

    ai_reply = response.choices[0].message.content

    # Confidence-based escalation
    if "ESCALATE_REQUIRED" in ai_reply:

        print("\nAI: I’m not sure about that, so I’ll connect you with a human agent.\n")

        conversation.append({
            "role": "assistant",
            "content": "Escalated due to unknown question"
        })

        continue

    # Normal response
    print(f"\nAI: {ai_reply}\n")

    conversation.append({
        "role": "assistant",
        "content": ai_reply
    })

    # Lead Qualification (only once)
    if not qualified:

        print("AI: Before we continue, I’d like to ask a few questions.\n")

        business_type = input("AI: What type of business do you run? ")
        team_size = input("AI: How many team members do you have? ")
        tools = input("AI: What tools are you currently using? ")

        lead_data["business_type"] = business_type
        lead_data["team_size"] = team_size
        lead_data["tools"] = tools

        qualified = True

# Conversation Summary
summary_prompt = f"""
Summarize this customer conversation.

Conversation:
{conversation}

Lead Data:
{lead_data}

Return:
1. Customer Intent
2. Key Details
3. Escalation Reason
4. Recommended Next Action
"""

summary_response = client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": summary_prompt
        }
    ]
)

summary = summary_response.choices[0].message.content

print("\n===== Conversation Summary =====\n")
print(summary)

print("\nConversation Ended")