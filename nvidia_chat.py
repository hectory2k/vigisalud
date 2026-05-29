import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")
if not api_key:
    print("❌ ERROR: No se encontró NVIDIA_API_KEY en el .env")
    sys.exit(1)

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

MODEL = "meta/llama-3.3-70b-instruct"

user_message = "Paciente 68 años, DM2, GLP-1, dolor miembro inferior post-inmovilización. ¿Riesgo de TVP? ¿Recomendación?"

print(f"🤖 Modelo: {MODEL}")
print(f"💬 Pregunta: {user_message}\n")
print("-" * 50)

try:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_message}],
        temperature=0.6,
        top_p=0.95,
        max_tokens=2048,
        stream=True
    )

    for chunk in completion:
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        if delta and delta.content is not None:
            print(delta.content, end="", flush=True)

    print("\n" + "-" * 50)
    print("✅ Listo")

except Exception as e:
    print(f"\n❌ Error: {e}")
