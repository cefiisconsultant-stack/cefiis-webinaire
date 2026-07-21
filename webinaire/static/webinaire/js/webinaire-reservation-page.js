document.addEventListener('DOMContentLoaded', function() {
    // Capture et stockage des UTM depuis l'URL
    (function() {
        const keys = ["utm_source","utm_medium","utm_campaign","gclid"];
        const p = new URLSearchParams(location.search);
        keys.forEach(k => { const v = p.get(k); if (v) sessionStorage.setItem(k, v); });
    })();

    // Date cible du webinaire : 11 octobre 2025 à 16h00
    const countdownDate = new Date("2026-07-18T16:00:00").getTime();

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Compteur de places
    const savedSpots = localStorage.getItem('webinaire_spots');
    if (savedSpots !== null) {
        document.getElementById('spots-count').textContent = savedSpots;
    }

    function updateCountdown() {
        const now = new Date().getTime();
        const distance = countdownDate - now;

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById("days").textContent = days.toString().padStart(2, '0');
        document.getElementById("hours").textContent = hours.toString().padStart(2, '0');
        document.getElementById("minutes").textContent = minutes.toString().padStart(2, '0');
        document.getElementById("seconds").textContent = seconds.toString().padStart(2, '0');

        if (distance < 0) {
            clearInterval(countdownInterval);
            document.querySelector(".countdown-timer").innerHTML = "<div class='countdown-value'>🎉 Le webinaire a commencé !</div>";
        }
    }

    const countdownInterval = setInterval(updateCountdown, 1000);
    updateCountdown();

    // Affichage d'erreur sur un champ
    function showFieldError(fieldName, message) {
        const input = document.getElementById(fieldName);
        if (input) {
            input.classList.add('field-error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            errorDiv.style.cssText = 'color: #ff5252; font-size: 0.8rem; margin-top: 5px;';
            input.parentNode.appendChild(errorDiv);
        }
    }

    // Erreur générique (popup)
    function showGenericError(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'error-alert';
        alertDiv.innerHTML = `
            <div class="alert-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button class="alert-close">&times;</button>
            </div>
        `;
        alertDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff5252;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(alertDiv);

        const closeButton = alertDiv.querySelector('.alert-close');
        closeButton.onclick = () => alertDiv.remove();
        setTimeout(() => {
            if (alertDiv.parentNode) alertDiv.remove();
        }, 5000);
    }

    // Styles d'alerte et d'erreur
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .error-alert .alert-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .error-alert .alert-close {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            margin-left: 10px;
        }
        .field-error {
            border-color: #ff5252 !important;
            box-shadow: 0 0 0 3px rgba(255, 82, 82, 0.2) !important;
        }
    `;
    document.head.appendChild(style);

    // Gestion du formulaire
    const form = document.getElementById('webinar-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Réinitialiser les erreurs précédentes
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('.field-error').forEach(el => el.classList.remove('field-error'));

        const formData = new FormData(form);

        // Construire l'objet data en cohérence avec le modèle Django
        const data = {
            prenom: formData.get('prenom').trim(),
            email: formData.get('email').trim(),
            profession: formData.get('profession').trim(),
            nom: '',
            niveau_etude: 'Non spécifié',
            utm_source:   sessionStorage.getItem('utm_source')   || '',
            utm_medium:   sessionStorage.getItem('utm_medium')   || '',
            utm_campaign: sessionStorage.getItem('utm_campaign') || '',
            gclid:        sessionStorage.getItem('gclid')        || '',
        };

        // Validation basique côté client
        if (!data.prenom) {
            showFieldError('prenom', 'Le prénom est obligatoire.');
            return;
        }
        if (!data.email) {
            showFieldError('email', 'L\'email est obligatoire.');
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement...';
        submitButton.disabled = true;

        // Diminuer le compteur de places
        function decreaseRemainingSpots() {
            const spotsElement = document.getElementById('spots-count');
            if (spotsElement) {
                let currentSpots = parseInt(spotsElement.textContent);
                if (currentSpots > 1) {
                    const newSpots = currentSpots - 1;
                    spotsElement.textContent = newSpots;
                    localStorage.setItem('webinaire_spots', newSpots);
                    if (newSpots === 0) {
                        document.getElementById('remaining-spots').style.backgroundColor = '#ff5252';
                    }
                }
            }
        }
        decreaseRemainingSpots();

        // Envoi AJAX
        fetch('/confirmation-inscription-webinaire/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.status >= 200 && response.status < 300) {
                return response.json();
            } else {
                return response.json().then(errorData => { throw errorData; });
            }
        })
        .then(data => {
            if (data.success) {
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push({ event: 'inscription-webinaire' });
                window.location.href = '/inscription-webinaire-confirmé/';
            } else {
                // Gestion des erreurs retournées par Django
                if (data.field_errors) {
                    for (const [field, error] of Object.entries(data.field_errors)) {
                        showFieldError(field, error);
                    }
                } else {
                    showGenericError(data.error || 'Une erreur est survenue.');
                }
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            if (error.field_errors) {
                for (const [field, msg] of Object.entries(error.field_errors)) {
                    showFieldError(field, msg);
                }
            } else if (error.error) {
                showGenericError(error.error);
            } else {
                showGenericError('Une erreur réseau est survenue. Veuillez réessayer.');
            }
        })
        .finally(() => {
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        });
        console.log('Réponse brute du serveur:', error);
    });

    // Animation périodique sur la section de présentation
    setInterval(function() {
        const presentationText = document.querySelector('.presentation-text');
        if (presentationText) {
            presentationText.classList.remove('highlight-animation');
            void presentationText.offsetWidth;
            presentationText.classList.add('highlight-animation');
        }
    }, 10000);
});