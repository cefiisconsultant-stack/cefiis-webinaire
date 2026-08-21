(function () {
  "use strict";

  var body = document.body;
  var eventUrl = body.dataset.eventUrl;
  var sessionId = body.dataset.sessionId;
  var feedbackUrl = body.dataset.feedbackUrl;
  var csrfField = document.querySelector("[name=csrfmiddlewaretoken]");
  var csrf = csrfField ? csrfField.value : "";
  var rating = 0;

  function track(name, screen) {
    var data = {
      session_id: sessionId,
      nom: name,
      ecran: screen || "resultat",
      device: innerWidth < 700 ? "mobile" : "desktop"
    };
    if (window.gtag) {
      window.gtag("event", "diagnostic_" + name, data);
    }
    fetch(eventUrl, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data),
      keepalive: true
    }).catch(function () {});
  }

  document.querySelectorAll("[data-track]").forEach(function (link) {
    link.addEventListener("click", function () {
      track(this.dataset.track);
    });
  });

  document.querySelectorAll("[data-rating]").forEach(function (button) {
    button.addEventListener("click", function () {
      rating = Number(this.dataset.rating);
      document.querySelectorAll("[data-rating]").forEach(function (item) {
        item.classList.toggle("active", Number(item.dataset.rating) === rating);
      });
      document.getElementById("feedback-submit").disabled = false;
    });
  });

  document.getElementById("feedback-submit").addEventListener("click", function () {
    var button = this;
    var error = document.getElementById("feedback-error");
    button.disabled = true;
    fetch(feedbackUrl, {
      method: "POST",
      headers: {"Content-Type": "application/json", "X-CSRFToken": csrf},
      body: JSON.stringify({
        note: rating,
        commentaire: document.getElementById("feedback").value.trim()
      })
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          throw new Error(data.error || "Une erreur est survenue.");
        }
        return data;
      });
    }).then(function () {
      document.querySelector(".feedback-form").hidden = true;
      document.querySelector(".thanks").hidden = false;
    }).catch(function (err) {
      button.disabled = false;
      error.textContent = err.message;
      error.hidden = false;
    });
  });

  var buyButton = document.getElementById("ebook-buy-button");
  var dialog = document.getElementById("payment-dialog");
  var paymentForm = document.getElementById("payment-form");
  var paymentButton = document.getElementById("payment-submit");
  var paymentError = document.getElementById("payment-error");
  var paymentLoading = document.getElementById("payment-loading");
  var paymentLoadingMessage = document.getElementById("payment-loading-message");
  var price = Number(body.dataset.ebookPrice);
  var widgetObserver = null;
  var slowLoadingTimer = null;
  var loadingFailureTimer = null;
  var widgetReadyFallbackTimer = null;
  var hideLoadingTimer = null;
  var widgetFramesBeforeOpen = [];
  var lifecycleListenersBound = false;
  var widgetOpenCalled = false;
  var widgetReady = false;
  var paymentCompleting = false;
  var kkiapayOrigin = "https://widget-v3.kkiapay.me";

  function openPaymentDialog() {
    if (dialog.open) {
      return;
    }
    if (typeof dialog.showModal === "function") {
      dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
  }

  function closePaymentDialog() {
    if (typeof dialog.close === "function") {
      dialog.close();
    } else {
      dialog.removeAttribute("open");
    }
  }

  function showPaymentLoading() {
    clearTimeout(slowLoadingTimer);
    clearTimeout(loadingFailureTimer);
    clearTimeout(widgetReadyFallbackTimer);
    clearTimeout(hideLoadingTimer);
    widgetReady = false;
    paymentCompleting = false;
    paymentLoadingMessage.textContent = "Connexion à KKiaPay en cours…";
    paymentLoading.classList.remove("is-leaving", "is-behind-widget", "is-verifying");
    paymentLoading.hidden = false;
    paymentLoading.setAttribute("aria-busy", "true");
    /* Le loader reste devant l'iframe tant que KKiaPay n'a pas confirmé que
       son interface est initialisée. Il passera ensuite derrière le widget. */
    document.body.appendChild(paymentLoading);
    document.documentElement.classList.add("payment-is-loading");
    slowLoadingTimer = setTimeout(function () {
      paymentLoadingMessage.textContent = "La connexion prend un peu plus de temps. Merci de patienter…";
    }, 6000);
    loadingFailureTimer = setTimeout(function () {
      showPaymentError("La fenêtre de paiement met trop de temps à s’ouvrir. Vérifiez votre connexion puis réessayez.");
    }, 30000);
  }

  function hidePaymentLoading() {
    clearTimeout(slowLoadingTimer);
    clearTimeout(loadingFailureTimer);
    clearTimeout(widgetReadyFallbackTimer);
    clearTimeout(hideLoadingTimer);
    if (paymentLoading.hidden) {
      return;
    }
    paymentLoading.classList.add("is-leaving");
    hideLoadingTimer = setTimeout(function () {
      paymentLoading.hidden = true;
      paymentLoading.removeAttribute("aria-busy");
      paymentLoading.classList.remove("is-leaving", "is-behind-widget", "is-verifying");
      document.documentElement.classList.remove("payment-is-loading");
    }, 200);
  }

  function stopWatchingForWidget() {
    if (widgetObserver) {
      widgetObserver.disconnect();
      widgetObserver = null;
    }
    clearTimeout(widgetReadyFallbackTimer);
  }

  function frameExistedBeforeOpening(frame) {
    return widgetFramesBeforeOpen.indexOf(frame) !== -1;
  }

  function markKkiapayReady() {
    if (paymentLoading.hidden || widgetReady || paymentCompleting) {
      return;
    }
    widgetReady = true;
    stopWatchingForWidget();
    clearTimeout(slowLoadingTimer);
    clearTimeout(loadingFailureTimer);
    paymentLoadingMessage.textContent = "Paiement sécurisé en cours…";
    /* L'animation continue, mais un niveau sous l'iframe KKiaPay : le
       formulaire devient visible et cliquable sans écran vide intermédiaire. */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        paymentLoading.classList.add("is-behind-widget");
      });
    });
  }

  function watchFrameLoad(frame) {
    if (frame.dataset.cefiisKkiapayWatched === "true") {
      return;
    }
    frame.dataset.cefiisKkiapayWatched = "true";
    frame.addEventListener("load", function () {
      /* Secours si une future version du SDK ne renvoie plus son signal
         WIDGET_SUCCESSFULLY_INIT. Le délai laisse le temps au premier rendu. */
      widgetReadyFallbackTimer = setTimeout(markKkiapayReady, 8000);
    }, {once: true});
  }

  function scanForKkiapayFrame() {
    var frames = Array.prototype.slice.call(document.querySelectorAll("iframe"));
    for (var index = 0; index < frames.length; index += 1) {
      var frame = frames[index];
      var src = frame.getAttribute("src") || "";
      if (frameExistedBeforeOpening(frame) || !/kkiapay\.me/i.test(src)) {
        continue;
      }
      watchFrameLoad(frame);
      return true;
    }
    return false;
  }

  function keepLoaderAboveKkiapay() {
    if (!paymentLoading.hidden && !widgetReady && document.body.lastElementChild !== paymentLoading) {
      document.body.appendChild(paymentLoading);
    }
  }

  function watchForKkiapayWidget() {
    stopWatchingForWidget();
    widgetObserver = new MutationObserver(function () {
      scanForKkiapayFrame();
      requestAnimationFrame(keepLoaderAboveKkiapay);
    });
    widgetObserver.observe(document.body, {
      childList: true,
      subtree: false
    });
    scanForKkiapayFrame();
  }

  function resetPaymentButton() {
    paymentButton.disabled = false;
    paymentButton.textContent = "Continuer vers le paiement sécurisé — " + price.toLocaleString("fr-FR") + " FCFA";
  }

  function closeKkiapayWidgetSilently() {
    if (typeof window.closeKkiapayWidget === "function") {
      try {
        window.closeKkiapayWidget();
      } catch (error) {}
    }
  }

  function handleKkiapayClose() {
    widgetOpenCalled = false;
    widgetReady = false;
    stopWatchingForWidget();
    if (paymentCompleting) {
      return;
    }
    hidePaymentLoading();
    resetPaymentButton();
    paymentError.hidden = true;
    openPaymentDialog();
  }

  function bindKkiapayLifecycleListeners() {
    if (lifecycleListenersBound) {
      return;
    }
    lifecycleListenersBound = true;
    if (typeof window.addKkiapayCloseListener === "function") {
      window.addKkiapayCloseListener(handleKkiapayClose);
    }
    if (typeof window.addPaymentAbortedListener === "function") {
      window.addPaymentAbortedListener(function () {
        paymentCompleting = false;
        closeKkiapayWidgetSilently();
        showPaymentError("Le paiement a été interrompu. Vous pouvez vérifier vos informations puis réessayer.");
      });
    }
  }

  function showPaymentError(message) {
    widgetOpenCalled = false;
    widgetReady = false;
    paymentCompleting = false;
    stopWatchingForWidget();
    closeKkiapayWidgetSilently();
    hidePaymentLoading();
    openPaymentDialog();
    paymentError.textContent = message;
    paymentError.hidden = false;
    resetPaymentButton();
  }

  buyButton.addEventListener("click", function () {
    track("ebook_click", "resultat");
    track("checkout_view", "checkout");
    paymentError.hidden = true;
    openPaymentDialog();
    document.getElementById("payment-email").focus();
  });

  dialog.querySelector(".dialog-close").addEventListener("click", function () {
    closePaymentDialog();
  });

  paymentForm.addEventListener("submit", function (event) {
    event.preventDefault();
    paymentError.hidden = true;
    if (!paymentForm.checkValidity()) {
      paymentForm.reportValidity();
      return;
    }
    if (typeof window.openKkiapayWidget !== "function") {
      showPaymentError("Le module de paiement n’a pas pu être chargé. Vérifiez votre connexion puis réessayez.");
      return;
    }

    var name = document.getElementById("payment-name").value.trim();
    var email = document.getElementById("payment-email").value.trim();
    var phone = document.getElementById("payment-phone").value.trim();
    track("payment_started", "checkout");
    paymentButton.disabled = true;
    paymentButton.textContent = "Ouverture du paiement…";
    closePaymentDialog();
    widgetFramesBeforeOpen = Array.prototype.slice.call(document.querySelectorAll("iframe"));
    showPaymentLoading();
    watchForKkiapayWidget();
    bindKkiapayLifecycleListeners();
    requestAnimationFrame(function () {
      setTimeout(function () {
        try {
          widgetOpenCalled = true;
          window.openKkiapayWidget({
            amount: price,
            key: body.dataset.kkiapayKey,
            sandbox: body.dataset.kkiapaySandbox === "true",
            fullname: name,
            email: email,
            phone: phone,
            phoneNumber: phone,
            paymentMethods: ["momo", "card"],
            data: JSON.stringify({
              prenom: name,
              email: email,
              diagnosticId: body.dataset.diagnosticId
            })
          });
        } catch (error) {
          widgetOpenCalled = false;
          showPaymentError("La fenêtre de paiement n’a pas pu s’ouvrir. Vérifiez votre connexion puis réessayez.");
        }
      }, 50);
    });
  });

  if (typeof window.addKkiapayListener === "function") {
    window.addKkiapayListener("success", function (response) {
      paymentCompleting = true;
      stopWatchingForWidget();
      clearTimeout(slowLoadingTimer);
      clearTimeout(loadingFailureTimer);
      clearTimeout(widgetReadyFallbackTimer);
      paymentLoading.classList.remove("is-behind-widget", "is-leaving");
      paymentLoading.classList.add("is-verifying");
      paymentLoading.hidden = false;
      paymentLoading.setAttribute("aria-busy", "true");
      paymentLoadingMessage.textContent = "Paiement reçu. Vérification sécurisée en cours…";
      document.body.appendChild(paymentLoading);
      closeKkiapayWidgetSilently();
      var transactionId = response && response.transactionId;
      if (!transactionId) {
        showPaymentError("Le paiement semble terminé, mais sa référence est absente. Ne repayez pas et contactez-nous.");
        return;
      }
      paymentButton.disabled = true;
      paymentButton.textContent = "Vérification du paiement…";
      fetch(body.dataset.paymentUrl, {
        method: "POST",
        headers: {"Content-Type": "application/json", "X-CSRFToken": csrf},
        body: JSON.stringify({
          transactionId: transactionId,
          prenom: document.getElementById("payment-name").value.trim(),
          email: document.getElementById("payment-email").value.trim(),
          diagnosticId: body.dataset.diagnosticId,
          diagnosticSession: sessionId
        })
      }).then(function (serverResponse) {
        return serverResponse.json().then(function (data) {
          if (!serverResponse.ok || !data.success) {
            throw new Error(data.error || "Le paiement n’a pas pu être confirmé.");
          }
          return data;
        });
      }).then(function (data) {
        window.location.href = data.redirect;
      }).catch(function (err) {
        showPaymentError(err.message + " Si votre compte a été débité, ne repayez pas et contactez-nous.");
      });
    });

    window.addKkiapayListener("failed", function () {
      paymentCompleting = false;
      showPaymentError("Le paiement a échoué ou a été annulé. Vous pouvez vérifier vos informations puis réessayer.");
    });
  }

  /* Le SDK actuel émet ce message lorsque l'interface interne a réellement
     terminé son initialisation. Il est plus précis que le simple load de
     l'iframe, particulièrement lors d'une première visite sans cache. */
  window.addEventListener("message", function (event) {
    if (
      event.origin === kkiapayOrigin &&
      event.data &&
      event.data.name === "WIDGET_SUCCESSFULLY_INIT" &&
      widgetOpenCalled
    ) {
      markKkiapayReady();
    }
  });
})();
