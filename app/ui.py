import reflex as rx
from app.state import AppState, ChatMessage

BG   = "#080a0f"
SIDE = "#0a0c11"
SURF = "#111520"
INP  = "#181d2e"
BOR  = "#1a1f30"
BOR2 = "#2a3050"
ACC  = "#5b8dee"
ACCD = "#3a6bd4"
USR  = "#0f1e42"
USBR = "#1a3a7a"
TXT  = "#cdd5e8"
MUT  = "#4a5270"
DIM  = "#252d45"
GRN  = "#1fc87a"
AMB  = "#e8a020"
SANS = "'IBM Plex Sans', sans-serif"
MONO = "'IBM Plex Mono', monospace"

EXAMPLES = [
    "Que es ciberseguridad?",
    "Que es un ataque de phishing?",
    "Que es ransomware?",
    "Como funciona MFA?",
    "Controles ISO 27001?",
]

def lbl(t):
    return rx.text(t, size="1", weight="bold", style={
        "color": DIM, "letter_spacing": "0.14em", "font_family": SANS, "margin_bottom": "6px"
    })

def chip(s):
    return rx.badge(s, style={"font_family": MONO, "background": INP, "color": MUT,
                               "border": f"1px solid {BOR2}", "border_radius": "4px"})

def user_msg(msg: ChatMessage):
    return rx.box(
        rx.text(msg.content, style={"color": TXT, "font_size": "14px",
                                    "line_height": "1.75", "font_family": SANS}),
        style={"background": USR, "border": f"1px solid {USBR}",
               "border_radius": "14px 14px 3px 14px", "padding": "11px 16px",
               "max_width": "68%", "align_self": "flex-end"}
    )

def assistant_msg(msg: ChatMessage):
    return rx.flex(
        rx.box(style={"width": "2px", "background": ACC, "border_radius": "2px",
                      "align_self": "stretch", "flex_shrink": "0", "opacity": "0.6"}),
        rx.box(
            rx.markdown(msg.content, component_map={
                "p": lambda t: rx.text(t, style={"color": TXT, "font_size": "14px",
                                                  "line_height": "1.75", "font_family": SANS,
                                                  "margin_bottom": "6px"}),
                "code": lambda t: rx.code(t, style={"font_family": MONO, "font_size": "12px",
                                                     "background": INP, "color": ACC,
                                                     "padding": "1px 6px", "border_radius": "3px"}),
            }),
            rx.cond(msg.sources.length() > 0,
                rx.box(
                    rx.text("Fuentes", style={"color": DIM, "font_size": "11px",
                                              "font_weight": "600", "font_family": SANS,
                                              "margin_bottom": "5px"}),
                    rx.flex(rx.foreach(msg.sources, chip), gap="5px", flex_wrap="wrap"),
                    style={"margin_top": "12px", "padding_top": "10px",
                           "border_top": f"1px solid {BOR}"}
                ), rx.box()
            ),
            style={"flex": "1", "min_width": "0"}
        ),
        gap="14px", align_items="flex-start",
        style={"background": SURF, "border": f"1px solid {BOR}",
               "border_radius": "3px 14px 14px 14px", "padding": "14px 18px",
               "max_width": "86%", "align_self": "flex-start"}
    )

def message_item(msg: ChatMessage):
    return rx.cond(msg.role == "user", user_msg(msg), assistant_msg(msg))

def typing_bubble():
    return rx.cond(AppState.is_loading,
        rx.flex(
            rx.box(style={"width": "2px", "background": ACC, "border_radius": "2px",
                          "align_self": "stretch", "flex_shrink": "0", "opacity": "0.6"}),
            rx.flex(rx.spinner(size="1", style={"color": ACC}),
                    rx.text("Procesando...", style={"color": MUT, "font_size": "13px",
                                                    "font_family": SANS}),
                    align="center", gap="8px"),
            gap="14px", align_items="center",
            style={"background": SURF, "border": f"1px solid {BOR}",
                   "border_radius": "3px 14px 14px 14px", "padding": "12px 18px",
                   "max_width": "86%", "align_self": "flex-start"}
        ), rx.box()
    )

