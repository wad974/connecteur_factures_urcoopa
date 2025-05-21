function ImprimerFacture() {
    let savedData = JSON.parse(localStorage.getItem("savedChildren"));
    let savedDataClients = JSON.parse(localStorage.getItem("savedChildrenClients"));

    if (!savedData || savedData.length === 0) {
        console.warn("Aucune donnée à imprimer !");
        return;
    }

    // Charger le fichier HTML
    fetch(chrome.runtime.getURL('assets/html/printFacture.html'))
        .then(response => response.text())
        .then(html => {

            console.log(savedData);

            // Création d'un iframe pour impression chrome
            iframe = document.createElement("iframe");
            iframe.id = "print-frame";
            iframe.style.position = "absolute";
            iframe.style.width = "0px";
            iframe.style.height = "0px";
            iframe.style.border = "none";
            document.body.appendChild(iframe);



            let doc = iframe.contentDocument || iframe.contentWindow.document;
            doc.open();

            // Construire le contenu HTML pour l'impression
            let htmlContent = `
                                
                                    
                                    <style>
                                        section { font-family: Arial, sans-serif; padding: 20px; }
                                        .receipt-container { border: 1px solid #000; padding: 10px; margin: 10px; }
                                    </style>
                                <section>
                                    <h2>Facture</h2>
                                    <div class="receipt-container">
                            `;

            // Ajouter chaque élément stocké
            
            savedData.forEach(item => {
                
                htmlContent += `<div class="${item.classes.join(' ')}" id="${item.id}">${item.html}</div>`;

            });

            htmlContent += `
                                    </div>
                                    <script>
                                        window.onload = function() {
                                            window.print();
                                        };
                                    </script>
                                </section>
                            `;

            doc.write(htmlContent);
            doc.close();

            // Attendre un petit moment pour être sûr que l'iframe est chargé avant de lancer l'impression
            setTimeout(() => {
                iframe.contentWindow.focus();
                iframe.contentWindow.print();
            }, 100);

        })
        .catch(error => console.error('Erreur lors du chargement de la facture pour impression :', error));

}



function ReupereTousLesEnfants() {
    // Sélectionner l'élément parent dont on veut récupérer les enfants

    if (document.querySelector(".pos-receipt"))
    {
        let parent = document.querySelector(".pos-receipt");

        // Récupérer tous les enfants directs
        let enfants = Array.from(parent.children);

        // Stocker leurs informations dans un tableau
        let data = enfants.map(child => ({
            html: child.innerHTML,       // Contenu HTML
            text: child.textContent,     // Texte
            id: child.id,                // ID
            classes: Array.from(child.classList), // Liste des classes
            src: child.src // source img
        }));

        // Pour stocker temporairement et réutiliser après un rechargement de page :
        localStorage.setItem("savedChildren", JSON.stringify(data));

        // Pour récupérer les données plus tard :
        let savedData = JSON.parse(localStorage.getItem("savedChildren"));
    }
    

    if (document.querySelector(".partner-list-contents"))
    {
        let parentClients = document.querySelector(".partner-list-contents");
        console.log(parentClients);

        // Récupérer tous les enfants directs
        let enfantsClients = Array.from(parentClients.children);
        console.log(enfantsClients);

        // Stocker leurs informations dans un tableau
        let dataClients = enfantsClients.map(child => ({
            html: child.innerHTML,       // Contenu HTML
            text: child.textContent,     // Texte
            id: child.id,                // ID
            classes: Array.from(child.classList), // Liste des classes
        }));

        //console.log(data);

        // Pour stocker temporairement et réutiliser après un rechargement de page :
        localStorage.setItem("savedChildrenClients", JSON.stringify(dataClients));

        // Pour récupérer les données plus tard :
        let savedDataClients = JSON.parse(localStorage.getItem("savedChildrenClients"));
        //console.log(savedData);
    }
}



// Fonction pour vérifier et exécuter l'action si le bouton est présent
function checkAndExecute() {
    const divReceipt = document.querySelector(".receipt-screen");
    if (divReceipt) {

        const divButtons = document.querySelector('.actions .d-flex .buttons');
        if (!divButtons) {
            console.warn("Impossible de trouver le conteneur des boutons !");
            return;
        }

        // Vérifier si le bouton existe déjà pour éviter les doublons
        if (!document.querySelector('.print-facture-button')) {
            let buttonPrintFacture = document.createElement('button');
            buttonPrintFacture.innerHTML = '<i class="fa fa-print ms-2" role="img" aria-label="Impression facture" title="Impression facture"></i> Imprimer la facture';
            buttonPrintFacture.className = 'button print btn btn-lg btn-secondary w-100 py-3 mt-4 print-facture-button';

            // Ajouter un événement au bouton
            buttonPrintFacture.addEventListener('click', () => {
                console.log("Bouton 'Imprimer la facture' cliqué !");
                // Ajoute ici le code pour l'impression
                ImprimerFacture();
            });

            // Injection du bouton
            divButtons.appendChild(buttonPrintFacture);
            console.log('Bouton imprimer facture ajouté avec succès!');
        }
    }
}



// Observer les changements dans la page POS d'Odoo
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === "childList" || mutation.type === "attributes") {
            checkAndExecute();
            ReupereTousLesEnfants();
        }
    });
});



// Cibler le `body` pour surveiller les changements dans le DOM
observer.observe(document.body, { childList: true, subtree: true });



// Vérification initiale au chargement de la page
checkAndExecute();




async function postData(url = "") {
    // Les options par défaut sont indiquées par *
    fetch( url, {
        mode: 'no-cors',
        method: 'GET',
        headers: {
            'Accept': '*/*'
        }
    })
        .then(() => {
            // En mode no-cors, on ne peut pas accéder à response.ok
            console.log('Tiroir ouvert avec succès');
        })
        .catch(error => {
            console.error('Erreur:', error);
        });// transforme la réponse JSON reçue en objet JavaScript natif
}






// ici fuuntion post data
postData(url).then((donnees) => {

    console.log(donnees); // Les données JSON analysées par l'appel `donnees.json()`

});
