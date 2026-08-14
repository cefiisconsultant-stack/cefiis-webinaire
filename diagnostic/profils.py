"""Règles explicites de personnalisation du résultat du diagnostic.

La segmentation reste volontairement lisible : chaque résultat peut être
expliqué à partir des réponses du prospect, sans score opaque ni IA externe.
"""

PROFILS_SITUATION = {
    "poste": {
        "titre": "Expert salarié en transition progressive",
        "texte": (
            "Votre emploi sécurise le démarrage : vous pouvez tester une offre, obtenir "
            "des premiers rendez-vous et construire vos preuves sans quitter votre poste."
        ),
    },
    "entrepreneur": {
        "titre": "Entrepreneur avec une expertise à transformer en offre de conseil",
        "texte": (
            "Votre avantage est votre connaissance directe du marché. L’enjeu est de séparer "
            "clairement l’offre de conseil de vos autres activités et de la rendre achetable."
        ),
    },
    "fin_contrat": {
        "titre": "Expert à un moment favorable de repositionnement",
        "texte": (
            "Vos réalisations récentes peuvent devenir des preuves commerciales. Il faut les "
            "formaliser rapidement avant que les contacts et les résultats ne deviennent moins accessibles."
        ),
    },
    "retraite": {
        "titre": "Expert en phase de transmission et de valorisation",
        "texte": (
            "Votre capital principal est l’expérience accumulée. Une offre ciblée permet de la "
            "transmettre sous forme de diagnostic, d’accompagnement ou de formation."
        ),
    },
    "etudiant": {
        "titre": "Profil émergent à professionnaliser progressivement",
        "texte": (
            "Le conseil est accessible, mais votre priorité est de bâtir des preuves : projets "
            "encadrés, missions d’assistance, portfolio et spécialisation sur un problème précis."
        ),
    },
    "sans_emploi": {
        "titre": "Expert disponible pour tester une première offre",
        "texte": (
            "Votre disponibilité peut accélérer les tests, à condition de commencer par une "
            "mission courte et précise plutôt que par une offre générale difficile à vendre."
        ),
    },
    "consultant": {
        "titre": "Consultant en activité à structurer ou à développer",
        "texte": (
            "Votre enjeu n’est plus de prouver que vous pouvez intervenir, mais de rendre les "
            "missions, les tarifs et l’organisation plus réguliers et moins dépendants du hasard."
        ),
    },
    "autre": {
        "titre": "Expert à un point de transition particulier",
        "texte": (
            "Votre situation demande un parcours adapté, mais le socle reste le même : un problème "
            "précis, une offre compréhensible, un prix et une méthode pour rencontrer le marché."
        ),
    },
}

NUANCES_EXPERIENCE = {
    "moins5": (
        "Avec moins de cinq ans d’expérience, une spécialisation étroite et des preuves concrètes "
        "seront plus convaincantes qu’un positionnement trop large."
    ),
    "5a10": (
        "Votre expérience est suffisante pour formaliser une méthode et commencer à la tester "
        "auprès d’un marché précis."
    ),
    "10a20": (
        "Votre expérience constitue déjà un capital fort ; le risque principal est de la présenter "
        "de façon trop générale au lieu de la relier à un résultat client."
    ),
    "plus20": (
        "Votre ancienneté apporte de la crédibilité, à condition de transformer les années "
        "d’expérience en preuves, méthode et résultats observables."
    ),
}

SIGNAUX_MARCHE = {
    "souvent": {
        "titre": "Le marché vous envoie déjà un signal fort",
        "texte": (
            "On sollicite régulièrement votre analyse : un besoin existe déjà. Le prochain pas "
            "consiste à cadrer ces demandes, annoncer un livrable et proposer un prix."
        ),
        "action": "Reprenez trois demandes reçues récemment et transformez-en une en proposition payante.",
    },
    "parfois": {
        "titre": "Le signal du marché est encourageant",
        "texte": (
            "Certaines personnes reconnaissent déjà votre expertise. Vous devez maintenant vérifier "
            "si ce besoin est assez fréquent et important pour devenir une offre."
        ),
        "action": "Menez cinq conversations de découverte avec des organisations correspondant à votre cible.",
    },
    "jamais": {
        "titre": "Le marché reste à valider",
        "texte": (
            "L’absence de sollicitation ne disqualifie pas votre expertise. Elle indique seulement "
            "qu’il faut tester le problème, le vocabulaire et la cible avant de construire une offre complète."
        ),
        "action": "Interrogez dix professionnels sur le problème que vous envisagez de résoudre.",
    },
}

