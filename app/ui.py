import reflex as rx
from app.state import AppState, ChatMessage

BG       = "#0a0c10"
SURFACE  = "#13161f"
INPUT    = "#1c2030"
BORDER   = "#252a38"
ACCENT   = "#4f8ef7"
TEXT     = "#dde1ed"
MUTED    = "#606680"
DIM      = "#363c54"
GREEN    = "#22c97a"
AMBER    = "#f0a832"
SANS     = "'IBM Plex Sans', sans-serif"
MONO     = "'IBM Plex Mono', monospace"

EXAMPLES = [
    "Que es un ataque de phishing?",
    "Que es ransomware?",
    "Como funciona MFA?",
    "Como gestionar una vulnerabilidad critica?",
    "Controles ISO 27001?",
]


def user_msg(msg: ChatMessage):
    return rx.box(
        rx.text(msg.content, style={"color": TEXT, "font_size": "14px",
                                    "line_height": "1.7", "font_family": SANS}),
        style={
            "background": "#162040", "border": "1px solid #1e3a6e",
            "border_radius": "16px 16px 4px 16px",
            "padding": "11px 15px", "max_width": "70%", "align_self": "flex-end",
        }
    )


def assistant_msg(msg: ChatMessage):
    return rx.flex(
        rx.box(style={"width": "2px", "background": ACCENT,
                      "border_radius": "2px", "align_self": "stretch", "flex_shrink": "0"}),
        rx.box(
            rx.markdown(msg.content, component_map={
                "p": lambda t: rx.text(t, style={"color": TEXT, "font_size": "14px",
                                                  "line_height": "1.7", "font_family": SANS,
                                                  "margin_bottom": "4px"}),
                "code": lambda t: rx.code(t, style={"font_family": MONO, "font_size": "12px",
                                                     "background": INPUT, "color": ACCENT,
                                                     "padding": "1px 5px", "border_radius": "3px"}),
            }),
            rx.cond(
                msg.sources.length() > 0,
                rx.box(
                    rx.text("Fuentes", style={"color": DIM, "font_size": "11px",
                                              "font_weight": "600", "font_family": SANS,
                                              "margin_bottom": "5px"}),
                    rx.flex(
                        rx.foreach(msg.sources, lambda s: rx.box(
                            rx.text(s, style={"color": MUTED, "font_size": "11px", "font_family": MONO}),
                            style={"padding": "2px 8px", "background": INPUT,
                                   "border": f"1px solid {BORDER}", "border_radius": "4px"}
                        )),
                        gap="5px", flex_wrap="wrap",
                    ),
                    style={"margin_top": "10px", "padding_top": "10px",
                           "border_top": f"1px solid {BORDER}"}
                ),
                rx.box()
            ),
            style={"flex": "1", "min_width": "0"}
        ),
        gap="12px", align_items="flex-start",
        style={
            "background": SURFACE, "border": f"1px solid {BORDER}",
            "border_radius": "4px 16px 16px 16px",
            "padding": "13px 16px", "max_width": "84%", "align_self": "flex-start",
        }
    )


def message_item(msg: ChatMessage):
    return rx.cond(msg.role == "user", user_msg(msg), assistant_msg(msg))


def sidebar():
    return rx.box(
        # Logo
        rx.flex(
            rx.box(style={"width": "3px", "height": "18px", "background": ACCENT, "border_radius": "2px"}),
            rx.text("CiberRAG", style={"font_size": "15px", "font_weight": "600",
                                       "color": TEXT, "font_family": SANS}),
            align="center", gap="10px", style={"margin_bottom": "26px"}
        ),

        # Estado KB
        rx.box(
            rx.text("BASE DE CONOCIMIENTO", style={"color": DIM, "font_size": "10px",
                                                    "letter_spacing": "0.1em", "font_weight": "600",
                                                    "font_family": SANS, "margin_bottom": "8px"}),
            rx.box(
                rx.flex(
                    rx.box(style={"width": "7px", "height": "7px", "border_radius": "50%", "flex_shrink": "0",
                                  "background": rx.cond(AppState.db_ready, GREEN, AMBER)}),
                    rx.text(rx.cond(AppState.db_ready, "Activa", "Sin datos"),
                            style={"font_size": "13px", "font_weight": "500", "font_family": SANS,
                                   "color": rx.cond(AppState.db_ready, GREEN, AMBER)}),
                    align="center", gap="7px", style={"margin_bottom": "4px"}
                ),
                rx.text(AppState.status_message, style={"color": DIM, "font_size": "11px",
                                                         "font_family": MONO, "line_height": "1.5"}),
                style={"padding": "11px", "background": INPUT, "border": f"1px solid {BORDER}",
                       "border_radius": "8px", "margin_bottom": "18px"}
            ),
        ),

        # Botones
        rx.box(
            rx.text("ACCIONES", style={"color": DIM, "font_size": "10px", "letter_spacing": "0.1em",
                                        "font_weight": "600", "font_family": SANS, "margin_bottom": "8px"}),
            rx.vstack(
                rx.button("↺  Recargar documentos", on_click=AppState.reload_documents,
                          loading=AppState.is_indexing,
                          style={"width": "100%", "background": INPUT, "color": TEXT,
                                 "border": f"1px solid {BORDER}", "border_radius": "6px",
                                 "padding": "8px 12px", "font_size": "13px", "font_family": SANS,
                                 "cursor": "pointer", "text_align": "left"}),
                rx.button("✕  Limpiar conversacion", on_click=AppState.clear_chat,
                          style={"width": "100%", "background": "transparent", "color": MUTED,
                                 "border": f"1px solid {BORDER}", "border_radius": "6px",
                                 "padding": "8px 12px", "font_size": "13px", "font_family": SANS,
                                 "cursor": "pointer", "text_align": "left"}),
                spacing="2", width="100%",
            ),
            style={"margin_bottom": "22px"}
        ),

        # Ejemplos — fix alineación
        rx.box(
            rx.text("EJEMPLOS", style={"color": DIM, "font_size": "10px", "letter_spacing": "0.1em",
                                        "font_weight": "600", "font_family": SANS, "margin_bottom": "8px"}),
            rx.vstack(
                *[rx.button(q, on_click=AppState.set_input(q),
                            style={"width": "100%", "background": "transparent", "color": MUTED,
                                   "border": "none", "border_radius": "5px", "padding": "6px 8px",
                                   "font_size": "12px", "font_family": SANS, "cursor": "pointer",
                                   "text_align": "left", "display": "block",
                                   "_hover": {"background": INPUT, "color": TEXT}})
                  for q in EXAMPLES],
                spacing="1", width="100%",
            )
        ),

        style={
            "width": "235px", "min_width": "235px",
            "background": "#0e1118",
            "border_right": f"1px solid {BORDER}",
            "padding": "20px 14px",
            "height": "100vh", "overflow_y": "auto",
            "display": "flex", "flex_direction": "column",
        }
    )


