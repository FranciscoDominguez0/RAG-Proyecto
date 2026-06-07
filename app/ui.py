import reflex as rx
from app.state import AppState, ChatMessage

# Paleta de colores
C = {
    "bg_base":      "#0d0f14",
    "bg_sidebar":   "#111318",
    "bg_surface":   "#181b22",
    "bg_input":     "#1c1f28",
    "bg_user":      "#1e3a5f",
    "border":       "#252933",
    "border_light": "#2e3340",
    "accent":       "#3b82f6",
    "accent_dim":   "#1d4ed8",
    "text_primary": "#e8eaf0",
    "text_muted":   "#6b7280",
    "text_dim":     "#4b5563",
    "green":        "#10b981",
    "green_dim":    "#064e3b",
    "amber":        "#f59e0b",
}

FONT_SANS = "'IBM Plex Sans', sans-serif"
FONT_MONO = "'IBM Plex Mono', monospace"


# ─── Componentes de mensaje ───────────────────────────

def source_tag(source: str) -> rx.Component:
    return rx.box(
        rx.text(source, size="1", style={"font_family": FONT_MONO, "color": C["text_muted"]}),
        style={
            "padding": "2px 8px",
            "background": C["bg_input"],
            "border": f"1px solid {C['border_light']}",
            "border_radius": "4px",
        }
    )


def user_message(msg: ChatMessage) -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(
                msg.content,
                size="3",
                style={"color": C["text_primary"], "line_height": "1.65", "font_family": FONT_SANS}
            ),
            style={
                "background": C["bg_user"],
                "border": f"1px solid #1e4080",
                "border_radius": "12px 12px 4px 12px",
                "padding": "12px 16px",
                "max_width": "70%",
            }
        ),
        style={"display": "flex", "justify_content": "flex-end", "width": "100%", "margin_bottom": "4px"}
    )


def assistant_message(msg: ChatMessage) -> rx.Component:
    return rx.box(
        rx.box(
            # Indicador lateral
            rx.box(
                style={
                    "width": "3px",
                    "min_height": "100%",
                    "background": C["accent"],
                    "border_radius": "2px",
                    "flex_shrink": "0",
                }
            ),
            # Contenido
            rx.box(
                rx.markdown(
                    msg.content,
                    component_map={
                        "p": lambda text: rx.text(
                            text,
                            size="3",
                            style={
                                "color": C["text_primary"],
                                "line_height": "1.65",
                                "font_family": FONT_SANS,
                                "margin_bottom": "8px",
                            }
                        ),
                        "code": lambda text: rx.code(
                            text,
                            style={
                                "font_family": FONT_MONO,
                                "font_size": "12px",
                                "background": C["bg_input"],
                                "color": C["accent"],
                                "padding": "1px 5px",
                                "border_radius": "3px",
                            }
                        ),
                    }
                ),
                # Fuentes
                rx.cond(
                    msg.sources.length() > 0,
                    rx.box(
                        rx.text(
                            "Fuentes",
                            size="1",
                            style={"color": C["text_dim"], "font_weight": "500", "margin_bottom": "6px", "font_family": FONT_SANS}
                        ),
                        rx.flex(
                            rx.foreach(msg.sources, source_tag),
                            gap="6px",
                            flex_wrap="wrap",
                        ),
                        style={"margin_top": "12px", "padding_top": "12px", "border_top": f"1px solid {C['border']}"}
                    ),
                    rx.box()
                ),
                style={"flex": "1"}
            ),
            style={
                "display": "flex",
                "gap": "14px",
                "align_items": "stretch",
                "background": C["bg_surface"],
                "border": f"1px solid {C['border']}",
                "border_radius": "4px 12px 12px 12px",
                "padding": "14px 18px",
                "max_width": "85%",
            }
        ),
        style={"display": "flex", "justify_content": "flex-start", "width": "100%", "margin_bottom": "4px"}
    )


def message_item(msg: ChatMessage) -> rx.Component:
    return rx.cond(
        msg.role == "user",
        user_message(msg),
        assistant_message(msg),
    )


# ─── Indicador de carga ───────────────────────────────

def loading_indicator() -> rx.Component:
    return rx.cond(
        AppState.is_loading,
        rx.box(
            rx.box(
                rx.box(style={"width": "3px", "background": C["accent"], "border_radius": "2px", "flex_shrink": "0"}),
                rx.flex(
                    rx.spinner(size="1", style={"color": C["accent"]}),
                    rx.text(
                        "Consultando base de conocimiento...",
                        size="2",
                        style={"color": C["text_muted"], "font_family": FONT_SANS}
                    ),
                    align="center",
                    gap="10px",
                ),
                style={
                    "display": "flex",
                    "gap": "14px",
                    "align_items": "center",
                    "background": C["bg_surface"],
                    "border": f"1px solid {C['border']}",
                    "border_radius": "4px 12px 12px 12px",
                    "padding": "14px 18px",
                }
            ),
            style={"display": "flex", "justify_content": "flex-start", "width": "100%", "margin_bottom": "4px"}
        ),
        rx.box()
    )


