#!/usr/bin/env python3
"""
AI EMERGENCY HEALTH ASSISTANT - REST API SERVER & STATIC HOST
Department of CSA, SOET, ITM University Gwalior
Runs on standard Python 3 library with zero external pip dependencies.
Includes proper medication names, dosages, and safety warnings.
"""

import http.server
import socketserver
import os
import sys
import json
import urllib.request
import urllib.error
from triage_engine import evaluate_clinical_rules

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_CASES = [
    {
        "case": "General",
        "sample_input": "I have a mild headache",
        "expected_behaviour": "General level: rest, fluids, Paracetamol/Ibuprofen, when to see a doctor"
    },
    {
        "case": "Caution",
        "sample_input": "Fever for 3 days with vomiting",
        "expected_behaviour": "Caution level: ORS, Paracetamol, precautions and see a doctor soon"
    },
    {
        "case": "Emergency",
        "sample_input": "Bleeding that will not stop",
        "expected_behaviour": "Emergency level: call emergency services first, sterile pressure gauze, Betadine"
    },
    {
        "case": "Sample Interaction",
        "sample_input": "My father has chest pain and is sweating a lot. What should I do?",
        "expected_behaviour": "Emergency level: call 112 immediately, chewable Aspirin 300mg, sit and rest"
    },
    {
        "case": "Vague input",
        "sample_input": "I don't feel good",
        "expected_behaviour": "Asks simple follow-up questions, avoid random self-medication"
    },
    {
        "case": "Non-health",
        "sample_input": "Write me a poem",
        "expected_behaviour": "Politely redirects to health topics"
    }
]

def call_gemini_api(query: str, api_key: str) -> dict:
    """Calls Google Gemini API with system prompt safety rules & medication specifications."""
    system_prompt = (
        "You are the AI Emergency Health Assistant prototype developed at ITM University Gwalior. "
        "Analyze the user's health query and return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "level": "GENERAL" | "CAUTION" | "EMERGENCY" | "CLARIFICATION" | "REDIRECT",\n'
        '  "summary": "Short 1-sentence summary",\n'
        '  "immediate_action": "Crucial first step under time pressure",\n'
        '  "information": "Clear explanation of what might be happening in simple language",\n'
        '  "precautions": ["Precautions and what to avoid"],\n'
        '  "medications": [\n'
        '    {\n'
        '      "name": "Generic & brand name (e.g. Paracetamol / Crocin 500mg, ORS Electral, Aspirin / Dispirin 300mg)",\n'
        '      "type": "OTC | Prescription / Emergency Only | Supply | Avoid / Danger",\n'
        '      "dose": "Standard adult dose (e.g. 500mg, 1 sachet in 1L water)",\n'
        '      "purpose": "What this medicine helps with",\n'
        '      "instructions": "How to take (e.g. chew immediately, take after food)",\n'
        '      "warning": "Safety precautions and contraindications (e.g. do not take if bleeding, max 3g/day)"\n'
        '    }\n'
        '  ],\n'
        '  "next_steps": ["Step-by-step guidance"],\n'
        '  "professional_help": "When to see a doctor or call emergency services",\n'
        '  "disclaimer": "General guidance only, not a medical diagnosis. Call 112 for acute emergencies."\n'
        "}\n"
        "Classification & Medication Rules:\n"
        "- EMERGENCY (Chest pain / cardiac): Chewable Aspirin 300mg (chewed, antiplatelet), Sublingual Nitroglycerin 5mg (ONLY if previously prescribed for angina). Mandate calling 112.\n"
        "- EMERGENCY (Bleeding): Povidone-Iodine (Betadine 5%) antiseptic, compression gauze. CONTRAINDICATED: Avoid Aspirin, Ibuprofen, or blood thinners.\n"
        "- CAUTION (Fever + Vomiting): Oral Rehydration Salts (ORS / Electral sachets), Paracetamol (Crocin 500-650mg). Avoid NSAIDs (Combiflam/Ibuprofen) on empty stomach.\n"
        "- GENERAL (Mild headache): Paracetamol (500mg) or Ibuprofen (200-400mg after meals), ORS fluids.\n"
        "- CLARIFICATION: Vague inputs like 'I don't feel good'. Advise against self-medicating before symptoms are clarified.\n"
        "- REDIRECT: Non-health questions like 'Write a poem'. No medications needed."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [
                {"text": system_prompt},
                {"text": f'User Query: "{query}"'}
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=5) as response:
        result = json.loads(response.read().decode("utf-8"))
        json_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(json_text)

class HealthAssistantRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS for cross-origin local testing
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "status": "healthy",
                "service": "AI Emergency Health Assistant",
                "institution": "ITM University Gwalior",
                "version": "1.1.0",
                "features": ["Triage", "Proper Medication Guidance", "Safety Guardrails"],
                "test_cases_count": len(TEST_CASES)
            }
            self.wfile.write(json.dumps(resp, indent=2).encode("utf-8"))
            return

        elif self.path == "/api/test-cases":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(TEST_CASES, indent=2).encode("utf-8"))
            return

        # Default: Serve static files (index.html, styles.css, app.js)
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(post_body) if post_body else {}
            except json.JSONDecodeError:
                data = {}

            query = data.get("query", "")
            api_key = data.get("api_key") or os.environ.get("GEMINI_API_KEY", "")

            # Attempt Generative AI if key is present
            triage_result = None
            if api_key:
                try:
                    triage_result = call_gemini_api(query, api_key)
                except Exception as ex:
                    print(f"[WARN] Generative AI API call failed ({ex}), falling back to local clinical rules.")

            # Fall back to high-precision local clinical NLP engine
            if not triage_result:
                triage_result = evaluate_clinical_rules(query)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(triage_result, indent=2).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    print(f"==============================================================")
    print(f"  AI EMERGENCY HEALTH ASSISTANT - HTTP & REST SERVER")
    print(f"  ITM University Gwalior | Dept. of CSA | SOET")
    print(f"==============================================================")
    print(f"  Serving directory : {BASE_DIR}")
    print(f"  Local Web UI      : http://localhost:{PORT}")
    print(f"  API Healthcheck   : http://localhost:{PORT}/api/health")
    print(f"  API Chat Endpoint : http://localhost:{PORT}/api/chat (POST)")
    print(f"==============================================================")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), HealthAssistantRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully.")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()
