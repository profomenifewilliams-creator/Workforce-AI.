import json
import os
import re
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST


# Lightweight per-process throttle for the demo service. Use a shared cache or
# API gateway for a multi-instance production deployment.
_REQUESTS = {}
_LIMIT = 12
_WINDOW = 60


def home(request):
    return render(request, "home.html")


@require_GET
def healthz(request):
    return JsonResponse({"ok": True, "service": "afrilearn-ai"})


def _safe_topic(text):
    text = re.sub(r"[\x00-\x1f<>]", " ", text or "")
    return " ".join(text.split())[:180]


def _fallback_lesson(topic, age_group):
    clean = topic.strip().rstrip("?.!") or "the wonders of science"
    lowered = clean.lower()
    if any(term in lowered for term in ("make a bomb", "build a weapon", "hurt myself", "kill myself", "how to poison")):
        return {
            "title": "Let's choose a safer discovery",
            "intro": "I'm glad you asked a question. I can't help with instructions that could hurt someone, but we can explore safety, science, or how people prevent accidents.",
            "steps": [
                {"title": "Pause and stay safe", "body": "Move away from anything dangerous and ask a trusted adult for help if something unsafe is nearby."},
                {"title": "Explore the science safely", "body": "We can learn about energy, materials, or how safety equipment protects people using pictures and harmless examples."},
                {"title": "Ask a new question", "body": "Choose a safe experiment, a science fact, or a project that helps people."},
            ],
            "quiz": {"question": "What should you do when an activity could hurt someone?", "options": ["Ask a trusted adult and choose a safe alternative", "Try it secretly", "Ignore safety instructions"], "correctIndex": 0, "explanation": "A trusted adult can help you find a safer way to learn."},
            "challenge": "Draw a safety badge and name one trusted adult you could ask for help.",
            "mode": "guided_demo",
        }
    if "rainbow" in lowered:
        intro = "A rainbow appears when sunlight meets tiny water droplets in the air. Each droplet bends and reflects light, spreading it into the colours we see."
        steps = [
            {"title": "Find the droplets", "body": "After rain, tiny droplets can hang in the air like little glass beads waiting for sunlight."},
            {"title": "Bend the light", "body": "Sunlight bends when it enters and leaves a droplet. Different colours bend by different amounts, so the colours spread out."},
            {"title": "Look safely", "body": "A rainbow is often visible with the Sun behind you and rain or mist in front. Never look directly at the Sun."},
        ]
        quiz = {"question": "What helps create a rainbow?", "options": ["Sunlight interacting with water droplets", "Clouds painting the sky", "The Moon shining through dry air"], "correctIndex": 0, "explanation": "Water droplets bend and reflect sunlight, separating it into colours."}
        challenge = "Draw the path of a tiny sunbeam as it enters a raindrop, bounces inside, and comes out as colour."
    elif "fraction" in lowered or "pizza" in lowered:
        intro = "Fractions help us describe equal parts of a whole. Imagine sharing one pizza fairly with friends: the number of equal slices tells us the size of each part."
        steps = [
            {"title": "Make equal parts", "body": "Imagine a pizza cut into 4 equal slices. The 4 tells us how many equal parts make the whole."},
            {"title": "Count what you have", "body": "If you take 1 slice, you have one quarter, written as 1/4. The top number tells how many parts you have."},
            {"title": "Try another share", "body": "If you take 2 of the 4 slices, you have 2/4. That is the same amount as one half of the pizza."},
        ]
        quiz = {"question": "A cake is cut into 4 equal pieces. You take 1. What fraction did you take?", "options": ["1/4", "2/4", "4/1"], "correctIndex": 0, "explanation": "One piece out of four equal pieces is one quarter."}
        challenge = "Draw a fruit or pizza, split it into 4 equal parts, and shade 2 parts. Say the fraction out loud."
    else:
        intro = f"Welcome, explorer! Let's discover {clean.lower()} one small step at a time. Curiosity is your superpower, and you can learn by asking questions, noticing patterns, and trying safe activities."
        steps = [
            {"title": "Start with a wonder", "body": f"What do you already know about {clean.lower()}? Share one idea, make a guess, or draw what you imagine."},
            {"title": "Connect the idea", "body": f"Think of one example of {clean.lower()} you might notice at home, at school, outdoors, or in your community."},
            {"title": "Try it yourself", "body": "Explain the idea in your own words. A drawing, a simple example, or a question can show what you have discovered."},
        ]
        quiz = {"question": "Which habit helps you learn something new?", "options": ["Ask questions and try carefully", "Give up after one try", "Never check your ideas"], "correctIndex": 0, "explanation": "Curiosity, practice, and checking ideas help us understand."}
        challenge = f"Create a drawing or safe example to explain {clean.lower()}, then tell someone you trust one thing you discovered."
    return {"title": clean[:90], "intro": intro, "steps": steps, "quiz": quiz, "challenge": challenge, "mode": "guided_demo"}


