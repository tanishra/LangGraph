import streamlit as st
from db_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# *************************************************** utility functions ****************************************

def generate_thread_id():
    return uuid.uuid4()  # thread_id

def new_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id, title="New Chat")
    st.session_state['message_history'] = []

def add_thread(thread_id, title="New Chat"):
    for thread in st.session_state['chat_threads']:
        if thread['thread_id'] == thread_id:
            return
    
    st.session_state['chat_threads'].append({
        'thread_id': thread_id,
        'title': title
    })

def load_conversation(thread_id):
    state = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )

    return state.values.get('messages', [])

def generate_chat_title(message, max_len=40):
    return message[:max_len] + "..." if len(message) > max_len else message

# **************************************************** Session ***************************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()
    # [
    #   {
    #       "thread_id": UUID,
    #       "title": "Chat title"
    #   }
    # ]

add_thread(st.session_state['thread_id'])

# *************************************************** Sidebar UI ***********************************************

st.sidebar.title("ChatNode")

if st.sidebar.button("New Chat"):
    new_chat()

st.sidebar.header("Your Chats")

for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread['title'], key=str(thread['thread_id'])):
        st.session_state['thread_id'] = thread['thread_id']
        messages = load_conversation(thread['thread_id'])

        temp_messages = []
        for message in messages:
            role = 'user' if isinstance(message, HumanMessage) else 'assistant'
            temp_messages.append({
                'role': role,
                'content': message.content
            })
        
        st.session_state['message_history'] = temp_messages

# *************************************************** Main UI ***************************************************

# Loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input("Type here")

if user_input:
    # Store user message
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    # Update chat title if this is the first user message
    if len(st.session_state['message_history']) == 1:
        title = generate_chat_title(user_input)
        for thread in st.session_state['chat_threads']:
            if thread['thread_id'] == st.session_state['thread_id']:
                thread['title'] = title
                break

    with st.chat_message('user'):
        st.text(user_input)
    
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
    
    # Store AI message
    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message
    })