LECTURES_MOTIVATION = {
    "remuneration": "Votre modèle devra relier le prix à la valeur créée, et non seulement au temps passé.",
    "independance": "Votre priorité sera de construire plusieurs sources régulières de missions.",
    "liberte": "La liberté viendra d’offres standardisées, de limites claires et d’une organisation prévisible.",
    "valorisation": "Votre expertise doit devenir une méthode, des livrables et des preuves que le client comprend.",
    "apres_carriere": "Une transition progressive et documentée sécurisera mieux l’après-carrière qu’un lancement tardif.",
    "impact": "Votre positionnement doit viser un problème important et un résultat mesurable dans votre secteur.",
    "autre": "Votre motivation personnelle doit devenir un critère concret pour choisir vos missions et vos clients.",
}

AXES_ACTIONS = {
    "positionnement": "Formuler en une phrase la cible, le problème et le résultat promis.",
    "offre": "Décrire une offre sur une page : étapes, livrables, durée et résultat attendu.",
    "tarifs": "Construire un prix indicatif et écrire les trois raisons qui le justifient.",
    "prospection": "Constituer une liste de 20 prospects et planifier les cinq premiers contacts.",
}


def determiner_phase(reponse):
    """Retourne un code de segment, un libellé de phase et un titre de résultat."""
    if reponse.est_consultant:
        if reponse.anciennete_consultant == "moins1" or reponse.score <= 1:
            return (
                "consultant_lancement",
                "Lancement actif",
                "Votre activité existe. Il faut maintenant sécuriser ses fondations commerciales.",
            )
        if reponse.score <= 2 or not reponse.a_prospection:
            return (
                "consultant_structuration",
                "Structuration commerciale",
                "Votre activité avance. La priorité est maintenant de la rendre plus régulière.",
            )
        return (
            "consultant_croissance",
            "Consolidation et croissance",
            "Votre socle est solide. Vous pouvez viser une activité plus prévisible et des contrats plus structurants.",
        )

    if reponse.score == 0:
        if reponse.situation == "etudiant" or reponse.experience == "moins5":
            return (
                "exploration",
                "Exploration encadrée",
                "Votre potentiel doit d’abord être transformé en spécialisation et en premières preuves.",
            )
        return (
            "fondations",
            "Fondations",
            "Votre expertise a du potentiel. Le socle commercial reste à construire.",
        )
    if reponse.score <= 2:
        return (
            "structuration",
            "Structuration",
            "Votre profil est pertinent. Votre expertise doit maintenant devenir une offre complète.",
        )
    if reponse.score == 3 or reponse.sollicitation == "jamais":
        return (
            "test_marche",
            "Test du marché",
            "Votre socle est avancé. La prochaine étape est de le confronter à des clients réels.",
        )
    return (
        "pret_lancer",
        "Prêt à lancer",
        "Votre socle est complet et le marché vous a déjà envoyé des signaux : passez à l’offre payante.",
    )


def analyse_pour(reponse, domaine):
    segment, phase, titre = determiner_phase(reponse)
    profil = dict(PROFILS_SITUATION.get(reponse.situation, PROFILS_SITUATION["autre"]))
    profil["texte"] = f"{profil['texte']} {NUANCES_EXPERIENCE.get(reponse.experience, '')}".strip()
    signal = SIGNAUX_MARCHE.get(reponse.sollicitation, SIGNAUX_MARCHE["jamais"])

    manquants = []
    for present, code in (
        (reponse.a_positionnement, "positionnement"),
        (reponse.a_offre, "offre"),
        (reponse.a_tarifs, "tarifs"),
        (reponse.a_prospection, "prospection"),
    ):
        if not present:
            manquants.append(AXES_ACTIONS[code])
    plan = manquants[:2]
    if signal["action"] not in plan:
        plan.append(signal["action"])
    if not plan:
        plan = [signal["action"]]

    intro = (
        f"Votre expérience en {domaine.lower()} constitue votre matière première. "
        f"{LECTURES_MOTIVATION.get(reponse.motivation, LECTURES_MOTIVATION['autre'])}"
    )
    return {
        "segment": segment,
        "phase": phase,
        "titre": titre,
        "intro": intro,
        "profil": profil,
        "signal": signal,
        "motivation": LECTURES_MOTIVATION.get(
            reponse.motivation, LECTURES_MOTIVATION["autre"]
        ),
        "plan": plan[:3],
    }
