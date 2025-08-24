#!/usr/bin/env python3
"""
🔥 CV ANALYZER ONE-SHOT (Ollama)

OCR + Analyse RH en un seul appel avec le modèle vision d'Ollama (ex: qwen2.5-vl:7b)

Différences vs version LM Studio:
- Endpoint: http://localhost:11434/api/chat
- Listing modèles: GET /api/tags
- Champ image: {"type": "image", "image": <base64>}
- Peut streamer la sortie (option stream=True)

Prérequis:
1. Installer Ollama: https://ollama.com/download
2. Ouvrir un terminal et télécharger le modèle vision désiré:
   ollama pull qwen2.5-vl:7b
3. (Optionnel) Tester:
   ollama run qwen2.5-vl:7b "Décris cette image" (puis coller base64 manuellement si besoin)
4. Placer un fichier image CV (ex: test.jpg) dans le dossier.
5. Installer dépendances Python: pip install -r requirements.txt

Usage:
python cv_oneshot_ollama.py test.jpg "Développeur Python Junior"
"""
import requests
import json
import base64
import sys
import time
from pathlib import Path
from typing import Optional

class OllamaCVOneShot:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5-vl:7b", stream: bool = False):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.stream = stream

    # ---------------------- Infrastructure ----------------------
    def check_connection(self) -> bool:
        print("🔍 Vérification Ollama...")
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if r.status_code == 200:
                data = r.json()
                names = [m.get("name", "") for m in data.get("models", [])]
                if any(self.model.split(':')[0] in n for n in names):
                    print(f"✅ Modèle trouvé: {self.model} (ou variante)")
                else:
                    print(f"⚠️ Modèle {self.model} absent. Téléchargez-le: ollama pull {self.model}")
                return True
            print(f"❌ Statut HTTP inattendu: {r.status_code}")
        except Exception as e:
            print(f"❌ Impossible de contacter Ollama: {e}")
        return False

    # ---------------------- Prompt Builder ----------------------
    def build_prompt(self, job_offer: str) -> str:
        return f"""Vous êtes un expert RH très exigeant. 
Votre mission : analyser le CV en fonction de l’offre d’emploi fournie.

⚠️ Règles strictes :
- Le JSON doit contenir **exactement et uniquement** les champs suivants, sans en ajouter d'autres.
- Les champs numériques doivent rester des nombres (pas de texte).
- Les détails et explications doivent être intégrés **uniquement** dans les champs texte comme \"commentaires\" ou \"experience_pertinente\".
- N'utilisez pas de sous-objets ou de champs imbriqués.

Champs attendus dans le JSON final :
{{
  \"nom_prenom\": \"Nom et prénom du candidat (extrait du CV)\",
  \"score_technique\": 30,
  \"score_experience\": 22,
  \"score_formation\": 12,
  \"score_soft_skills\": 11,
  \"score_global\": 75,
  \"points_forts\": [\"point fort 1\", \"point fort 2\"],
  \"points_faibles\": [\"point faible 1\"],
  \"competences_matchees\": [\"compétence matchée 1\"],
  \"competences_manquantes\": [\"compétence manquante 1\"],
  \"experience_pertinente\": \"résumé de l'expérience pertinente\",
  \"recommandation\": \"Recommandé / À considérer / Non recommandé\",
  \"commentaires\": \"analyse concise (2 phrases)\",
  \"methode_analyse\": \"Ollama-Qwen2.5-VL\"
}}

Critères de notation :
- Compétences techniques requises : 40 points max
- Expérience pertinente : 30 points max
- Formation et qualifications : 15 points max
- Compétences soft skills : 15 points max

Offre d'emploi:
{job_offer}

INSTRUCTIONS:
1. Lis l'image de CV fournie.
2. Extrait toutes les informations utiles.
3. Compare avec l'offre.
4. Fournis UNIQUEMENT le JSON, sans texte avant/après.
"""

    # ---------------------- Core One-Shot ----------------------
    def analyze_oneshot(self, image_path: str, job_offer: str) -> Optional[str]:
        print("🚀 Lancement analyse ONE-SHOT (Ollama)...")
        try:
            with open(image_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Lecture image échouée: {e}")
            return None
        prompt = self.build_prompt(job_offer)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": b64}
                    ]
                }
            ],
            "stream": self.stream,
            "options": {
                "temperature": 0.1
            }
        }
        url = f"{self.base_url}/api/chat"
        start = time.time()
        try:
            if self.stream:
                result_full = ""
                with requests.post(url, json=payload, stream=True, timeout=600) as r:
                    r.raise_for_status()
                    for line in r.iter_lines():
                        if not line:
                            continue
                        data = json.loads(line.decode('utf-8'))
                        msg = data.get("message", {}).get("content", "")
                        result_full += msg
                        if data.get("done"):
                            break
                print(f"⚡ Terminé (stream): {time.time()-start:.1f}s")
                return result_full
            else:
                r = requests.post(url, json=payload, timeout=600)
                if r.status_code != 200:
                    print(f"❌ HTTP {r.status_code}: {r.text[:200]}")
                    return None
                data = r.json()
                content = data.get("message", {}).get("content", "")
                print(f"⚡ Terminé: {time.time()-start:.1f}s")
                return content
        except Exception as e:
            print(f"❌ Erreur requête Ollama: {e}")
            return None

    # ---------------------- Parsing & Display ----------------------
    def parse_json(self, raw: str) -> Optional[dict]:
        if not raw:
            return None
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start == -1 or end == -1:
            print("❌ JSON introuvable dans la réponse")
            print("Réponse brute:")
            print(raw[:500])
            return None
        snippet = raw[start:end]
        try:
            return json.loads(snippet)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print(snippet)
            return None

    def display(self, data: dict):
        print("\n" + "="*60)
        print("📊 RÉSULTATS (Ollama One-Shot)")
        print("="*60)
        print(f"👤 {data.get('nom_prenom','N/A')}")
        print(f"🎯 Global: {data.get('score_global','?')}/100")
        print(f"Technique: {data.get('score_technique','?')} /40  | Exp: {data.get('score_experience','?')} /30  | Form: {data.get('score_formation','?')} /15  | Soft: {data.get('score_soft_skills','?')} /15")
        print(f"Recommandation: {data.get('recommandation','N/A')}")
        for k,label in [
            ("points_forts","Points forts"),
            ("points_faibles","Points faibles"),
            ("competences_matchees","Compétences matchées"),
            ("competences_manquantes","Compétences manquantes")]:
            vals = data.get(k, [])
            print(f"\n{label}:")
            if isinstance(vals, list):
                for v in vals:
                    print(f"  • {v}")
            else:
                print(f"  {vals}")
        print("\nExpérience pertinente:")
        print("  " + data.get("experience_pertinente","N/A"))
        print("\nCommentaires:")
        print("  " + data.get("commentaires","N/A"))
        print("\nMéthode: " + str(data.get("methode_analyse","N/A")))
        print("="*60)

    def save(self, data: dict, image_path: str):
        ts = time.strftime('%Y%m%d_%H%M%S')
        base = Path(image_path).stem
        out = f"{base}_ollama_oneshot_{ts}.json"
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Sauvegardé: {out}")

    # ---------------------- Orchestration ----------------------
    def run(self, image_path: str, job_offer: str) -> bool:
        print("🔥 CV ANALYZER ONE-SHOT OLLAMA")
        print("="*50)
        if not self.check_connection():
            return False
        if not Path(image_path).exists():
            print(f"❌ Image introuvable: {image_path}")
            return False
        raw = self.analyze_oneshot(image_path, job_offer)
        if not raw:
            return False
        data = self.parse_json(raw)
        if not data:
            return False
        self.display(data)
        self.save(data, image_path)
        print("✅ Terminé")
        return True


def main():
    if len(sys.argv) < 3:
        print("Usage: python cv_oneshot_ollama.py <image_cv> <offre_emploi>")
        print("Ex:    python cv_oneshot_ollama.py test.jpg \"Développeur Python Junior\"")
        print("Prérequis: ollama pull qwen2.5-vl:7b")
        return
    image = sys.argv[1]
    job = sys.argv[2]
    analyzer = OllamaCVOneShot()
    analyzer.run(image, job)

if __name__ == "__main__":
    main()
