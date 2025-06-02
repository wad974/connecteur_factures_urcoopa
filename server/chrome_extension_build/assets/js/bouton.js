// Fonction pour vérifier si nous sommes sur une page model = module
function isPOSPage() {
    const url = window.location.href;
    //console.log('URL : ', url)
    return url.includes('action=') && url.includes('cids=');
}



function injectScriptsHtmlFactureUrcoopaAdherent() {

    // Charger le fichier HTML
    fetch(chrome.runtime.getURL('assets/html/facture-ocr.html'))
        .then(response => response.text())
        .then(html => {
            // loading fin
            console.log('LOADING PAGE = FALSE');
            loadingPage(false);
            // Création d'un conteneur div pour template html facture            
            container = document.createElement("div");
            container.innerHTML = html
            container.id = "print-facture-container";
            container.style.position = "absolute";
            container.style.display = "block";
            container.style.top = "0";
            container.style.right = "0";
            container.style.left = "0";
            container.style.bottom = "0";
            container.style.width = "100%";
            container.style.height = "100%";
            container.style.border = "none";
            container.style.zindex = "9999";

            // ajout container
            bodyTableauBord = document.querySelector('.o_action_manager');
            bodyTableauBord.style.position = 'relative';
            bodyTableauBord.appendChild(container);

            // suppression barre recherche
            const barreSearch = document.querySelector('.o_control_panel .o_control_panel_actions');
            barreSearch.style.display = 'none !important';

            // ajout bouton close
            const BoutonClose = container.querySelector('.boutonFactureOcrRetour');

            // on injecte le bouton dans container
            //container.appendChild(BoutonClose);
            BoutonClose.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();

                if (container && container.parentNode === document.body) {
                    document.body.removeChild(container);
                } else if (container && container.parentNode) {
                    container.parentNode.removeChild(container);
                } else {
                    console.warn('❌ Impossible de retirer le conteneur : il n\'est pas dans le DOM ou déjà supprimé');
                }

                console.log('Bouton Close Sicalait Fermer');
            });

            const xhrButton = document.querySelector(".xhr");
            const log = document.querySelector(".event-log");

            function handleEvent(e) {
                log.textContent = `${log.textContent}${e.type}: ${e.loaded} bytes transferred\n`;
            }

            function addListeners(xhr) {
                xhr.addEventListener("loadstart", handleEvent);
                xhr.addEventListener("load", handleEvent);
                xhr.addEventListener("loadend", handleEvent);
                xhr.addEventListener("progress", handleEvent);
                xhr.addEventListener("error", handleEvent);
                xhr.addEventListener("abort", handleEvent);
            }

            xhrButton.addEventListener("click", () => {
                log.textContent = "";
                let url = "https://172.17.240.18:9898/factureAdherentUrcoopa";

                const xhr = new XMLHttpRequest();
                xhr.open("GET", url);
                addListeners(xhr);

                xhr.onload = () => {
                    if (xhr.status === 200) {

                        log.textContent += "\n✅ Réponse reçue :\n";
                        log.textContent += xhr.responseText;
                        console.info('✅ api chargé avec succès');

                    } else {
                        log.textContent += "\n❌ Erreur de chargement";
                    }
                };

                xhr.send();
            });

        })
        .catch(error => console.error('Erreur lors du chargement de la facture-ocr :', error));

}


