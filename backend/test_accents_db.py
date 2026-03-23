from src.crud import crud_chat
from src.schemas.chat_schema import MessageCreate, SessionCreate
from src.api.dependencies import get_db
import uuid

db = next(get_db())

# Create session
user_id = uuid.uuid4()
sess = crud_chat.create_session(db, SessionCreate(user_id=user_id, title="Test Accents"))
print(f"Session Title: {sess.title}")

# Create message
content = "Xin chào, Tôi muốn xem giá mã FPT."
msg = crud_chat.create_message(db, sess.id, MessageCreate(role="user", content=content))
print(f"Saved content: {msg.content}")

# Read back
msgs = crud_chat.get_messages(db, sess.id)
print(f"Read content: {msgs[0].content}")

assert msgs[0].content == content, "Accent mismatch!"
print("Success! Accents preserved in DB.")
