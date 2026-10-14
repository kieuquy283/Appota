"""Vercel entrypoint for Appota Knowledge Guard API.

This exports the FastAPI ASGI application for Vercel Serverless Functions.
For the Streamlit UI, see streamlit_app.py.
"""

from api.index import app

__all__ = ["app"]
