from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Asegúrate de que esta importación sea correcta según tu estructura
# Por ejemplo: from .api.v1 import dashboard_router
from api.v1 import dashboard_router

app = FastAPI(
    title="Dashboard BFF Service",
    description="API service to aggregate and serve dashboard data for the frontend.",
    version="1.0.0"
)

# --- Configuración para servir archivos estáticos ---
# Asegúrate de que la carpeta 'static' exista en la raíz de tu proyecto
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Rutas para servir los archivos HTML principales del frontend ---
@app.get("/", response_class=HTMLResponse, summary="Página de Login/Registro del Frontend")
async def read_root():
    """
    Sirve el archivo HTML principal (login/registro) para la raíz de la aplicación.
    """
    with open(STATIC_DIR / "index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse, summary="Página Principal del Dashboard del Frontend")
async def read_dashboard():
    """
    Sirve el archivo HTML de la interfaz principal del dashboard.
    """
    with open(STATIC_DIR / "dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

# --- Tus configuraciones de API existentes ---

# Incluye el router para la API del dashboard
app.include_router(
    dashboard_router.router,
    prefix="/api/v1/dashboards",
    tags=["Dashboards"]
)

@app.get("/health", tags=["Health Check"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}