import asyncio
from dotenv import load_dotenv
load_dotenv()

from agents.invoice_generator import invoice_generator_agent
from tools.database import save_invoice, get_invoice

async def test():
    print("Testing Invoice Generator + Database save...\n")
    
    message = "Invoice Acme Corp Rs.45000 for web design project, due in 30 days"
    
    print("Step 1 - Generating invoice from message...")
    invoice = await invoice_generator_agent(message)
    print(f"  Invoice ID: {invoice['invoice_id']}")
    print(f"  Client: {invoice['client_name']}")
    print(f"  Amount: {invoice['currency']} {invoice['amount']}")
    print(f"  Due date: {invoice['due_date']}")
    print()
    
    print("Step 2 - Saving to Firestore...")
    save_invoice(invoice)
    print("  Saved!")
    print()
    
    print("Step 3 - Reading back from Firestore...")
    saved = get_invoice(invoice['invoice_id'])
    print(f"  Retrieved: {saved['invoice_id']} - {saved['client_name']} - {saved['status']}")
    print()
    
    print("All good! Invoice Generator + Database working perfectly.")

asyncio.run(test())