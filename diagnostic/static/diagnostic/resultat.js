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
    paymentLoadingMessage.textContent = "Connexion à KKiaPay en cours…";
    paymentLoading.classList.remove("is-leaving");
    paymentLoading.hidden = false;
    document.documentElement.classList.add("payment-is-loading");
    slowLoadingTimer = setTimeout(function () {
      paymentLoadingMessage.textContent = "La connexion prend un peu plus de temps. Merci de patienter…";
    }, 7000);
    loadingFailureTimer = setTimeout(function () {
      showPaymentError("La fenêtre de paiement met trop de temps à s’ouvrir. Vérifiez votre connexion puis réessayez.");
    }, 20000);
  }

  function hidePaymentLoading() {
    clearTimeout(slowLoadingTimer);
    clearTimeout(loadingFailureTimer);
    if (paymentLoading.hidden) {
      return;
    }
    paymentLoading.classList.add("is-leaving");
    setTimeout(function () {
      paymentLoading.hidden = true;
      paymentLoading.classList.remove("is-leaving");
      document.documentElement.classList.remove("payment-is-loading");
    }, 200);
  }

  function stopWatchingForWidget() {
    if (widgetObserver) {
      widgetObserver.disconnect();
      widgetObserver = null;
    }
  }

  function nodeContainsKkiapayWidget(node) {
    if (!node || node.nodeType !== 1) {
      return false;
    }
    var element = node;
    var signature = [
      element.id || "",
      typeof element.className === "string" ? element.className : "",
      element.getAttribute("src") || "",
      element.getAttribute("title") || ""
    ].join(" ");
    if (/kkiapay/i.test(signature)) {
      return true;
    }
    return Boolean(element.querySelector('iframe[src*="kkiapay" i], [id*="kkiapay" i], [class*="kkiapay" i]'));
  }

  function watchForKkiapayWidget() {
    stopWatchingForWidget();
    widgetObserver = new MutationObserver(function (mutations) {
      var widgetFound = mutations.some(function (mutation) {
        return Array.prototype.some.call(mutation.addedNodes, nodeContainsKkiapayWidget);
      });
      if (widgetFound) {
        stopWatchingForWidget();
        hidePaymentLoading();
        paymentButton.disabled = false;
        paymentButton.textContent = "Continuer vers le paiement sécurisé — " + price.toLocaleString("fr-FR") + " FCFA";
      }
    });
    widgetObserver.observe(document.body, {childList: true, subtree: true});
  }

  function showPaymentError(message) {
    stopWatchingForWidget();
    hidePaymentLoading();
    openPaymentDialog();
    paymentError.textContent = message;
    paymentError.hidden = false;
    paymentButton.disabled = false;
    paymentButton.textContent = "Continuer vers le paiement sécurisé — " + price.toLocaleString("fr-FR") + " FCFA";
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
    showPaymentLoading();
    watchForKkiapayWidget();
    requestAnimationFrame(function () {
      setTimeout(function () {
        try {
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
          showPaymentError("La fenêtre de paiement n’a pas pu s’ouvrir. Vérifiez votre connexion puis réessayez.");
        }
      }, 50);
    });
  });

  if (typeof window.addKkiapayListener === "function") {
    window.addKkiapayListener("success", function (response) {
      stopWatchingForWidget();
      hidePaymentLoading();
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
      showPaymentError("Le paiement a échoué ou a été annulé. Vous pouvez vérifier vos informations puis réessayer.");
    });
  }
})();