def sidebar():
    return rx.flex(
        # Logo
        rx.flex(
            rx.box(rx.text("C", style={"color": "white", "font_size": "13px",
                                       "font_weight": "700", "font_family": SANS}),
                   style={"width": "26px", "height": "26px", "border_radius": "7px",
                          "background": f"linear-gradient(135deg, {ACC}, {ACCD})",
                          "display": "flex", "align_items": "center", "justify_content": "center"}),
            rx.box(
                rx.text("CiberRAG", style={"font_size": "13px", "font_weight": "600",
                                           "color": TXT, "font_family": SANS}),
                rx.text("Consultor IA", style={"font_size": "10px", "color": MUT,
                                               "font_family": SANS}),
            ),
            align="center", gap="9px",
            style={"padding_bottom": "18px", "border_bottom": f"1px solid {BOR}",
                   "margin_bottom": "20px"}
        ),

        # Estado
        lbl("BASE DE CONOCIMIENTO"),
        rx.flex(
            rx.box(style={"width": "7px", "height": "7px", "border_radius": "50%",
                          "flex_shrink": "0",
                          "background": rx.cond(AppState.db_ready, GRN, AMB)}),
            rx.box(
                rx.text(rx.cond(AppState.db_ready, "Activa", "Sin datos"),
                        style={"font_size": "12px", "font_weight": "600",
                               "color": rx.cond(AppState.db_ready, GRN, AMB),
                               "font_family": SANS}),
                rx.text(AppState.status_message,
                        style={"font_size": "10px", "color": MUT, "font_family": MONO}),
            ),
            gap="9px", align_items="center",
            style={"padding": "10px 12px", "background": INP, "border": f"1px solid {BOR}",
                   "border_radius": "8px", "margin_bottom": "20px"}
        ),

        # Acciones
        lbl("ACCIONES"),
        rx.vstack(
            rx.button(
                rx.flex(rx.icon("refresh-cw", size=12), rx.text("Recargar documentos"),
                        gap="7px", align="center"),
                on_click=AppState.reload_documents, loading=AppState.is_indexing,
                style={"width": "100%", "background": INP, "color": TXT, "font_family": SANS,
                       "border": f"1px solid {BOR2}", "border_radius": "7px",
                       "padding": "8px 12px", "font_size": "12px", "cursor": "pointer",
                       "justify_content": "flex-start",
                       "_hover": {"border_color": ACC}}
            ),
            rx.button(
                rx.flex(rx.icon("trash-2", size=12), rx.text("Limpiar conversacion"),
                        gap="7px", align="center"),
                on_click=AppState.clear_chat,
                style={"width": "100%", "background": "transparent", "color": MUT,
                       "font_family": SANS, "border": f"1px solid {BOR}",
                       "border_radius": "7px", "padding": "8px 12px", "font_size": "12px",
                       "cursor": "pointer", "justify_content": "flex-start",
                       "_hover": {"background": INP, "color": TXT}}
            ),
            spacing="2", width="100%", style={"margin_bottom": "20px"}
        ),

        # Sugerencias
        lbl("SUGERENCIAS"),
        rx.vstack(
            *[rx.button(q, on_click=AppState.set_input(q),
                style={"width": "100%", "background": "transparent", "color": MUT,
                       "font_family": SANS, "border": "none", "border_radius": "6px",
                       "padding": "5px 8px", "font_size": "12px", "cursor": "pointer",
                       "justify_content": "flex-start", "white_space": "normal",
                       "text_align": "left", "line_height": "1.5",
                       "_hover": {"background": INP, "color": TXT}}
              ) for q in EXAMPLES],
            spacing="1", width="100%"
        ),

        rx.box(style={"flex": "1"}),
        rx.text("v1.0 · RAG + DeepSeek",
                style={"color": DIM, "font_size": "10px", "font_family": MONO,
                       "text_align": "center", "padding_top": "16px",
                       "border_top": f"1px solid {BOR}"}),

        direction="column",
        style={"width": "270px", "min_width": "270px", "background": SIDE,
               "border_right": f"1px solid {BOR}", "padding": "24px 20px",
               "height": "100vh", "overflow_y": "auto"}
    )

