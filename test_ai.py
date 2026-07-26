from ai_model import find_answer


document = """
SQL Injection is a technique used to attack databases.

XSS is a security vulnerability that allows attackers to inject malicious scripts into web pages.

A firewall is a network security device that monitors and controls incoming and outgoing network traffic.
"""

question = "How can attackers attack databases?"

answer = find_answer(document, question)

print("Question:")
print(question)

print("\nAI Answer:")
print(answer)