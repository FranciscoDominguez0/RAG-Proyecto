import asyncio
import reflex as rx
from pydantic import BaseModel
from typing import List, Dict, Any
from app.rag_engine import load_and_index_documents, search_only, stream_response


class ChatMessage(BaseModel):
    role: str
    content: str
    sources: List[str] = []


class AppState(rx.State):
    messages: List[ChatMessage] = []
    user_input: str = ""
    input_key: int = 0
    is_loading: bool = False
    is_indexing: bool = False
    db_ready: bool = False
    db_stats: Dict[str, Any] = {}
    status_message: str = "Iniciando..."

    @rx.event
    async def initialize_system(self):
        self.is_indexing = True
        self.status_message = "Indexando documentos..."
        yield
        try:
            stats = await asyncio.to_thread(load_and_index_documents)
            self.db_stats = stats
            if stats.get("total_chunks", 0) > 0:
                self.db_ready = True
                self.status_message = f"{stats.get('files_processed', 0)} archivo(s) — {stats['total_chunks']} fragmentos"
            else:
                self.db_ready = False
                self.status_message = "Sin documentos en /documentos"
        except Exception as e:
            self.db_ready = False
            self.status_message = f"Error: {str(e)}"
        self.is_indexing = False
        yield

    @rx.event
    async def send_message(self):
        question = self.user_input.strip()
        if not question or self.is_loading:
            return
        self.user_input = ""
        self.input_key += 1
        self.is_loading = True
        self.messages.append(ChatMessage(role="user", content=question))
        yield

        if not self.db_ready:
            self.messages.append(ChatMessage(role="assistant",
                content="Base de conocimiento no disponible. Verifica los documentos en /documentos."))
            self.is_loading = False
            yield
            return

        try:
            retrieved = await asyncio.to_thread(search_only, question)
            sources = list({d["metadata"].get("source", "") for d in retrieved})
            self.messages.append(ChatMessage(role="assistant", content="", sources=sources))
            yield
            tokens = await asyncio.to_thread(lambda: list(stream_response(question, retrieved)))
            for token in tokens:
                self.messages[-1].content += token
                yield
        except Exception as e:
            self.messages.append(ChatMessage(role="assistant",
                content=f"Error: {str(e)}"))

        self.is_loading = False
        yield

    @rx.event
    def set_input(self, value: str):
        self.user_input = value

    @rx.event
    def clear_chat(self):
        self.messages = []

    @rx.event
    async def handle_key_press(self, key: str):
        if key == "Enter":
            yield AppState.send_message()

    @rx.event
    async def reload_documents(self):
        self.is_indexing = True
        self.status_message = "Recargando..."
        yield
        try:
            stats = await asyncio.to_thread(load_and_index_documents, True)
            self.db_stats = stats
            if stats.get("total_chunks", 0) > 0:
                self.db_ready = True
                self.status_message = f"{stats.get('files_processed', 0)} archivo(s) — {stats['total_chunks']} fragmentos"
            else:
                self.db_ready = False
                self.status_message = "No se encontraron documentos."
        except Exception as e:
            self.status_message = f"Error: {str(e)}"
        self.is_indexing = False
        yield