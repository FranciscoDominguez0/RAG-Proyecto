import reflex as rx

config = rx.Config(
    app_name="app",
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="dark", accent_color="blue")
        )
    ],
)