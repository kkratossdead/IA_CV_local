#!/usr/bin/env python3
"""
🔥 ANALYSEUR CV ULTRA-RAPIDE 
Version ONE-SHOT avec Qwen2-VL + GPU AMD RX 6700 XT

OCR + Analyse RH en UN SEUL APPEL
Optimisé pour LM Studio + modèle Qwen2-VL-7B-Instruct
"""

import requests
import json
import base64
import sys
import time
from pathlib import Path

class CVAnalyzerOneShot:
    def __init__(self, base_url="http://localhost:1234/v1"):
        """
        Analyseur CV ultra-rapide avec un seul prompt
        """
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        
    def check_connection(self):
        """Vérifier LM Studio et modèle Qwen2-VL"""
        print("🔍 Vérification de la connexion LM Studio...")
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                model_names = [model['id'] for model in models.get('data', [])]
                
                print("✅ LM Studio connecté")
                
                # Vérifier Qwen2-VL
                qwen_models = [m for m in model_names if 'qwen2' in m.lower() and 'vl' in m.lower()]
                if qwen_models:
                    print(f"🎯 Qwen2-VL détecté: {qwen_models[0]}")
                    return True
                else:
                    print("⚠️ Qwen2-VL non chargé")
                    return False
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    def analyze_cv_oneshot(self, image_path, job_offer):
        """
        Analyse CV complète en une seule requête
        OCR + Analyse RH simultanée
        """
        print("🚀 Analyse ONE-SHOT en cours...")
        
        # Encoder l'image
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Erreur lecture image: {e}")
            return None
        
        # PROMPT COMBINÉ : OCR + Analyse RH
        combined_prompt = f"""Vous êtes un expert RH très exigeant. 
Votre mission : analyser le CV en fonction de l'offre d'emploi fournie.

⚠️ Règles strictes :
- Le JSON doit contenir **exactement et uniquement** les champs suivants, sans en ajouter d'autres.
- Les champs numériques doivent rester des nombres (pas de texte).
- Les détails et explications doivent être intégrés **uniquement** dans les champs texte comme "commentaires" ou "experience_pertinente".
- N'utilisez pas de sous-objets ou de champs imbriqués.

Champs attendus dans le JSON final :
{{
  "nom_prenom": "Nom et prénom du candidat (extrait du CV)",
  "score_technique": [nombre sur 40],
  "score_experience": [nombre sur 30],
  "score_formation": [nombre sur 15],
  "score_soft_skills": [nombre sur 15],
  "score_global": [nombre sur 100],
  "points_forts": ["liste des points forts du candidat"],
  "points_faibles": ["liste des points faibles ou manques"],
  "competences_matchees": ["compétences qui correspondent à l'offre"],
  "competences_manquantes": ["compétences requises mais absentes"],
  "experience_pertinente": "description détaillée de l'expérience pertinente",
  "recommandation": "Recommandé / À considérer / Non recommandé",
  "commentaires": "analyse détaillée du profil",
  "methode_analyse": "Qwen2-VL"
}}

Critères de notation :
- Compétences techniques requises : 40 points max
- Expérience pertinente : 30 points max
- Formation et qualifications : 15 points max
- Compétences soft skills : 15 points max

Voici l'offre d'emploi à analyser :
{job_offer}

"""

        payload = {
            "model": "auto",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": combined_prompt},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=180  # Plus de temps pour le traitement complexe
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                analysis_result = result['choices'][0]['message']['content']
                print(f"⚡ Analyse ONE-SHOT terminée: {duration:.1f}s")
                return analysis_result
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur analyse ONE-SHOT: {e}")
            return None
    
    def save_results(self, analysis_json, image_name):
        """Sauvegarder les résultats"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_name = Path(image_name).stem
        
        # Analyse RH complète
        json_file = f"{base_name}_oneshot_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_json, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Fichier sauvé: {json_file}")
        return json_file
    
    def display_results(self, analysis_json):
        """Affichage formaté des résultats"""
        print("\n" + "="*60)
        print("📊 RÉSULTATS ANALYSE ONE-SHOT")
        print("="*60)
        
        print(f"👤 CANDIDAT: {analysis_json.get('nom_prenom', 'N/A')}")
        print(f"🎯 SCORE GLOBAL: {analysis_json.get('score_global', 0)}/100")
        
        print(f"\n📈 SCORES DÉTAILLÉS:")
        print(f"  🔧 Technique: {analysis_json.get('score_technique', 0)}/40")
        print(f"  💼 Expérience: {analysis_json.get('score_experience', 0)}/30")
        print(f"  🎓 Formation: {analysis_json.get('score_formation', 0)}/15")
        print(f"  🤝 Soft Skills: {analysis_json.get('score_soft_skills', 0)}/15")
        
        print(f"\n📋 RECOMMANDATION: {analysis_json.get('recommandation', 'N/A')}")
        
        print(f"\n✅ POINTS FORTS:")
        for point in analysis_json.get('points_forts', []):
            print(f"  • {point}")
        
        print(f"\n⚠️ POINTS À AMÉLIORER:")
        for point in analysis_json.get('points_faibles', []):
            print(f"  • {point}")
        
        print(f"\n🎯 COMPÉTENCES MATCHÉES:")
        for comp in analysis_json.get('competences_matchees', []):
            print(f"  • {comp}")
        
        print(f"\n❌ COMPÉTENCES MANQUANTES:")
        for comp in analysis_json.get('competences_manquantes', []):
            print(f"  • {comp}")
        
        print(f"\n💼 EXPÉRIENCE PERTINENTE:")
        print(f"  {analysis_json.get('experience_pertinente', 'N/A')}")
        
        print(f"\n💭 COMMENTAIRES:")
        print(f"  {analysis_json.get('commentaires', 'N/A')}")
        
        print(f"\n🔧 MÉTHODE: {analysis_json.get('methode_analyse', 'N/A')}")
        
        print("="*60)
    
    def analyze_complete(self, image_path, job_offer):
        """
        Processus complet d'analyse CV en ONE-SHOT
        """
        print("🚀 ANALYSEUR CV ONE-SHOT")
        print("Qwen2-VL + GPU AMD RX 6700 XT")
        print("="*50)
        
        # Vérifications préliminaires
        if not self.check_connection():
            return False
        
        if not Path(image_path).exists():
            print(f"❌ Image introuvable: {image_path}")
            return False
        
        print(f"📄 Analyse: {image_path}")
        print(f"💼 Poste: {job_offer}")
        
        total_start = time.time()
        
        # Analyse ONE-SHOT
        analysis_raw = self.analyze_cv_oneshot(image_path, job_offer)
        if not analysis_raw:
            print("❌ Échec analyse ONE-SHOT")
            return False
        
        # Traitement des résultats
        try:
            # Parser le JSON de l'analyse
            json_start = analysis_raw.find('{')
            json_end = analysis_raw.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = analysis_raw[json_start:json_end]
                analysis_json = json.loads(json_str)
                
                total_time = time.time() - total_start
                
                # Affichage des résultats
                self.display_results(analysis_json)
                
                # Sauvegarde
                json_file = self.save_results(analysis_json, image_path)
                
                print(f"\n🚀 ANALYSE ONE-SHOT TERMINÉE EN {total_time:.1f}s")
                print("🎉 Ultra-rapide avec un seul appel Qwen2-VL !")
                
                return True
            else:
                print("❌ Format JSON invalide dans la réponse")
                print("Réponse brute:")
                print(analysis_raw[:500])
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            print("Réponse brute:")
            print(analysis_raw[:500])
            return False

def main():
    """Interface principale"""
    print("🎯 ANALYSEUR CV ONE-SHOT")
    print("Powered by Qwen2-VL + AMD RX 6700 XT")
    print("OCR + Analyse RH en UN SEUL APPEL")
    print("="*50)
    
    # Vérification arguments
    if len(sys.argv) < 3:
        print("\n📋 UTILISATION:")
        print("python cv_oneshot.py <image_cv> <offre_emploi>")
        print("\n📝 EXEMPLE:")
        print('python cv_oneshot.py test.jpg "Développeur Python Junior"')
        print("\n🔧 AVANTAGES:")
        print("• OCR + Analyse RH en une seule requête")
        print("• Plus rapide que la version 2-étapes")
        print("• Prompt RH exact selon vos spécifications")
        print("• Utilisation optimale du GPU AMD")
        return
    
    image_path = sys.argv[1]
    job_offer = sys.argv[2]
    
    # Lancement de l'analyse ONE-SHOT
    analyzer = CVAnalyzerOneShot()
    success = analyzer.analyze_complete(image_path, job_offer)
    
    if success:
        print("\n✅ Analyse ONE-SHOT réussie !")
    else:
        print("\n❌ Analyse ONE-SHOT échouée")

if __name__ == "__main__":
    main()