// Fonction principale d'initialisation
function initPOSFactureUrcoopaAdherent() {
    console.log('Extension Lien Facture Urcoopa Adherent charger');

    // Ne continuer que si nous sommes sur une page POS
    if (!isPOSPage()) {
        console.log('Page non-POS détectée, extension lien facture-Urcoopa-Adherent inactive');
        return;
    }

    console.log('Page POS détectée, activation de l\'extension Lien-Facture-Urcoopa-Adherent');

    // Fonction pour créer le bouton du tiroir caisse
    function createCalculatriceButton() {
        try {
            const aDivBox = document.createElement('a');
            aDivBox.setAttribute('class', 'dropdown-item o_nav_entry facture-urcoopa-adherent-button');
            aDivBox.setAttribute('role', 'menuitem');
            aDivBox.setAttribute('tabindex', '1');
            aDivBox.setAttribute('href', 'http://172.17.240.18:9898/');
            aDivBox.setAttribute('data-hotkey', '2');
            aDivBox.setAttribute('aria-selected', 'false');
            aDivBox.setAttribute('data-section', '119');
            aDivBox.setAttribute('data-menu-xmlid', 'account.menu_action_out_move_urcoopa_adherent');
            aDivBox.innerHTML = 'Adherent-Urcoopa';
            aDivBox.style.cursor = 'pointer';
            
            /**
            aDivBox.addEventListener('click', function (e) {

                e.preventDefault();
                e.stopPropagation();
                console.log('Extension Facture-Adherent-Urcoopa cliquée');
                console.clear();

                // loading debut
                console.log('LOADING PAGE = TRUE');
                loadingPage(true);

                //injectScriptsHtmlFactureUrcoopaAdherent();

                console.log('LOADING PAGE = FALSE MAYBE');
                loadingPage(false);

            });
             */

            console.log('✅ Bouton Facture-Adherent-Urcoopa créé');
            return aDivBox;

        } catch (error) {
            console.error('❌ Erreur lors de la création du bouton :', error);
            return null;
        }
    }


    // etape 2 . Fonction pour injecter le bouton
    function injectButton() {
        console.log('🚀 Tentative d\'injection du bouton');
        const possibleContainers = [
            'div.o_menu_sections',
            '.o_main_navbar .o_menu_sections',
            '.o_navbar .o_main_navbar .o_menu_sections'
        ];

        for (const selector of possibleContainers) {
            const container = document.querySelector(selector);
            if (container) {
                console.log(`📦 Conteneur trouvé : ${selector}`);

                if (!document.querySelector('.facture-urcoopa-adherent-button')) {
                    const button = createCalculatriceButton();
                    if (button) {
                        container.appendChild(button); // 👍 l'ajout est fait ici
                        console.log('✅ Bouton injecté avec succès');
                        return true;
                    } else {
                        console.warn('⚠️ Impossible de créer le bouton');
                    }
                } else {
                    console.log('🔁 Bouton déjà présent, pas de duplication');
                    return false;
                }
            }
        }

        console.warn('❌ Aucun conteneur trouvé pour injection');
        return false;
    }

    // Variable pour compter les tentatives
    let attempts = 0;
    const MAX_ATTEMPTS = 5; // 30 secondes maximum

    // Fonction pour vérifier périodiquement et injecter le bouton
    function checkAndInject() {
        attempts++;
        if (attempts === 1) {
            console.log('Démarrage des tentatives d\'injection...');
        }

        if (injectButton()) {
            console.log('Injection réussie, arrêt des vérifications périodiques');
            return;
        }

        if (attempts >= MAX_ATTEMPTS) {
            console.log('Nombre maximum de tentatives atteint, arrêt des vérifications');
            return;
        }

        setTimeout(checkAndInject, 1000);
    }

    // etape 1 . Observer les changements dans le DOM pour les nouvelles opportunités d'injection
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.addedNodes.length && !document.querySelector('.facture-urcoopa-adherent-button')) {
                injectButton();
                break;
            }
        }
    });

    // Démarrer l'observation du DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });



}

// INIT BOUTON ECOUTE BOUTON COMPTA
console.log("🌐 Init recherche bouton comptabilité déclenché");

const observer = new MutationObserver((mutations, obs) => {
    const boutonCompta = document.querySelector("a[data-menu-xmlid='account_accountant.menu_accounting']");
    const DivCompta = document.querySelector("a[data-menu-xmlid='account.menu_board_journal_1']");


    if (boutonCompta) {
        console.log("✅ Bouton comptabilité détecté");

        boutonCompta.addEventListener('click', () => {
            console.log("🟢 Clic sur 'Comptabilité' détecté");

            // Démarrer l'extension
            setTimeout(() => {
                initPOSFactureUrcoopaAdherent();
            }, 0);
        }, { once: true });

        obs.disconnect(); // on arrête l'observation une fois trouvé
    }

    if (DivCompta) {
        console.clear();
        console.log("✅ Zone comptabilité détecté");

        // Démarrer l'extension
            setTimeout(() => {
                initPOSFactureUrcoopaAdherent();
            }, 0);
    }
});

// On observe tout le body pour détecter l’arrivée du bouton
observer.observe(document.body, {
    childList: true,
    subtree: true
});

console.log('🔍 Observateur DOM démarré pour bouton Comptabilité');