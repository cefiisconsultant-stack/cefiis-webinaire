
       // Animation au défilement
        document.addEventListener('DOMContentLoaded', function() {
            const elements = document.querySelectorAll('.content section, .highlight, .testimonial, .fade-in');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = 1;
                        entry.target.style.transform = 'translateY(0)';
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.1 });
            
            elements.forEach(element => {
                element.style.opacity = 0;
                element.style.transform = 'translateY(30px)';
                element.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
                observer.observe(element);
            });

            // Effet d'onde pour les boutons CTA
            const waveButtons = document.querySelectorAll('.wave-effect');
            waveButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    let wave = document.createElement('span');
                    wave.classList.add('wave');
                    this.appendChild(wave);
                    
                    setTimeout(() => {
                        wave.remove();
                    }, 2000);
                });
            });
            
            // Ajout d'effets de clic pour les boutons
            const buttons = document.querySelectorAll('button');
            buttons.forEach(button => {
                button.addEventListener('click', function() {
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 200);
                });
            });
        });

        // Animation de vague au clic
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('cta-button') || e.target.classList.contains('floating-cta-button') || e.target.classList.contains('mini-cta-button')) {
                e.preventDefault();
                
                let x = e.clientX - e.target.getBoundingClientRect().left;
                let y = e.clientY - e.target.getBoundingClientRect().top;
                
                let ripple = document.createElement('span');
                ripple.classList.add('ripple');
                ripple.style.left = `${x}px`;
                ripple.style.top = `${y}px`;
                
                e.target.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            }
        });
        
        // Fonction pour le menu déroulant
        function toggleDropdown() {
            const dropdownContent = document.querySelector('.dropdown-content');
            const toggleButton = document.querySelector('.dropdown-toggle');
            
            dropdownContent.classList.toggle('show');
            toggleButton.classList.toggle('expanded');
            
            // Changer le texte du bouton
            if (dropdownContent.classList.contains('show')) {
                toggleButton.innerHTML = 'Masquer les croyances <span class="arrow">▼</span>';
            } else {
                toggleButton.innerHTML = 'Voir les 2 croyances suivantes <span class="arrow">▼</span>';
            }
        }

