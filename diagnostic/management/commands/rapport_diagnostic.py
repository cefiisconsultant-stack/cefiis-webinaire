import json
from collections import Counter, defaultdict
from datetime import timedelta
from statistics import mean, median

from django.core.management.base import BaseCommand
from django.utils import timezone

from diagnostic.models import DiagnosticEvenement, DiagnosticReponse


SCREEN_ORDER = [
    "intro", "ebook", "domaine", "experience", "situation", "anciennete",
    "sollicitation", "motivation", "elements", "difficulte", "contact",
]


def taux(numerateur, denominateur):
    return round(numerateur / denominateur * 100, 1) if denominateur else 0.0


def libelle(value, choices):
    return dict(choices).get(value, value or "Non renseigné")


class Command(BaseCommand):
    help = "Affiche un tunnel dédupliqué, les abandons, les segments et les conversions."

    def add_arguments(self, parser):
        parser.add_argument("--jours", type=int, default=30)
        parser.add_argument("--format", choices=("text", "json"), default="text")

    def handle(self, *args, **options):
        jours = min(max(options["jours"], 1), 3650)
        debut = timezone.now() - timedelta(days=jours)
        evenements = list(
            DiagnosticEvenement.objects.filter(date_creation__gte=debut)
            .only("session_id", "nom", "ecran", "duree_ms", "meta", "date_creation")
            .order_by("date_creation")
        )
        reponses = list(DiagnosticReponse.objects.filter(date_creation__gte=debut))

        sessions_par_nom = defaultdict(set)
        vues_par_ecran = defaultdict(set)
        fins_par_ecran = defaultdict(set)
        erreurs_par_ecran = defaultdict(set)
        durees_par_ecran = defaultdict(list)
        dernier_ecran = {}
        acquisition = {}

        for event in evenements:
            session = str(event.session_id)
            sessions_par_nom[event.nom].add(session)
            if event.nom == "view":
                acquisition.setdefault(session, {
                    "source": event.meta.get("source") or "direct",
                    "source_info": event.meta.get("source_info") or "sans-audience",
                    "campaign": event.meta.get("campaign") or "sans-campagne",
                    "content": event.meta.get("content") or "sans-variante",
                    "device": event.meta.get("device") or "inconnu",
                })
            if event.nom == "step_view" and event.ecran:
                vues_par_ecran[event.ecran].add(session)
                dernier_ecran[session] = event.ecran
            elif event.nom == "step_complete" and event.ecran:
                fins_par_ecran[event.ecran].add(session)
                if event.duree_ms is not None and 0 <= event.duree_ms <= 3_600_000:
                    # Le navigateur envoie la durée de l’écran, pas un horodatage cumulé.
                    durees_par_ecran[event.ecran].append(event.duree_ms)
            elif event.nom == "validation_error" and event.ecran:
                erreurs_par_ecran[event.ecran].add(session)

        sessions_reponses = {str(reponse.session_id) for reponse in reponses}
        sessions_par_nom["complete"].update(sessions_reponses)
        for reponse in reponses:
            acquisition[str(reponse.session_id)] = {
                "source": reponse.utm_source or "direct",
                "source_info": reponse.utm_source_info or "sans-audience",
                "campaign": reponse.utm_campaign or "sans-campagne",
                "content": reponse.utm_content or "sans-variante",
                "device": reponse.device or "inconnu",
            }

        vues = sessions_par_nom["view"]
        demarrages = sessions_par_nom["start"]
        termines = sessions_par_nom["complete"]
        abandons_inferes = demarrages - termines
        sorties = Counter(dernier_ecran.get(session, "intro") for session in abandons_inferes)

        sources = defaultdict(
            lambda: {"vues": set(), "demarrages": set(), "termines": set(), "achats": set()}
        )
        audiences = defaultdict(
            lambda: {"vues": set(), "demarrages": set(), "termines": set(), "achats": set()}
        )
        all_sessions = vues | demarrages | termines | sessions_par_nom["purchase"]
        for session in all_sessions:
            key = acquisition.get(session, {}).get("source", "direct")
            audience_key = acquisition.get(session, {}).get("source_info", "sans-audience")
            if session in vues:
                sources[key]["vues"].add(session)
                audiences[audience_key]["vues"].add(session)
            if session in demarrages:
                sources[key]["demarrages"].add(session)
                audiences[audience_key]["demarrages"].add(session)
            if session in termines:
                sources[key]["termines"].add(session)
                audiences[audience_key]["termines"].add(session)
            if session in sessions_par_nom["purchase"]:
                sources[key]["achats"].add(session)
                audiences[audience_key]["achats"].add(session)

        durees = [r.duree_secondes for r in reponses if r.duree_secondes is not None]
        notes = [r.note_formulaire for r in reponses if r.note_formulaire is not None]
        achats_attribues = {
            str(r.session_id) for r in reponses if r.ebook_achete
        } | sessions_par_nom["purchase"]

        funnel = {
            "vues_uniques": len(vues),
            "demarrages": len(demarrages),
            "taux_demarrage": taux(len(demarrages), len(vues)),
            "termines": len(termines),
            "taux_completion": taux(len(termines), len(demarrages)),
            "resultats_affiches": len(sessions_par_nom["result_view"]),
            "clics_ebook": len(sessions_par_nom["ebook_click"]),
            "pages_paiement": len(sessions_par_nom["checkout_view"]),
            "paiements_demarres": len(sessions_par_nom["payment_started"]),
            "achats_attribues": len(achats_attribues),
            "taux_achat_par_resultat": taux(len(achats_attribues), len(sessions_par_nom["result_view"])),
            "clics_whatsapp": len(sessions_par_nom["whatsapp_click"]),
            "abandons_inferes": len(abandons_inferes),
            "duree_mediane_secondes": round(median(durees), 1) if durees else None,
            "note_moyenne": round(mean(notes), 2) if notes else None,
            "nombre_avis": len(notes),
        }

        ecrans = []
        for ecran in SCREEN_ORDER:
            if not (vues_par_ecran[ecran] or sorties[ecran]):
                continue
            durations = durees_par_ecran[ecran]
            ecrans.append({
                "ecran": ecran,
                "vues_uniques": len(vues_par_ecran[ecran]),
                "fins_uniques": len(fins_par_ecran[ecran]),
                "sorties_inferees": sorties[ecran],
                "sessions_avec_erreur": len(erreurs_par_ecran[ecran]),
                "duree_mediane_secondes": round(median(durations) / 1000, 1) if durations else None,
            })

        acquisition_rows = []
        for source, valeurs in sorted(sources.items()):
            acquisition_rows.append({
                "source": source,
                "vues": len(valeurs["vues"]),
                "demarrages": len(valeurs["demarrages"]),
                "termines": len(valeurs["termines"]),
                "achats": len(valeurs["achats"]),
                "taux_completion": taux(len(valeurs["termines"]), len(valeurs["demarrages"])),
            })

        audience_rows = []
        for audience, valeurs in sorted(audiences.items()):
            audience_rows.append({
                "audience": audience,
                "vues": len(valeurs["vues"]),
                "demarrages": len(valeurs["demarrages"]),
                "termines": len(valeurs["termines"]),
                "achats": len(valeurs["achats"]),
                "taux_completion": taux(len(valeurs["termines"]), len(valeurs["demarrages"])),
            })

        segments = Counter(libelle(r.segment, DiagnosticReponse.SEGMENTS) for r in reponses)
        situations = Counter(libelle(r.situation, DiagnosticReponse.SITUATIONS) for r in reponses)
        optins = sum(1 for r in reponses if r.consentement_marketing)
        rapport = {
            "periode_jours": jours,
            "funnel": funnel,
            "par_ecran": ecrans,
            "acquisition_par_source": acquisition_rows,
            "acquisition_par_audience": audience_rows,
            "segments": dict(segments.most_common()),
            "situations": dict(situations.most_common()),
            "optin_marketing": {"nombre": optins, "taux": taux(optins, len(reponses))},
        }

        if options["format"] == "json":
            self.stdout.write(json.dumps(rapport, ensure_ascii=False, indent=2))
            return
        self._write_text(rapport)

    def _write_text(self, rapport):
        f = rapport["funnel"]
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"DIAGNOSTIC — {rapport['periode_jours']} DERNIERS JOURS"
        ))
        rows = [
            ("Vues uniques", f["vues_uniques"]),
            ("Démarrages", f"{f['demarrages']} ({f['taux_demarrage']:.1f}% des vues)"),
            ("Diagnostics terminés", f"{f['termines']} ({f['taux_completion']:.1f}% des démarrages)"),
            ("Abandons inférés", f["abandons_inferes"]),
            ("Résultats affichés", f["resultats_affiches"]),
            ("Clics ebook", f["clics_ebook"]),
            ("Pages de paiement", f["pages_paiement"]),
            ("Paiements démarrés", f["paiements_demarres"]),
            ("Achats attribués", f"{f['achats_attribues']} ({f['taux_achat_par_resultat']:.1f}% des résultats)"),
            ("Clics groupe WhatsApp", f["clics_whatsapp"]),
            ("Durée médiane", f"{f['duree_mediane_secondes']} s" if f["duree_mediane_secondes"] is not None else "—"),
            ("Note moyenne", f"{f['note_moyenne']}/5 ({f['nombre_avis']} avis)" if f["note_moyenne"] is not None else "—"),
        ]
        for label, value in rows:
            self.stdout.write(f"{label:26} {value}")

        self.stdout.write("\n" + self.style.MIGRATE_HEADING("PAR ÉCRAN — SESSIONS UNIQUES"))
        self.stdout.write("Écran           Vues   Fins   Sorties   Erreurs   Médiane")
        for row in rapport["par_ecran"]:
            duration = f"{row['duree_mediane_secondes']} s" if row["duree_mediane_secondes"] is not None else "—"
            self.stdout.write(
                f"{row['ecran'][:14]:14} {row['vues_uniques']:5} {row['fins_uniques']:6} "
                f"{row['sorties_inferees']:8} {row['sessions_avec_erreur']:9}   {duration}"
            )

        self.stdout.write("\n" + self.style.MIGRATE_HEADING("PAR SOURCE"))
        self.stdout.write("Source                 Vues   Starts   Fins   Achats   Complétion")
        for row in rapport["acquisition_par_source"]:
            self.stdout.write(
                f"{row['source'][:22]:22} {row['vues']:5} {row['demarrages']:8} "
                f"{row['termines']:6} {row['achats']:8}   {row['taux_completion']:.1f}%"
            )

        self.stdout.write("\n" + self.style.MIGRATE_HEADING("PAR AUDIENCE (UTM_SOURCE_INFO)"))
        self.stdout.write("Audience               Vues   Starts   Fins   Achats   Complétion")
        for row in rapport["acquisition_par_audience"]:
            self.stdout.write(
                f"{row['audience'][:22]:22} {row['vues']:5} {row['demarrages']:8} "
                f"{row['termines']:6} {row['achats']:8}   {row['taux_completion']:.1f}%"
            )

        self.stdout.write("\n" + self.style.MIGRATE_HEADING("SEGMENTS"))
        for label, count in rapport["segments"].items():
            self.stdout.write(f"{label:38} {count}")
        optin = rapport["optin_marketing"]
        self.stdout.write(f"\nOpt-in WhatsApp marketing : {optin['nombre']} ({optin['taux']:.1f}%)")
