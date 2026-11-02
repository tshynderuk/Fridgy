# Fridgy backend — AI recipe generation

This backend keeps the existing Android contract:

- `GET /health` -> `{"status":"ok"}`
- `POST /recipe` accepts `ingredients` and `max_time_minutes`
- successful response fields remain `recipe_name`, `cooking_time_minutes`,
  `ingredients`, `instructions`, `source`

The five hardcoded recipes have been replaced with Gemini generation.
The Gemini key is read only by the Python backend from `.env`; it must never
be placed in the Android app or committed to Git.

## 1. Back up the current backend

Before replacing `main.py`, make a copy named `main_old.py`.

## 2. Put the files in the backend folder

Copy these files next to `main.py`:

- `main.py`
- `requirements.txt`
- `.env.example`

The expected folder is `D:\AndroidStudioProjects\backend`.

## 3. Create the private environment file

In PowerShell, from the backend folder:

```powershell
Copy-Item .env.example .env
notepad .env
```

Replace `PASTE_YOUR_GEMINI_API_KEY_HERE` with your own key.
Do not send the key in chat and do not put it in Kotlin code.

Create a Gemini API key in Google AI Studio:
https://aistudio.google.com/app/apikey

## 4. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 5. Start the backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open while testing locally.

## 6. Test in Swagger

Open:

http://127.0.0.1:8000/docs

Try `POST /recipe` with:

```json
{
  "ingredients": ["куряче філе", "рис", "печериці", "вершки"],
  "max_time_minutes": 40
}
```

A successful answer should have `source: "gemini"`.

## Notes

- `GEMINI_API_KEY` is required for AI generation.
- If the key is missing, the API returns HTTP 503 with a clear message.
- AI timeout is controlled by `AI_TIMEOUT_S`.
- The response format stays compatible with the current Android DTO.
- The current Android emulator base URL remains `http://10.0.2.2:8000/`.
- For production deployment, use HTTPS, keep the key in the hosting provider's
  secret/environment settings, and add rate limiting and abuse protection.
