# Configuration Ollama pour Analyse CV One-Shot

## 1. Installation
Télécharger: https://ollama.com/download

Vérifier l'installation:
```powershell
ollama --version
```

## 2. Télécharger un modèle Vision
Exemple recommandé:
```powershell
ollama pull qwen2.5-vl:7b
```
Lister les modèles:
```powershell
ollama list
```

## 3. Test rapide (optionnel)
```powershell
ollama run qwen2.5-vl:7b "Décris l'image suivante"  # (mode interactif)
```

## 4. Installer dépendances Python
```powershell
pip install -r requirements.txt
```

## 5. Lancer l'analyse One-Shot
```powershell
python cv_oneshot_ollama.py test.jpg "Développeur Python Junior"
```

## 6. Structure JSON attendue
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
  "methode_analyse": "Ollama-Qwen2.5-VL"
}
```

## 7. Limitations
- Sous Windows: traitement CPU (pas d'accélération GPU AMD via Ollama)
- Performances plus lentes que LM Studio pour l'OCR
- Réduire la résolution de l'image si temps > 60s

## 8. Astuces optimisation
- Compresser l'image (JPEG qualité 80)
- Découper pages multiples en images séparées
- Baisser temperature (0.1 déjà optimal)
- Vérifier charge CPU (Gestionnaire des tâches)

## 9. Problèmes fréquents
| Problème | Cause | Solution |
|----------|-------|----------|
| Connection refused | Service Ollama arrêté | Relancer Ollama Desktop |
| Modèle introuvable | pull non fait | `ollama pull qwen2.5-vl:7b` |
| Réponse vide | JSON mal formé ou trop long | Relancer, vérifier prompt |
| Lenteur extrême | Image lourde | Réduire résolution |

## 10. Commandes utiles
```powershell
# Redémarrer service (si bloqué)
Stop-Process -Name Ollama -Force

# Voir les logs (Mac/Linux)
ollama serve
```

---
Fichier généré automatiquement pour usage multi-machine.
