import asyncio
from dotenv import load_dotenv
load_dotenv()

from tools.gmail_mcp import send_email

async def test():
    print("Testing Gmail connection...\n")

    # Send a test email to yourself
    print("Sending test email...")
    success = await send_email(
        to="likithyadav123ab@gmail.com",
        subject="InvoiceIQ Test — Gmail MCP Working!",
        body=(
            "Hello!\n\n"
            "This is a test email from InvoiceIQ.\n\n"
            "If you received this, your Gmail MCP is working perfectly.\n\n"
            "Your system can now send real payment reminder emails automatically!\n\n"
            "- InvoiceIQ"
        )
    )

    if success:
        print("Email sent successfully!")
        print("Check your Gmail inbox for the test email.")
    else:
        print("Email failed — check the error above.")

asyncio.run(test())