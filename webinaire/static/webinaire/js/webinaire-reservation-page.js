document.addEventListener('DOMContentLoaded', function() {
    // Date cible du webinaire : 14 septembre 2025 à 20h00
    const countdownDate = new Date("2025-10-11T16:00:00").getTime();

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
    
    // Mettre à jour le compte à rebours toutes les secondes
    const countdownInterval = setInterval(updateCountdown, 1000);
    updateCountdown();     
    
    // Fonction pour afficher les erreurs de champ
    function showFieldErrors(fieldErrors) {
        // Réinitialiser les erreurs précédentes
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('.field-error').forEach(el => el.classList.remove('field-error'));
        
        // Afficher les nouvelles erreurs
        for (const [field, error] of Object.entries(fieldErrors)) {
            let input;
            
            // Gestion spéciale pour le champ niveau_etude (boutons radio)
            if (field === 'niveau_etude') {
                const radioContainer = document.querySelector('.radio-group');
                input = radioContainer;
                
                // Ajouter la classe d'erreur à tous les boutons radio
                document.querySelectorAll('input[name="niveau_etude"]').forEach(radio => {
                    radio.classList.add('field-error');
                });
            } else {
                input = document.getElementById(field) || document.querySelector(`[name="${field}"]`);
                if (input) {
                    input.classList.add('field-error');
                }
            }
            
            if (input) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = error;
                errorDiv.style.cssText = 'color: #ff5252; font-size: 0.8rem; margin-top: 5px;';
                
                // Positionner l'erreur différemment pour les boutons radio
                if (field === 'niveau_etude') {
                    input.parentNode.insertBefore(errorDiv, input.nextSibling);
                } else {
                    input.parentNode.appendChild(errorDiv);
                }
            } else {
                showGenericError(error);
            }
        }
    }
    
    // Fonction pour afficher une erreur générique
    function showGenericError(message) {
        // Créer une alerte stylisée
        const alertDiv = document.createElement('div');
        alertDiv.className = 'error-alert';
        alertDiv.innerHTML = `
            <div class="alert-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button class="alert-close">&times;</button>
            </div>
        `;
        
        // Style pour l'alerte
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
        
        // Fermer l'alerte après 5 secondes ou quand on clique sur la croix
        const closeButton = alertDiv.querySelector('.alert-close');
        closeButton.onclick = () => alertDiv.remove();
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    // Ajouter l'animation pour l'alerte
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
        
        input[type="radio"].field-error + label {
            color: #ff5252;
        }
    `;
    document.head.appendChild(style);
    
    // Gestion du formulaire avec AJAX
    const form = document.getElementById('webinar-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Récupération des données du formulaire
        const formData = new FormData(form);
        const niveauEtude = document.querySelector('input[name="niveau_etude"]:checked');
        
        const data = {
            prenom: formData.get('prenom'),
            nom: formData.get('nom'),
            email: formData.get('email'),
            profession: formData.get('profession'),
            niveau_etude: niveauEtude ? niveauEtude.value : ''
        };
        
        // Désactiver le bouton pour éviter les doubles soumissions
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Traitement en cours...';
        submitButton.disabled = true;

            // 🔥 Fonction pour diminuer le compteur de places
            function decreaseRemainingSpots() {
                const spotsElement = document.getElementById('spots-count');
                if (spotsElement) {
                    let currentSpots = parseInt(spotsElement.textContent);
                    if (currentSpots > 1) {
                        const newSpots = currentSpots - 1;
                        spotsElement.textContent = newSpots;
                        // Sauvegarder dans le localStorage
                        localStorage.setItem('webinaire_spots', newSpots);
                        
                        if (newSpots === 0) {
                            document.getElementById('remaining-spots').style.backgroundColor = '#ff5252';
                        }
                    }
                }
            }

        // 🔥 DIMINUER LE COMPTEUR DE PLACES IMMÉDIATEMENT
        decreaseRemainingSpots();
        
        fetch('/confirmation-inscription-webinaire/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            // Vérifier si la réponse est OK (200-299) ou une erreur (400-499)
            if (response.status >= 200 && response.status < 300) {
                return response.json();
            } else {
                // Pour les erreurs 400, on peut aussi récupérer le JSON
                return response.json().then(errorData => {
                    throw errorData;
                });
            }
        })
        .then(data => {
            if (data.success) {
                console.log('Success:', data);

                // Pousser l'événement dans la couche de données
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push({
                    event: 'inscription-webinaire'
                });

                // Redirection vers la page de confirmation
                window.location.href = '/inscription-webinaire-confirmé/';
            } else {
                // Afficher les erreurs de validation
                if (data.field_errors) {
                    showFieldErrors(data.field_errors);
                } else {
                    showGenericError(data.error || 'Une erreur est survenue');
                }
            }
        })
        .catch((error) => {
            console.error('Erreur:', error);
            
            if (error.field_errors) {
                // C'est une erreur de validation Django
                showFieldErrors(error.field_errors);
            } else if (error.error) {
                // C'est une erreur avec un message
                showGenericError(error.error);
            } else {
                // Erreur réseau ou autre
                showGenericError('Une erreur réseau est survenue. Veuillez vérifier votre connexion et réessayer.');
            }
        })
        .finally(() => {
            // Réactiver le bouton
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        });
    });
    
        // Répéter l'animation de mise en évidence toutes les 10 secondes
        setInterval(function() {
            document.querySelector('.presentation-text').classList.remove('highlight-animation');
            void document.querySelector('.presentation-text').offsetWidth; // Déclencher un reflow
            document.querySelector('.presentation-text').classList.add('highlight-animation');
        }, 10000);
        // AJOUTER ce code à la fin de votre fichier JS, avant le }); final

    // Amélioration de l'UX pour les boutons radio
    const radioOptions = document.querySelectorAll('.radio-option');

    radioOptions.forEach(option => {
        // Clic sur toute la zone
        option.addEventListener('click', function(e) {
            const radioInput = this.querySelector('input[type="radio"]');
            if (radioInput && !radioInput.disabled) {
                radioInput.checked = true;
                updateRadioSelection();
                
                // Déclencher l'événement change pour les écouteurs existants
                radioInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        // Empêcher la double activation quand on clique directement sur l'input
        const radioInput = option.querySelector('input[type="radio"]');
        if (radioInput) {
            radioInput.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    });

    // Mettre à jour visuellement la sélection
    function updateRadioSelection() {
        radioOptions.forEach(option => {
            const radioInput = option.querySelector('input[type="radio"]');
            if (radioInput && radioInput.checked) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }

    // Initialiser l'état de sélection
    updateRadioSelection();

    // Mettre à jour quand l'utilisateur change avec le clavier
    document.querySelectorAll('input[name="niveau_etude"]').forEach(radio => {
        radio.addEventListener('change', updateRadioSelection);
    });

    // ... (votre code existant continue ici) ...
});