
"""
Azure AI Foundry Agent – Creation & Test Script
Team Name: GenisisFlow
Use case: Automated Issue Triage & Categorization
"""

import os
import time
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

load_dotenv()

def main():
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    endpoint = os.getenv("PROJECT_ENDPOINT")

    if not all([tenant_id, client_id, client_secret, endpoint]):
        raise ValueError("Missing required environment variables")

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

    project = AIProjectClient(
        credential=credential,
        endpoint=endpoint
    )

    print("Connected to Azure AI Foundry")

    agent = project.agents.create_agent(
        model="gpt-4o-mini",
        name="GenisisFlow",
        instructions=(
            "You are an AI agent that performs automated issue triage. "
            "Classify support tickets, suggest priority, and help route issues."
        )
    )

    print(f"AGENT CREATED")
    print(f"Agent Name: {agent.name}")
    print(f"Agent ID: {agent.id}")
    print("SAVE THIS AGENT ID")

    thread = project.agents.threads.create()

    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="User cannot login and receives 401 unauthorized error."
    )

    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )

    while run.status not in ("completed", "failed"):
        time.sleep(1)
        run = project.agents.runs.get(
            thread_id=thread.id,
            run_id=run.id
        )

    if run.status == "completed":
        messages = project.agents.messages.list(thread_id=thread.id)
        for msg in messages:
            if msg.role == "assistant":
                print("Agent Response:")
                print(msg.content[0].text)
    else:
        print("Agent run failed")

if __name__ == "__main__":
    main()
