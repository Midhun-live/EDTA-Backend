from fastapi_mail import MessageSchema
from fastapi import UploadFile
from io import BytesIO

try:
    f = UploadFile(filename="test.pdf", file=BytesIO(b"dummy"), headers={"content-type": "application/pdf"})
    msg = MessageSchema(
        subject="Test",
        recipients=["test@example.com"],
        body="Body",
        subtype="html",
        attachments=[f]
    )
    print("UploadFile success!")
except Exception as e:
    print("UploadFile failed:", e)

