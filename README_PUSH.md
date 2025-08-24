# IA CV Local

Analyse de CV locale avec Qwen2-VL (LM Studio) + GPU AMD (DirectML).

## Scripts
- `cv_analyzer.py` : Version standard (OCR + Analyse en 2 étapes)
- `cv_analyzer_clean.py` : Variante simplifiée
- `cv_oneshot.py` : Version One-Shot (OCR + Analyse RH en un seul appel)

## One-Shot (recommandé)
```bash
python cv_oneshot.py test.jpg "Développeur Python Junior"
```

## Prérequis
1. Installer LM Studio et charger `qwen2-vl-7b-instruct`
2. Activer DirectML (GPU AMD) dans Settings
3. Démarrer Local Server (port 1234)
4. Installer dépendances :
```bash
pip install -r requirements.txt
```

## Résultat
- Extraction OCR précise
- Analyse RH JSON structurée
- Sauvegarde automatique des résultats

## Structure JSON attendue
```json
{
  "nom_prenom": "Nom Prénom",
  "score_technique": 30,
  "score_experience": 22,
  "score_formation": 12,
  "score_soft_skills": 11,
  "score_global": 75,
  "points_forts": ["..."],
  "points_faibles": ["..."],
  "competences_matchees": ["..."],
  "competences_manquantes": ["..."],
  "experience_pertinente": "...",
  "recommandation": "Recommandé",
  "commentaires": "...",
  "methode_analyse": "Qwen2-VL"
}
```

## Nettoyage conseillé avant push
Supprimer fichiers générés (`*_extracted_*.txt`, `*_analysis_*.json`, `*_oneshot_*.json`) si non désirés.

## Licence
Usage interne / expérimentation.
