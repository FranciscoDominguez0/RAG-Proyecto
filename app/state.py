import asyncio
import reflex as rx
from pydantic import BaseModel
from typing import List, Dict, Any
from app.rag_engine import load_and_index_documents, generate_rag_response


class ChatMessage(BaseModel):
    role: str
    content: str
    sources: List[str] = []


class AppState(rx.State):
    messages: List[ChatMessage] = []
    user_input: str = ""
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
                self.status_message = (
                    f"{stats.get('files_processed', 0)} archivo(s) — "
                    f"{stats['total_chunks']} fragmentos indexados"
                )
            else:
                self.db_ready = False
                self.status_message = "Sin documentos. Agrega archivos a /documentos y recarga."
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

        self.messages.append(ChatMessage(role="user", content=question))
        self.user_input = ""
        self.is_loading = True
        yield

        if not self.db_ready:
            self.messages.append(ChatMessage(
                role="assistant",
                content="La base de conocimiento no esta disponible. Verifica que existan documentos en /documentos."
            ))
            self.is_loading = False
            yield
            return

        try:
            answer, retrieved = await asyncio.to_thread(
                generate_rag_response, question
            )
            sources = list({doc["metadata"].get("source", "") for doc in retrieved})
            self.messages.append(ChatMessage(
                role="assistant",
                content=answer,
                sources=sources
            ))
        except Exception as e:
            self.messages.append(ChatMessage(
                role="assistant",
                content=f"Error al generar respuesta: {str(e)}. Verifica que Ollama este corriendo."
            ))

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
        self.status_message = "Recargando documentos..."
        yield
        try:
            stats = await asyncio.to_thread(load_and_index_documents, True)
            self.db_stats = stats
            if stats.get("total_chunks", 0) > 0:
                self.db_ready = True
                self.status_message = (
                    f"{stats.get('files_processed', 0)} archivo(s) — "
                    f"{stats['total_chunks']} fragmentos indexados"
                )
            else:
                self.db_ready = False
                self.status_message = "No se encontraron documentos."
        except Exception as e:
            self.status_message = f"Error: {str(e)}"
        self.is_indexing = False
        yield