def chat_input():
    return rx.box(
        rx.flex(
            rx.text_area(
                placeholder="Escribe tu consulta de ciberseguridad...",
                value=AppState.user_input,
                on_change=AppState.set_input,
                on_key_down=AppState.handle_key_press,
                rows="1",
                style={
                    "flex": "1", "background": INPUT, "color": TEXT,
                    "border": f"1px solid {BORDER}", "border_radius": "10px",
                    "padding": "11px 14px", "font_size": "14px", "font_family": SANS,
                    "resize": "none", "outline": "none",
                    "_placeholder": {"color": DIM},
                    "_focus": {"border_color": ACCENT},
                }
            ),
            rx.button(
                rx.icon("arrow-up", size=16),
                on_click=AppState.send_message,
                loading=AppState.is_loading,
                disabled=AppState.user_input.length() == 0,
                style={
                    "background": ACCENT, "color": "white", "border": "none",
                    "border_radius": "10px", "width": "42px", "height": "42px",
                    "cursor": "pointer", "flex_shrink": "0",
                    "_hover": {"background": "#3a7de0"},
                    "_disabled": {"background": INPUT, "color": DIM, "cursor": "not-allowed"},
                }
            ),
            gap="8px", align_items="flex-end",
        ),
        style={
            "padding": "12px 20px 18px",
            "border_top": f"1px solid {BORDER}",
            "background": BG,
            "flex_shrink": "0",
        }
    )


def chat_area():
    return rx.box(
        rx.box(
            rx.cond(
                AppState.messages.length() == 0,
                rx.flex(
                    rx.vstack(
                        rx.box(style={"width": "28px", "height": "2px", "background": ACCENT, "border_radius": "1px"}),
                        rx.text("Consultor de Ciberseguridad",
                                style={"font_size": "19px", "font_weight": "600",
                                       "color": TEXT, "font_family": SANS, "letter_spacing": "-0.02em"}),
                        rx.text("Haz una pregunta basada en los documentos cargados.",
                                style={"color": MUTED, "font_size": "13px", "font_family": SANS}),
                        rx.cond(AppState.is_indexing,
                                rx.flex(rx.spinner(size="1", style={"color": ACCENT}),
                                        rx.text("Indexando...", style={"color": MUTED, "font_size": "13px",
                                                                        "font_family": SANS}),
                                        align="center", gap="8px"),
                                rx.box()),
                        align="center", spacing="3",
                    ),
                    align="center", justify="center", style={"height": "100%"}
                ),
                rx.box()
            ),
            rx.flex(
                rx.foreach(AppState.messages, message_item),
                rx.cond(
                    AppState.is_loading,
                    rx.flex(
                        rx.box(style={"width": "2px", "background": ACCENT, "border_radius": "2px",
                                      "align_self": "stretch", "flex_shrink": "0"}),
                        rx.flex(rx.spinner(size="1", style={"color": ACCENT}),
                                rx.text("Generando respuesta...",
                                        style={"color": MUTED, "font_size": "13px", "font_family": SANS}),
                                align="center", gap="8px"),
                        gap="12px", align_items="center",
                        style={"background": SURFACE, "border": f"1px solid {BORDER}",
                               "border_radius": "4px 16px 16px 16px",
                               "padding": "12px 16px", "max_width": "84%", "align_self": "flex-start"}
                    ),
                    rx.box()
                ),
                direction="column", gap="10px",
            ),
            id="msgs",
            style={"flex": "1", "overflow_y": "auto", "padding": "24px 20px 12px"}
        ),
        chat_input(),
        rx.script("""
            (function(){
                function scroll(){var e=document.getElementById('msgs');if(e)e.scrollTop=e.scrollHeight;}
                new MutationObserver(scroll).observe(document.getElementById('msgs')||document.body,{childList:true,subtree:true});
                scroll();
            })();
        """),
        style={
            "flex": "1", "display": "flex", "flex_direction": "column",
            "height": "100vh", "overflow": "hidden", "background": BG,
        }
    )


def index():
    return rx.box(
        rx.flex(sidebar(), chat_area(), direction="row",
                style={"height": "100vh", "overflow": "hidden"}),
        style={"background": BG}
    )