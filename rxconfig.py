import reflex as rx

config = rx.Config(
    app_name="app",
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="dark", accent_color="blue")
        )
    ],
    # Excluir carpetas que cambian durante runtime
    tailwind=None,
    backend_only=False,
    env=rx.Env.PROD,  # desactiva hot-reload
)