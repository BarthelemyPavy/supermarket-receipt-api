# Un assistant pour comprendre, pas pour réaliser le TD

Si les assistants sont autorisés pendant la séance, leur rôle est celui d'un tuteur :
ils expliquent, questionnent et relisent vos essais. Vous gardez la main sur le code,
les tests, les commandes et les décisions. L'autorisation reste celle de l'enseignant.

## Ce que fait le tuteur

- Demander votre tentative et votre hypothèse avant d'aider à résoudre un problème.
- Donner un indice ciblé, puis vous laisser essayer.
- Expliquer une notion, une erreur ou une sortie de commande que vous partagez.
- Relire un test proposé et discuter ce qu'il prouve, sans fournir la suite complète.
- Ne pas écrire de fichiers, fournir un patch ou donner le corrigé dans le chat.

Les règles communes sont dans [AGENTS.md](../AGENTS.md). Claude Code les importe via
[CLAUDE.md](../CLAUDE.md). Elles ne contiennent ni corrigé ni accès au dépôt enseignant.

## Les protections fournies

| Élément | Rôle |
| --- | --- |
| `.tutor/guard.py` | Politique commune en Python standard, sans dépendance ni appel réseau |
| `.claude/settings.json` | Hooks Claude Code et refus des outils directs d'édition/délégation |
| `.codex/hooks.json` | Hooks Codex pour les clients compatibles |
| `.codex/config.toml` | Lecture seule, pas d'escalade d'approbation ni de login shell, hooks activés |
| `.tutor/test_guard.py` | Tests techniques des garde-fous, séparés des tests métier du TD |

`SessionStart` rappelle le rôle de tuteur. `PreToolUse` vérifie les opérations avant
leur exécution : refus par défaut, seuls quelques outils et commandes de lecture
sont reconnus. Un outil nouveau ou inconnu est refusé, même si son nom semble inoffensif.
Les refus n'empêchent pas de continuer à discuter avec le tuteur.

Les éditions, patches, outils MCP, sous-agents, terminaux interactifs, scripts,
interpréteurs, commandes Git et exécutions de tests sont refusés. Un test est du code :
il peut écrire des fichiers. C'est donc vous qui exécutez `uv` et `pytest` dans votre
terminal, puis partagez les résultats utiles. Aucun hook Git ne limite votre travail manuel.

Lectures disponibles pour l'assistant : outils natifs `Read`, `Glob` et `Grep` dans le
dépôt, et les formes de commandes suivantes, sans les combiner :

```text
pwd
ls -la -- src/supermarket_receipt_api
cat -- src/supermarket_receipt_api/routes/checkout.py
head -n 80 -- src/supermarket_receipt_api/services/checkout.py
tail -n 40 -- src/supermarket_receipt_api/services/checkout.py
rg --no-config --files
rg --no-config --files -- src
rg --no-config -n -- checkout src/supermarket_receipt_api
rg --no-config -n -F -- checkout src/supermarket_receipt_api/routes/checkout.py
```

Les chemins contenant des espaces doivent être cités. Les redirections, pipelines,
substitutions, expansions shell et options non prévues sont refusés. Les expressions
régulières contenant ces caractères peuvent donc être refusées également : utiliser
une recherche textuelle simple ou partager l'extrait. `head` et `tail` acceptent de 1
à 2 000 lignes. Aucun `allow` n'est renvoyé aux outils : une lecture admise conserve
les contrôles de permissions ordinaires du client.

## Activation avant la séance

Périmètre des commandes de hooks : **macOS, Linux ou Windows avec WSL2**, shell POSIX,
Git et `python3` disponibles dans le terminal de l'assistant. Utiliser Python 3.10+
pour les tests des garde-fous ; le projet applicatif reste en Python 3.13.
La configuration Windows native n'a pas été validée : utiliser WSL2 pour ce dispositif.
Le script n'installe rien et ne télécharge pas Python s'il manque.

1. Cloner une copie indépendante du dépôt étudiant, comprenant les dossiers cachés
   `.claude`, `.codex` et `.tutor`. Les anciens ZIP J1 ne contiennent pas ces ajouts.
