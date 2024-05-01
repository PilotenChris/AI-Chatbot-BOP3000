import uuid

def start_new_session():
    sessionId = str(uuid.uuid4())
    return sessionId