import reflex as rx
from app.state import EstadoChat, Mensaje


# ── Paleta ────────────────────────────────────────────────────────────────────
VERDE      = "#00FF9C"
VERDE_DIM  = "#00C97A"
FONDO      = "#0D0D0D"
SUPERFICIE = "#141414"
BORDE      = "#1E1E1E"
TEXTO      = "#E2E2E2"
TEXTO_DIM  = "#666666"
ACENTO     = "#00FF9C22"

# ── Componentes ───────────────────────────────────────────────────────────────

def burbuja_usuario(msg: Mensaje) -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(msg.contenido, color=FONDO, font_size="0.9rem", line_height="1.6"),
            background=VERDE,
            border_radius="14px 14px 2px 14px",
            padding="12px 16px",
            max_width="75%",
        ),
        display="flex",
        justify_content="flex-end",
        margin_bottom="8px",
    )


def burbuja_asistente(msg: Mensaje) -> rx.Component:
    return rx.box(
        rx.box(
            rx.markdown(
                msg.contenido,
                color=TEXTO,
                font_size="0.88rem",
                line_height="1.7",
            ),
            background=SUPERFICIE,
            border="1px solid",
            border_color=BORDE,
            border_radius="14px 14px 14px 2px",
            padding="12px 16px",
            max_width="85%",
        ),
        display="flex",
        justify_content="flex-start",
        margin_bottom="8px",
    )


def indicador_escritura() -> rx.Component:
    return rx.cond(
        EstadoChat.cargando,
        rx.box(
            rx.box(
                rx.text("Buscando en documentos...", color=VERDE, font_size="0.8rem"),
                background=SUPERFICIE,
                border="1px solid",
                border_color=VERDE_DIM,
                border_radius="14px 14px 14px 2px",
                padding="10px 16px",
            ),
            display="flex",
            justify_content="flex-start",
            margin_bottom="8px",
        ),
    )


def encabezado() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.text(
                    "RAG",
                    color=VERDE,
                    font_size="1.1rem",
                    font_weight="700",
                    font_family="'JetBrains Mono', monospace",
                ),
                rx.text(
                    "Ciberseguridad",
                    color=TEXTO,
                    font_size="0.75rem",
                    font_family="'JetBrains Mono', monospace",
                ),
            ),
            rx.spacer(),
            rx.cond(
                EstadoChat.indexado,
                rx.badge(
                    EstadoChat.info_indice,
                    background=ACENTO,
                    color=VERDE,
                    border="1px solid",
                    border_color=VERDE_DIM,
                    font_size="0.7rem",
                    padding="4px 10px",
                    border_radius="20px",
                ),
            ),
            rx.button(
                "Limpiar",
                on_click=EstadoChat.limpiar_chat,
                background="transparent",
                color=TEXTO_DIM,
                border="1px solid",
                border_color=BORDE,
                border_radius="6px",
                font_size="0.75rem",
                padding="4px 12px",
                cursor="pointer",
                _hover={"color": TEXTO, "border_color": TEXTO_DIM},
            ),
            width="100%",
            align="center",
        ),
        background=SUPERFICIE,
        border_bottom="1px solid",
        border_color=BORDE,
        padding="14px 20px",
        position="sticky",
        top="0",
        z_index="10",
    )


def area_chat() -> rx.Component:
    return rx.box(
        rx.foreach(
            EstadoChat.mensajes,
            lambda msg: rx.cond(
                msg.rol == "usuario",
                burbuja_usuario(msg),
                burbuja_asistente(msg),
            ),
        ),
        indicador_escritura(),
        flex="1",
        overflow_y="auto",
        padding="20px",
        display="flex",
        flex_direction="column",
    )


def sugerencias() -> rx.Component:
    preguntas = [
        "¿Qué es un ataque phishing?",
        "¿Qué es SQL Injection?",
        "¿Qué recomienda OWASP?",
        "¿Qué es la ingeniería social?",
    ]
    return rx.cond(
        EstadoChat.mensajes == [],
        rx.box(
            rx.text(
                "Preguntas de ejemplo",
                color=TEXTO_DIM,
                font_size="0.75rem",
                margin_bottom="10px",
                font_family="'JetBrains Mono', monospace",
            ),
            rx.flex(
                *[
                    rx.button(
                        p,
                        on_click=lambda p=p: EstadoChat.set_entrada(p),
                        background="transparent",
                        color=TEXTO_DIM,
                        border="1px solid",
                        border_color=BORDE,
                        border_radius="20px",
                        font_size="0.78rem",
                        padding="6px 14px",
                        cursor="pointer",
                        _hover={
                            "color": VERDE,
                            "border_color": VERDE_DIM,
                            "background": ACENTO,
                        },
                    )
                    for p in preguntas
                ],
                flex_wrap="wrap",
                gap="8px",
            ),
            padding="0 20px 16px",
        ),
    )


def entrada_chat() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.input(
                placeholder="Escribe tu pregunta sobre ciberseguridad...",
                value=EstadoChat.entrada,
                on_change=EstadoChat.set_entrada,
                on_key_down=lambda e: rx.cond(
                    e == "Enter",
                    EstadoChat.enviar(),
                    rx.noop(),
                ),
                background=SUPERFICIE,
                border="1px solid",
                border_color=BORDE,
                color=TEXTO,
                border_radius="10px",
                padding="12px 16px",
                font_size="0.9rem",
                flex="1",
                _focus={
                    "border_color": VERDE_DIM,
                    "outline": "none",
                    "box_shadow": f"0 0 0 2px {ACENTO}",
                },
                _placeholder={"color": TEXTO_DIM},
            ),
            rx.button(
                rx.text("→", font_size="1.2rem"),
                on_click=EstadoChat.enviar,
                background=VERDE,
                color=FONDO,
                border_radius="10px",
                padding="12px 18px",
                font_weight="700",
                cursor="pointer",
                is_disabled=EstadoChat.cargando,
                _hover={"background": VERDE_DIM},
                _disabled={"opacity": "0.4", "cursor": "not-allowed"},
            ),
            width="100%",
            gap="10px",
        ),
        border_top="1px solid",
        border_color=BORDE,
        padding="14px 20px",
        background=FONDO,
    )


# ── Página principal ──────────────────────────────────────────────────────────

def index() -> rx.Component:
    return rx.box(
        rx.el.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap",
        ),
        encabezado(),
        rx.box(
            area_chat(),
            sugerencias(),
            entrada_chat(),
            display="flex",
            flex_direction="column",
            height="calc(100vh - 57px)",
        ),
        background=FONDO,
        color=TEXTO,
        font_family="'JetBrains Mono', monospace",
        min_height="100vh",
        on_mount=EstadoChat.iniciar,
    )


# ── App ───────────────────────────────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(appearance="dark"),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"
    ],
)
app.add_page(index, route="/", title="RAG Ciberseguridad")