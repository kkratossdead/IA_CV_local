#!/usr/bin/env python3
"""
🔥 ANALYSEUR CV PROFESSIONNEL 
Version finale avec Qwen2-VL + GPU AMD RX 6700 XT

Extraction de texte OCR + Analyse RH automatisée
Optimisé pour LM Studio + modèle Qwen2-VL-7B-Instruct
"""

import requests
import json
import base64
import sys
import time
from pathlib import Path

class CVAnalyzer:
    def __init__(self, base_url="http://localhost:1234/v1"):
        """
        Analyseur CV utilisant LM Studio avec Qwen2-VL
        Port par défaut LM Studio: 1234
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
                    print("💡 Chargez Qwen2-VL-7B-Instruct dans LM Studio")
                    return False
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            print("💡 Démarrez Local Server dans LM Studio")
            return False
    
    def extract_cv_text(self, image_path):
        """
        Extraction OCR professionnelle avec Qwen2-VL
        Précision maximale pour les CV
        """
        print("🔍 Extraction OCR...")
        
        # Encoder l'image
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Erreur lecture image: {e}")
            return None
        
        # Prompt OCR optimisé pour Qwen2-VL
        ocr_prompt = """Extrait tout le texte de cette image de CV avec précision maximale. 
Respecte l'orthographe exacte des noms, prénoms, compétences et informations.
Donne uniquement le texte extrait, sans introduction ni commentaire."""

        payload = {
            "model": "auto",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": ocr_prompt},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.05,
            "top_p": 0.8
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=150
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content']
                
                print(f"⚡ OCR terminé: {duration:.1f}s")
                print(f"📊 Texte extrait: {len(extracted_text)} caractères")
                
                return extracted_text
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur OCR: {e}")
            return None
    
    def analyze_cv_rh(self, cv_text, job_offer):
        """
        Analyse RH professionnelle du CV
        """
        print("📊 Analyse RH...")
        
        # Limiter les tailles pour éviter les timeouts
        cv_summary = cv_text[:1000] if len(cv_text) > 1000 else cv_text
        job_summary = job_offer[:200] if len(job_offer) > 200 else job_offer
        
        analysis_prompt = f"""Analyse ce CV pour le poste donné. Réponds avec un JSON valide uniquement.

POSTE: {job_summary}

CV: {cv_summary}

Format de réponse (remplace les valeurs):
{{
  "nom_prenom": "Nom Prénom du candidat",
  "score_technique": 32,
  "score_experience": 24,
  "score_formation": 13,
  "score_soft_skills": 11,
  "score_global": 80,
  "points_forts": ["Maîtrise Python", "Projets concrets"],
  "points_faibles": ["Manque d'expérience pro"],
  "competences_matchees": ["Python", "JavaScript"],
  "competences_manquantes": ["AWS", "Docker"],
  "recommandation": "Recommandé",
  "commentaires": "Profil prometteur avec de bonnes bases techniques."
}}"""

        payload = {
            "model": "auto",
            "messages": [{"role": "user", "content": analysis_prompt}],
            "max_tokens": 600,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                analysis_result = result['choices'][0]['message']['content']
                print(f"⚡ Analyse terminée: {duration:.1f}s")
                return analysis_result
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur analyse: {e}")
            return None
    
    def save_results(self, cv_text, analysis_json, image_name):
        """Sauvegarder les résultats"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_name = Path(image_name).stem
        
        # Texte extrait
        text_file = f"{base_name}_extracted_{timestamp}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"EXTRACTION CV - {image_name}\n")
            f.write("="*50 + "\n\n")
            f.write(cv_text)
        
        # Analyse RH
        json_file = f"{base_name}_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_json, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Fichiers sauvés:")
        print(f"  • {text_file}")
        print(f"  • {json_file}")
        
        return text_file, json_file
    
    def display_results(self, analysis_json):
        """Affichage formaté des résultats"""
        print("\n" + "="*60)
        print("📊 RÉSULTATS DE L'ANALYSE CV")
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
        
        print(f"\n💭 COMMENTAIRES:")
        print(f"  {analysis_json.get('commentaires', 'N/A')}")
        
        print("="*60)
    
    def analyze_cv_complete(self, image_path, job_offer):
        """
        Processus complet d'analyse CV
        """
        print("🔥 ANALYSEUR CV PROFESSIONNEL")
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
        
        # Étape 1: Extraction OCR
        cv_text = self.extract_cv_text(image_path)
        if not cv_text:
            print("❌ Échec extraction OCR")
            return False
        
        # Étape 2: Analyse RH
        analysis_raw = self.analyze_cv_rh(cv_text, job_offer)
        if not analysis_raw:
            print("❌ Échec analyse RH")
            return False
        
        # Étape 3: Traitement des résultats
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
                text_file, json_file = self.save_results(cv_text, analysis_json, image_path)
                
                print(f"\n🚀 ANALYSE TERMINÉE EN {total_time:.1f}s")
                print("🎉 Votre GPU AMD RX 6700 XT a travaillé efficacement !")
                
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
    print("🎯 ANALYSEUR CV PROFESSIONNEL")
    print("Powered by Qwen2-VL + AMD RX 6700 XT")
    print("="*50)
    
    # Vérification arguments
    if len(sys.argv) < 3:
        print("\n📋 UTILISATION:")
        print("python cv_analyzer.py <image_cv> <offre_emploi>")
        print("\n📝 EXEMPLE:")
        print('python cv_analyzer.py test.jpg "Développeur Python Junior"')
        print("\n🔧 PRÉREQUIS:")
        print("• LM Studio ouvert avec Local Server actif")
        print("• Modèle Qwen2-VL-7B-Instruct chargé")
        print("• GPU AMD détecté et utilisé")
        return
    
    image_path = sys.argv[1]
    job_offer = sys.argv[2]
    
    # Lancement de l'analyse
    analyzer = CVAnalyzer()
    success = analyzer.analyze_cv_complete(image_path, job_offer)
    
    if success:
        print("\n✅ Analyse réussie !")
    else:
        print("\n❌ Analyse échouée")

if __name__ == "__main__":
    main()