# ─── Estado vacío ─────────────────────────────────────

def empty_state() -> rx.Component:
    return rx.cond(
        AppState.messages.length() == 0,
        rx.box(
            rx.vstack(
                rx.box(
                    style={
                        "width": "48px",
                        "height": "3px",
                        "background": C["accent"],
                        "border_radius": "2px",
                        "margin_bottom": "24px",
                    }
                ),
                rx.text(
                    "Consultor de Ciberseguridad",
                    style={
                        "font_size": "22px",
                        "font_weight": "600",
                        "color": C["text_primary"],
                        "font_family": FONT_SANS,
                        "letter_spacing": "-0.02em",
                    }
                ),
                rx.text(
                    "Haz una pregunta basada en los documentos de seguridad cargados.",
                    size="3",
                    style={"color": C["text_muted"], "font_family": FONT_SANS, "text_align": "center", "max_width": "400px"}
                ),
                rx.cond(
                    AppState.is_indexing,
                    rx.flex(
                        rx.spinner(size="1", style={"color": C["accent"]}),
                        rx.text("Indexando documentos...", size="2", style={"color": C["text_muted"], "font_family": FONT_SANS}),
                        align="center",
                        gap="8px",
                        style={"margin_top": "16px"}
                    ),
                    rx.box()
                ),
                align="center",
                spacing="3",
            ),
            style={
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "height": "100%",
                "min_height": "400px",
            }
        ),
        rx.box()
    )


# ─── Sidebar ──────────────────────────────────────────

SAMPLE_QUESTIONS = [
    "Que es un ataque de phishing?",
    "Que es ransomware?",
    "Como funciona la autenticacion multifactor?",
    "Como gestionar una vulnerabilidad critica?",
    "Que controles recomienda ISO 27001?",
]


def sidebar() -> rx.Component:
    return rx.box(
        # Titulo
        rx.box(
            rx.box(style={"width": "3px", "height": "20px", "background": C["accent"], "border_radius": "2px"}),
            rx.text(
                "CiberRAG",
                style={
                    "font_size": "15px",
                    "font_weight": "600",
                    "color": C["text_primary"],
                    "font_family": FONT_SANS,
                    "letter_spacing": "-0.01em",
                }
            ),
            style={"display": "flex", "align_items": "center", "gap": "10px", "margin_bottom": "28px"}
        ),

        # Estado del sistema
        rx.box(
            rx.text("BASE DE CONOCIMIENTO", size="1", style={"color": C["text_dim"], "letter_spacing": "0.08em", "font_family": FONT_SANS, "font_weight": "600", "margin_bottom": "8px"}),
            rx.box(
                rx.box(
                    style={
                        "width": "7px",
                        "height": "7px",
                        "border_radius": "50%",
                        "background": rx.cond(AppState.db_ready, C["green"], C["amber"]),
                        "flex_shrink": "0",
                    }
                ),
                rx.text(
                    rx.cond(AppState.db_ready, "Activa", "Sin datos"),
                    size="2",
                    style={"color": rx.cond(AppState.db_ready, C["green"], C["amber"]), "font_family": FONT_SANS, "font_weight": "500"}
                ),
                style={"display": "flex", "align_items": "center", "gap": "8px", "margin_bottom": "6px"}
            ),
            rx.text(
                AppState.status_message,
                size="1",
                style={"color": C["text_dim"], "font_family": FONT_MONO, "line_height": "1.5"}
            ),
            style={
                "padding": "14px",
                "background": C["bg_input"],
                "border": f"1px solid {C['border']}",
                "border_radius": "8px",
                "margin_bottom": "20px",
            }
        ),

        # Acciones
        rx.box(
            rx.text("ACCIONES", size="1", style={"color": C["text_dim"], "letter_spacing": "0.08em", "font_family": FONT_SANS, "font_weight": "600", "margin_bottom": "8px"}),
            rx.vstack(
                rx.button(
                    "Recargar documentos",
                    on_click=AppState.reload_documents,
                    loading=AppState.is_indexing,
                    style={
                        "width": "100%",
                        "background": C["bg_input"],
                        "color": C["text_primary"],
                        "border": f"1px solid {C['border_light']}",
                        "border_radius": "6px",
                        "padding": "8px 12px",
                        "font_size": "13px",
                        "font_family": FONT_SANS,
                        "cursor": "pointer",
                        "text_align": "left",
                    }
                ),
                rx.button(
                    "Limpiar conversacion",
                    on_click=AppState.clear_chat,
                    style={
                        "width": "100%",
                        "background": "transparent",
                        "color": C["text_muted"],
                        "border": f"1px solid {C['border']}",
                        "border_radius": "6px",
                        "padding": "8px 12px",
                        "font_size": "13px",
                        "font_family": FONT_SANS,
                        "cursor": "pointer",
                        "text_align": "left",
                    }
                ),
                spacing="2",
            ),
            style={"margin_bottom": "24px"}
        ),

        # Preguntas de ejemplo
        rx.box(
            rx.text("EJEMPLOS", size="1", style={"color": C["text_dim"], "letter_spacing": "0.08em", "font_family": FONT_SANS, "font_weight": "600", "margin_bottom": "8px"}),
            rx.vstack(
                *[
                    rx.button(
                        q,
                        on_click=AppState.set_input(q),
                        style={
                            "width": "100%",
                            "background": "transparent",
                            "color": C["text_muted"],
                            "border": "none",
                            "border_radius": "6px",
                            "padding": "7px 10px",
                            "font_size": "12px",
                            "font_family": FONT_SANS,
                            "cursor": "pointer",
                            "text_align": "left",
                            "_hover": {"background": C["bg_input"], "color": C["text_primary"]},
                        }
                    )
                    for q in SAMPLE_QUESTIONS
                ],
                spacing="1",
            )
        ),

        style={
            "width": "260px",
            "min_width": "260px",
            "background": C["bg_sidebar"],
            "border_right": f"1px solid {C['border']}",
            "padding": "24px 16px",
            "height": "100vh",
            "overflow_y": "auto",
            "position": "sticky",
            "top": "0",
        }
    )


