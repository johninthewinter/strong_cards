# Publication LinkedIn en français

Un modèle local de 27 milliards de paramètres vient d’atteindre la neuvième marche d’un benchmark d’ingénierie progressif sur mon MacBook Pro M5 Max.

Pas neuf variantes d’un prompt jouet.

C1 : cache LRU.
C3 : ledger bancaire avec atomicité et invariants.
C7 : parser d’expressions sans `eval`.
C8 : graphe de dépendances avec détection de cycles.
C9 : mini moteur de tableur capable de parser des formules, résoudre des références futures, étendre des plages rectangulaires et détecter les cycles.

Gemma 4 31B local a franchi C1 à C9 au premier essai.
Qwen3.6 27B local a franchi C1 à C8, puis C9 après une relance étendue.
Huit routes hébergées — GLM, MiMo, Qwen, MiniMax et DeepSeek — ont également atteint C9.

Le résultat important n’est pas qu’un petit modèle « remplace » un modèle frontier.

C’est qu’il n’a jamais eu besoin de devenir l’architecte.

GPT-5.5 avait transformé chaque marche en Strong Card : un contrat figé avec objectif, interface, périmètre modifiable, invariants, tests, budget, règles de relance et conditions d’arrêt.

Puis il a quitté la boucle.

Un contrôleur shell/Python décidait de l’ordre, lançait le worker, exécutait les gates, autorisait ou refusait la relance et arrêtait le run. Zéro décision de control plane confiée à un LLM. Claude Code servait de harness aux modèles locaux, OpenCode aux routes hébergées, Codex au run de référence GPT.

Autrement dit : l’intelligence frontier a été dépensée avant l’exécution. L’autorité est restée dans du code déterministe. Les modèles moins chers ont absorbé le travail borné.

Et l’audit a aussi cassé mon propre résultat : C9 avait des trous de couverture. C10 contenait des contradictions entre contrat et tests. Même GPT-5.5 xhigh a obtenu 7/7 en codant autour du benchmark invalide.

C’est précisément pourquoi cette expérience m’intéresse.

Je ne cherche pas à savoir si un petit modèle peut improviser une application depuis un brief flou. Je cherche où le placer dans une vraie architecture pour qu’il soit utile, vérifiable et remplaçable, sans lui donner l’autorité sur le système.

J’ai publié le leaderboard complet, carte par carte et modèle par modèle, avec les échecs, relances, faux positifs, artefacts acceptés, runners et limites.

Premier pilote. Protocole suivant déjà en préparation.
