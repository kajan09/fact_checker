from flask import Flask, request, render_template_string, session
import os
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    get_response_synthesizer,
    PromptTemplate,
)
import llama_index
print(dir(llama_index.core.chat_engine.types))
from llama_index.core.chat_engine import CondenseQuestionChatEngine, SimpleChatEngine
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.ollama import Ollama

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

STORAGE_DIR = "/mnt/ssd/00_Dominik/storage/256"
DATA_DIR = "/mnt/ssd/00_Dominik/data"

Settings.embed_model = OllamaEmbedding(model_name="mxbai-embed-large")
Settings.llm = Ollama(model="gemma3:12b", request_timeout=300.0)
storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)


def initialize_index():
    global index
    if os.path.exists(STORAGE_DIR):
        index = load_index_from_storage(storage_context, verbose=True)
        print(len(index.docstore.docs))
    else:
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        index = VectorStoreIndex.from_documents(
            documents=documents,
            max_triplets_per_chunk=5,
            storage_context=storage_context,
            include_embeddings=True
        )
        # Persist index
        index.storage_context.persist()
    return index


def setup_chat_engine(index):
    global chat_engine
    def load_template(filename):
        with open(filename, 'r') as file:
            return file.read()
    
    text_qa_template_str = load_template('templates.txt')
    refine_template_str = load_template('templates.txt')

    text_qa_template = PromptTemplate(text_qa_template_str)
    refine_template = PromptTemplate(refine_template_str)

    retriever = index.as_retriever(similarity_top_k=4, verbose=True)
    response_synthesizer = get_response_synthesizer(
        response_mode="compact",
        verbose=True,
        text_qa_template=text_qa_template,
        refine_template=refine_template
    )

    query_engine = CitationQueryEngine.from_args(
        index,
        citation_chunk_size=256,
        verbose=True,
        response_synthesizer=response_synthesizer,
        retriever=retriever
    )
    custom_chat_history = [
        ChatMessage(
            role=MessageRole.USER,
            content="Hello",
        ),
        ChatMessage(role=MessageRole.ASSISTANT, content="Hello"),
    ]

    chat_engine = SimpleChatEngine.from_defaults(
        query_engine=query_engine,
        condense_question_prompt=text_qa_template,
        chat_history=custom_chat_history,
        verbose=True,
    )

    return chat_engine

@app.route("/", methods=["GET", "POST"])
def home():
    if 'chat_history' not in session:
        print('generation of chat history')
        session['chat_history'] = []
    chat_history = session['chat_history']
    #chat_engine.chat_history = chat_history
    if request.method == "POST":
        user_message = request.form.get("query_text", None)
        if user_message:
            try:
                # Add user message to the chat history
                chat_history.append({"sender": "user", "message": user_message})

                # Generate bot response
                response = chat_engine.chat(user_message)
                bot_message = response.response

                # Add bot response
                chat_history.append({"sender": "bot", "message": bot_message})

                # Re-assign to session to ensure it's saved
                session['chat_history'] = chat_history

            except Exception as e:
                bot_message = str(e)
                session['chat_history'].append({"sender": "bot", "message": bot_message})
            
    return render_template_string(template, chat_history=session.get('chat_history', []))

# HTML template with chat form
template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat with LLamaIndex</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 50px; }
    .container { max-width: 1000px; margin: auto; }
    .chat-form { margin-bottom: 20px; }
    .chat-box { background-color: #f9f9f9; padding: 10px; border: 1px solid #ddd; height: 800px; overflow-y: scroll; }
    .chat-entry { margin-bottom: 10px; }
    .chat-entry.user { text-align: right; }
    .chat-entry.bot { text-align: left; }
  </style>
  <script>
    function scrollToBottom() {
      var chatBox = document.getElementById("chat-box");
      chatBox.scrollTop = chatBox.scrollHeight;
    }
    window.onload = scrollToBottom;
  </script>
</head>
<body>
  <div class="container">
    <h1>Chat with Kidneychat</h1>
    <div id="chat-box" class="chat-box">
      {% for entry in chat_history %}
        <div class="chat-entry {{ entry.sender }}">
          <p>{{ entry.message }}</p>
        </div>
      {% endfor %}
    </div>
    <form method="POST" class="chat-form">
      <label for="query_text">Your message:</label><br>
      <input type="text" id="query_text" name="query_text" required style="width: 100%; padding: 8px; margin-top: 5px;"><br>
      <button type="submit" style="margin-top: 10px; padding: 10px 15px;">Send</button>
    </form>
  </div>
</body>
</html>
"""

if __name__ == "__main__":
    # Initialize the index before starting the website
    index=initialize_index()
    setup_chat_engine(index)
    app.run(host="0.0.0.0", port=5600)
