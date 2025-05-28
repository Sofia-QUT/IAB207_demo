from travel import create_app
app = create_app()
ctx = app.app_context()
ctx.push()
quit()