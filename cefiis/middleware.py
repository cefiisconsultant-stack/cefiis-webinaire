import logging
import re

from django.conf import settings


logger = logging.getLogger(__name__)


CONTAINER_PATTERN = re.compile(
    r"^GTM-[A-Z0-9]+$"
)

HEAD_PATTERN = re.compile(
    rb"<head(?=[\s>])[^>]*>",
    re.IGNORECASE,
)

BODY_PATTERN = re.compile(
    rb"<body(?=[\s>])[^>]*>",
    re.IGNORECASE,
)


class GoogleTagManagerMiddleware:
    """
    Injecte Google Tag Manager sur toutes les pages HTML publiques.

    Ne modifie pas :
    - l'administration Django ;
    - les réponses JSON ;
    - les téléchargements de fichiers ;
    - les réponses en streaming.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        self.enabled = bool(
            getattr(settings, "GTM_ENABLED", False)
        )

        self.container_id = str(
            getattr(settings, "GTM_CONTAINER_ID", "")
        ).strip().upper()

        if self.enabled and not CONTAINER_PATTERN.fullmatch(
            self.container_id
        ):
            logger.warning(
                "Google Tag Manager désactivé : "
                "identifiant de conteneur invalide."
            )

            self.enabled = False

    def __call__(self, request):
        response = self.get_response(request)

        if not self.enabled:
            return response

        if request.path_info.startswith("/admin/"):
            return response

        if response.status_code != 200:
            return response

        if getattr(response, "streaming", False):
            return response

        if response.get("Content-Encoding"):
            return response

        content_type = response.get(
            "Content-Type",
            "",
        ).split(";")[0].strip().lower()

        if content_type != "text/html":
            return response

        content = response.content

        if b"data-cefiis-gtm=" in content:
            return response

        if not HEAD_PATTERN.search(content):
            return response

        if not BODY_PATTERN.search(content):
            return response

        head_snippet = f"""
<!-- Google Tag Manager -->
<script data-cefiis-gtm="{self.container_id}">
(function(w,d,s,l,i){{
    w[l]=w[l]||[];
    w[l].push({{
        'gtm.start':new Date().getTime(),
        event:'gtm.js'
    }});

    var f=d.getElementsByTagName(s)[0];
    var j=d.createElement(s);
    var dl=l!='dataLayer'?'&l='+l:'';

    j.async=true;
    j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;

    f.parentNode.insertBefore(j,f);

}})(window,document,'script','dataLayer','{self.container_id}');
</script>
<!-- End Google Tag Manager -->
""".encode("ascii")

        body_snippet = f"""
<!-- Google Tag Manager (noscript) -->
<noscript>
    <iframe
        src="https://www.googletagmanager.com/ns.html?id={self.container_id}"
        height="0"
        width="0"
        style="display:none;visibility:hidden">
    </iframe>
</noscript>
<!-- End Google Tag Manager (noscript) -->
""".encode("ascii")

        content = HEAD_PATTERN.sub(
            lambda match: match.group(0) + head_snippet,
            content,
            count=1,
        )

        content = BODY_PATTERN.sub(
            lambda match: match.group(0) + body_snippet,
            content,
            count=1,
        )

        response.content = content

        if response.has_header("Content-Length"):
            response["Content-Length"] = str(
                len(content)
            )

        if response.has_header("ETag"):
            del response["ETag"]

        return response
