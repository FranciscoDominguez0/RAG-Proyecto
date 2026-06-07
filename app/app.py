import reflex as rx
from app.ui import index
from app.state import AppState

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap"
    ],
    style={"background": "#0d0f14"}
)

app.add_page(
    index,
    route="/",
    title="Consultor de Ciberseguridad IA",
    on_load=AppState.initialize_system,
)