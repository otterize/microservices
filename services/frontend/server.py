import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from session import UnauthenticatedException

# Route imports
from routes.views import router as views_router
from routes.cart import router as cart_router
from routes.users import router as users_router
from routes.products import router as products_router
from routes.checkout import router as checkout_router
from routes.newsletter import router as newsletter_router

app = FastAPI()

PORT = 7000

# Middleware for serving static files (like CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==============================================================================
# ==                                 HANDLERS                                 ==
# ==============================================================================


@app.exception_handler(UnauthenticatedException)
async def validation_exception_handler(request, exc):
    return RedirectResponse(url="/login", headers={"HX-Redirect": "/login"})

# ==============================================================================
# ==                                  ROUTES                                  ==
# ==============================================================================

app.include_router(views_router, tags=["views"])
app.include_router(cart_router, prefix="/api/cart", tags=["cart"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(checkout_router, prefix="/api/checkout", tags=["checkout"])
app.include_router(newsletter_router, prefix="/api/newsletter", tags=["newsletter"])


# ==============================================================================
# ==                                   MAIN                                   ==
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_path = f"{dir_path}/server.key"
    cert_path = f"{dir_path}/server.crt"

    print(key_path)

    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"Starting server at https://localhost:{PORT}")
        uvicorn.run(app="server:app", host="0.0.0.0", port=PORT, reload=True, ssl_keyfile=key_path, ssl_certfile=cert_path)
    else:
        print(f"Starting server at http://localhost:{PORT}")
        uvicorn.run(app="server:app", host="0.0.0.0", port=PORT, reload=True)