import google.generativeai as genai

# PONÉ TU CLAVE ACÁ ADENTRO
genai.configure(api_key="AQ.Ab8RN6IdbXS0MzxLKjTW00bpzv-Vey1OWhysVKd-o1TM0xYILg")

print("Buscando modelos autorizados para tu cuenta...")

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Podés usar este modelo: {m.name}")