2. Vérifier manuellement `python3 --version` et `git --version` dans le même environnement
   que l'assistant. Ouvrir une **nouvelle session dédiée au TD**, sans terminal persistant
   déjà lancé, plutôt que de réutiliser une session de développement existante.
3. **Claude Code :** accepter la confiance du dossier après lecture des fichiers.
   Vérifier avec `/status` que les réglages du projet sont chargés, puis avec `/hooks`
   que `SessionStart` et `PreToolUse` pointent sur `.tutor/guard.py`. Ne pas poursuivre
   en cas d'erreur de chargement des hooks.
4. **Codex :** utiliser un client prenant en charge les hooks de projet, approuver le
   projet puis examiner et approuver les définitions dans `/hooks`. Les hooks non
   approuvés peuvent être ignorés. Après une modification de leur définition, vérifier
   de nouveau leur approbation. Confirmer aussi que la session est en lecture seule.
   Si `/hooks` n'est pas disponible, ne pas considérer la protection comme active.
5. L'enseignant teste la configuration sur les versions et OS réellement utilisés :
   un appel de lecture doit passer et un appel d'édition doit être refusé par le hook.
   Contrôler le journal du hook et l'absence de modification. Un simple refus rédigé
   par le modèle ne prouve pas qu'un hook a été exécuté.

Vérifier la version et les hooks sur chaque poste : une mise à jour du CLI ne vaut pas
approbation des hooks. Les tests du script ne constituent pas un test de bout en bout
dans les deux assistants.

## Vérification technique, hors TD

L'enseignant ou le mainteneur peut lancer, dans son propre terminal :

```sh
python3 -I -B .tutor/test_guard.py
uv run ruff check . .tutor
uv run ruff format --check . .tutor
uv run pytest -q
```

Les tests de garde-fous ne sont pas ajoutés à la suite métier de l'étudiant. Ils
simulent des requêtes d'outils et exécutent le vrai script de décision en sous-processus,
sans appliquer les écritures demandées. Ils sont séparés des six cas d'exemple du TD
et ne fournissent pas de corrigé métier.

## Limites à connaître

- Ces fichiers sont modifiables sur un poste personnel et ne s'imposent pas aux autres
  assistants ou comptes. Ce n'est ni un dispositif anti-triche inviolable ni une preuve
  de travail sans IA.
- L'interdiction de fournir le corrigé dans le chat est une **consigne pédagogique**,
  pas un filtre déterministe sur les réponses. Les hooks contrôlent les outils pris en
  charge, pas toutes les phrases générées.
- Un hook non chargé, non approuvé, ignoré par un ancien client ou interrompu par un
  timeout ne garantit pas le blocage. Le lancement renvoie un refus si Python ou le
  script échoue normalement ; cela ne remplace pas la validation dans le client réel.
- Certains outils hébergés ou chemins spécialisés échappent aux hooks. Une entrée dans
  un terminal déjà démarré peut également ne pas repasser par `PreToolUse` : d'où la
  nouvelle session, le refus des shells interactifs et l'interdiction de contournement.
- Les contrôles de chemins refusent les accès directs hors dépôt et à certains fichiers
  locaux sensibles. Ils ne constituent pas une isolation complète des lectures
  récursives. Ne placer aucun secret ni corrigé enseignant dans le dépôt étudiant.
- Le dispositif suppose des exécutables et un environnement de shell de confiance.
  Ce n'est pas un bac à sable système administré ; un administrateur du poste contrôle
  toujours son environnement.
- Aucun historique de conversation, prompt ou code n'est envoyé à un serveur par ces
  hooks. Aucun mot de passe « enseignant » ou mécanisme de déverrouillage n'est inclus.

En cas de problème, arrêter la session d'assistant et prévenir l'enseignant. Le TD reste
réalisable dans l'éditeur et le terminal habituels, sans assistant.

## Références de configuration

Documentation consultée le 15 octobre 2026 :

- [Codex — hooks, confiance et limites](https://learn.chatgpt.com/docs/hooks).
- [Codex — référence de configuration](https://learn.chatgpt.com/docs/config-file/config-reference).
- [Claude Code — hooks](https://code.claude.com/docs/en/hooks).
- [Claude Code — réglages et ordre de priorité](https://code.claude.com/docs/en/settings).