def chat_input():
    return rx.box(
        rx.flex(
            rx.text_area(
                key=AppState.input_key, placeholder="Escribe tu consulta...",
                value=AppState.user_input, on_change=AppState.set_input,
                on_key_down=AppState.handle_key_press, rows="1",
                style={"flex": "1", "background": INP, "color": TXT,
                       "border": f"1px solid {BOR2}", "border_radius": "10px",
                       "padding": "11px 14px", "font_size": "14px", "font_family": SANS,
                       "resize": "none", "outline": "none",
                       "_placeholder": {"color": DIM},
                       "_focus": {"border_color": ACC, "box_shadow": f"0 0 0 2px {ACC}22"}}
            ),
            rx.button(
                rx.icon("arrow-up", size=16),
                on_click=AppState.send_message, loading=AppState.is_loading,
                disabled=AppState.user_input.length() == 0,
                style={"background": ACC, "color": "white", "border": "none",
                       "border_radius": "10px", "width": "42px", "height": "42px",
                       "cursor": "pointer", "flex_shrink": "0",
                       "_hover": {"background": ACCD},
                       "_disabled": {"background": INP, "color": DIM, "cursor": "not-allowed"}}
            ),
            gap="8px", align_items="flex-end",
        ),
        style={"padding": "12px 24px 20px", "border_top": f"1px solid {BOR}",
               "background": BG, "flex_shrink": "0"}
    )

def chat_area():
    return rx.box(
        rx.box(
            rx.cond(AppState.messages.length() == 0,
                rx.flex(
                    rx.vstack(
                        rx.box(style={"width": "36px", "height": "2px", "background": ACC,
                                      "border_radius": "1px", "box_shadow": f"0 0 12px {ACC}88"}),
                        rx.text("Consultor de Ciberseguridad",
                                style={"font_size": "20px", "font_weight": "600", "color": TXT,
                                       "font_family": SANS, "letter_spacing": "-0.025em"}),
                        rx.text("Haz preguntas basadas en los documentos cargados.",
                                style={"color": MUT, "font_size": "13px", "font_family": SANS}),
                        rx.cond(AppState.is_indexing,
                            rx.flex(rx.spinner(size="1", style={"color": ACC}),
                                    rx.text("Indexando...", style={"color": MUT, "font_size": "13px",
                                                                   "font_family": SANS}),
                                    align="center", gap="8px"),
                            rx.box()),
                        align="center", spacing="3",
                    ),
                    align="center", justify="center",
                    style={"height": "100%", "min_height": "300px"}
                ), rx.box()
            ),
            rx.flex(rx.foreach(AppState.messages, message_item), typing_bubble(),
                    direction="column", gap="10px"),
            id="msgs",
            style={"flex": "1", "overflow_y": "auto", "padding": "28px 24px 16px"}
        ),
        chat_input(),
        rx.script("""
            (function(){var e=document.getElementById('msgs');if(!e)return;
            function s(){e.scrollTop=e.scrollHeight;}
            new MutationObserver(s).observe(e,{childList:true,subtree:true});s();})();
        """),
        style={"flex": "1", "display": "flex", "flex_direction": "column",
               "height": "100vh", "overflow": "hidden", "background": BG}
    )

def index():
    return rx.box(
        rx.flex(sidebar(), chat_area(), direction="row",
                style={"height": "100vh", "overflow": "hidden"}),
        style={"background": BG}
    )