# ─── Area de chat ─────────────────────────────────────

def chat_input() -> rx.Component:
    return rx.box(
        rx.box(
            rx.flex(
                rx.text_area(
                    placeholder="Escribe tu consulta de ciberseguridad...",
                    value=AppState.user_input,
                    on_change=AppState.set_input,
                    on_key_down=AppState.handle_key_press,
                    rows="1",
                    style={
                        "flex": "1",
                        "background": C["bg_input"],
                        "color": C["text_primary"],
                        "border": f"1px solid {C['border_light']}",
                        "border_radius": "8px",
                        "padding": "12px 14px",
                        "font_size": "14px",
                        "font_family": FONT_SANS,
                        "resize": "none",
                        "outline": "none",
                        "_placeholder": {"color": C["text_dim"]},
                        "_focus": {"border_color": C["accent"]},
                    }
                ),
                rx.button(
                    rx.icon("arrow-up", size=16),
                    on_click=AppState.send_message,
                    loading=AppState.is_loading,
                    disabled=AppState.user_input.length() == 0,
                    style={
                        "background": C["accent"],
                        "color": "white",
                        "border": "none",
                        "border_radius": "8px",
                        "width": "40px",
                        "height": "40px",
                        "cursor": "pointer",
                        "flex_shrink": "0",
                        "_hover": {"background": C["accent_dim"]},
                        "_disabled": {"background": C["bg_input"], "color": C["text_dim"], "cursor": "not-allowed"},
                    }
                ),
                gap="10px",
                align_items="flex-end",
            ),
            rx.text(
                "Responde unicamente con base en los documentos cargados.",
                size="1",
                style={"color": C["text_dim"], "font_family": FONT_SANS, "margin_top": "8px", "text_align": "center"}
            ),
            style={"max_width": "820px", "margin": "0 auto"}
        ),
        style={
            "padding": "14px 24px 20px",
            "background": C["bg_base"],
            "border_top": f"1px solid {C['border']}",
            "position": "sticky",
            "bottom": "0",
        }
    )


def chat_area() -> rx.Component:
    return rx.box(
        # Mensajes
        rx.box(
            empty_state(),
            rx.foreach(AppState.messages, message_item),
            loading_indicator(),
            style={
                "padding": "28px 24px",
                "max_width": "820px",
                "margin": "0 auto",
                "min_height": "calc(100vh - 100px)",
            }
        ),
        chat_input(),
        style={
            "flex": "1",
            "overflow_y": "auto",
            "background": C["bg_base"],
            "display": "flex",
            "flex_direction": "column",
            "justify_content": "space-between",
        }
    )


# ─── Pagina principal ────────────────────────────────

def index() -> rx.Component:
    return rx.box(
        rx.flex(
            sidebar(),
            chat_area(),
            direction="row",
            style={"height": "100vh", "overflow": "hidden"}
        ),
        style={"background": C["bg_base"], "min_height": "100vh"}
    )