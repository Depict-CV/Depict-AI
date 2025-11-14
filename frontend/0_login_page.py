#!/usr/bin/env python3
import time

import httpx
from nicegui import ui

from config import config
from frontend.utils.session_storage import store
from frontend.utils.tags import (
    TAG_CAN_CERTIFY,
    TAG_EDIT,
    TAG_EDIT_DELETE,
    TAG_VIEW_ONLY,
)

API_URL = config.API_URL


async def login_action(username, password):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/login", json={"username": username, "hashed_password": password})
        if response.status_code == 200:
            user_id = response.json().get("user_id")
            store.user_id = user_id
            ui.notify("Login successful!", color="positive")
            ui.link("open projects", "/main_page")
        else:
            ui.notify("Invalid credentials", color="negative")


async def signup_action(username, email, password, permission):
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": password,
            "permission": permission,
        }
        response = await client.post(f"{API_URL}/users/", json=user_data)
        if response.status_code == 200:
            ui.notify("Sign up successful! Please log in.", color="positive")
        elif response.status_code == 400 and response.json().get("detail") == "Username already exists":
            ui.notify("Username already exists", color="negative")
        else:
            ui.notify("Sign up failed", color="negative")
    duration = time.perf_counter() - start
    print(f"Signup action took {duration:.2f} seconds")


# main dashboard, showing stats, recent activity, etc.
@ui.page("/")
def home_page():
    with ui.row():
        with ui.card():
            ui.label("Login")
            login_username = ui.input("Username")
            login_password = ui.input("Password", password=True)
            ui.button(
                "Login",
                on_click=lambda: login_action(login_username.value, login_password.value),
            )
        with ui.card():
            ui.label("Sign Up")
            signup_username = ui.input("Username")
            signup_password = ui.input("Password", password=True)
            signup_email = ui.input("Email")
            signup_permission = ui.select(
                [TAG_VIEW_ONLY, TAG_EDIT, TAG_EDIT_DELETE, TAG_CAN_CERTIFY],
                value="view only",
            )
            ui.button(
                "Sign Up",
                on_click=lambda: signup_action(
                    signup_username.value,
                    signup_email.value,
                    signup_password.value,
                    signup_permission.value,
                ),
            )


ui.run()