def _openai_lesson(topic, age_group, language):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    endpoint = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
    system = (
        "You are Lumi, an encouraging AI learning guide for children. Teach accurately with age-appropriate "
        "words, examples from everyday life and African contexts where helpful. Never request private details, "
        "encourage secrecy, provide dangerous instructions, sexual content, self-harm advice, or graphic violence. "
        "For risky requests, kindly redirect to a safe alternative and a trusted adult. Return only valid JSON with "
        "keys title, intro, steps (exactly 3 objects with title/body), quiz (question, three options, correctIndex, "
        "explanation), and challenge. Use the requested language only if reliable."
    )
    payload = {
        "model": model,
        "temperature": 0.45,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps({"topic": topic, "age_group": age_group, "language": language}, ensure_ascii=False)},
        ],
    }
    req = Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=18) as response:
        result = json.loads(response.read().decode("utf-8"))
    data = json.loads(result["choices"][0]["message"]["content"])
    if not isinstance(data.get("steps"), list) or len(data["steps"]) != 3:
        raise ValueError("The AI response did not contain three lesson steps.")
    quiz = data.get("quiz") or {}
    if len(quiz.get("options", [])) != 3 or quiz.get("correctIndex") not in (0, 1, 2):
        raise ValueError("The AI response did not contain a valid quiz.")
    return {
        "title": str(data.get("title", topic))[:90],
        "intro": str(data.get("intro", ""))[:900],
        "steps": [{"title": str(s.get("title", "Explore"))[:90], "body": str(s.get("body", ""))[:600]} for s in data["steps"]],
        "quiz": {"question": str(quiz.get("question", ""))[:300], "options": [str(v)[:140] for v in quiz["options"]], "correctIndex": quiz["correctIndex"], "explanation": str(quiz.get("explanation", ""))[:400]},
        "challenge": str(data.get("challenge", ""))[:600],
        "mode": "ai",
    }


@require_POST
def lesson_api(request):
    remote = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "unknown")).split(",")[0].strip()
    now = time.time()
    timestamps = [t for t in _REQUESTS.get(remote, []) if now - t < _WINDOW]
    if len(timestamps) >= _LIMIT:
        return JsonResponse({"error": "You've asked lots of brilliant questions. Please pause for a minute, then try again."}, status=429)
    timestamps.append(now)
    _REQUESTS[remote] = timestamps

    try:
        body = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Please send a valid learning question."}, status=400)
    topic = _safe_topic(str(body.get("topic", "")))
    if len(topic) < 2:
        return JsonResponse({"error": "Add a question or subject to start your lesson."}, status=400)
    age_group = str(body.get("age_group", "7–9 years"))[:30]
    language = str(body.get("language", "English"))[:30]

    try:
        lesson = _openai_lesson(topic, age_group, language)
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
        lesson = None
    if lesson is None:
        lesson = _fallback_lesson(topic, age_group)
    return JsonResponse(lesson, json_dumps_params={"ensure_ascii": False})
