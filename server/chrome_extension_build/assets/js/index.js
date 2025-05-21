// ADD TABLEAU DANS ARTICLE
function addRow() {
    const table = document.querySelector('#articles-table tbody');
    const row = table.rows[0].cloneNode(true);
    row.querySelectorAll('input').forEach(input => input.value = '');
    table.appendChild(row);
}

// SWTICH TAB
function switchTab() {

    // tab boutons
    const btnArticle = document.querySelector('.btn-tab-article');
    const btnGenerale = document.querySelector('.btn-tab-generale');

    // blocs tab
    const tabInfoGen = document.querySelector('#information-generale');
    const tabInfoArticle = document.querySelector('#information-article');

    console.log(tabInfoArticle)
    console.log(tabInfoGen)

    // Initialiser l'état
    tabInfoArticle.style.display = 'none';

    // action sur les tabs
    btnArticle.addEventListener('click', (event) => {
        event.preventDefault();
        console.log('Bouton article');

        tabInfoGen.style.display = 'none';
        tabInfoArticle.style.display = 'block';
    });

    btnGenerale.addEventListener('click', (event) => {
        event.preventDefault();
        console.log('Bouton generale');

        tabInfoArticle.style.display = 'none';
        tabInfoGen.style.display = 'block';
    });
}

// champs apprentissage à recuperere

async function uploadFileChampsApprentissage() {
    // On récupère le formulaire
    const form = document.getElementById('myForm');
    const btnEnvoyerApprentissage = document.querySelector('.o_form_button_save')

    btnEnvoyerApprentissage.addEventListener('click', async (event) => {
        event.preventDefault();  // Empêcher le rechargement de la page

        // loadingPage
        loadingPage(true);

        let formData = new FormData();
        console.log("Données envoyées :", [...formData.entries()]);

        // Récupérer le fichier PDF
        let fileInput = document.getElementById("file_input");
        if (!fileInput || fileInput.files.length === 0) {
            alert("Veuillez sélectionner un fichier PDF.");
            return;
        }
        formData.append("file", fileInput.files[0]);

        // Récupérer les autres champs du formulaire
        let fields = [
            "nomFournisseurFacture",
            "numeroFacture",
            "numeroReferenceFacture",
            "numeroClientFacture",
            "dateFacture",
            "numeroReferenceArticleFacture",
            "numeroDesignationArticleFacture",
            "eanFacture",
            "quantiteFacture",
            "remiseFacture",
            "montantArticleFacture"
        ];

        fields.forEach(field => {
            let inputElement = document.getElementsByName(field);
            if (inputElement.length > 0) {
                formData.append(field, inputElement[0].value);  // Prend la première occurrence
            } else {
                console.warn(`Champ "${field}" non trouvé dans le formulaire.`);
            }
        });

        console.log("Données envoyées :", [...formData.entries()]);

        try {
            let response = await fetch("http://127.0.0.1:8888/uploadApprentissage/", {
                method: "POST",
                body: formData
            });

            let result = await response.json();
            console.info("Réponse du serveur :", result);

            // loadingPage
            loadingPage(false);
            //on close container
            document.body.removeChild(container);

        } catch (error) {
            console.error("Erreur lors de l'envoi du formulaire :", error);
        }
    });
}



// apprentissage html
async function injectScriptsHtmlApprentisssageOcr() {

    // Charger le fichier HTML
    await fetch(chrome.runtime.getURL('assets/html/apprentissage-ocr.html'))
        .then(response => response.text())
        .then(html => {

            // Création d'un conteneur div pour template html facture            
            divApprentissage = document.createElement("div");
            divApprentissage.innerHTML = html
            divApprentissage.id = "print-apprentissage-container";
            divApprentissage.style.position = "absolute";
            divApprentissage.style.display = "flex";
            divApprentissage.style.alignItems = "center";
            divApprentissage.style.top = "0%";
            divApprentissage.style.left = "0%";
            divApprentissage.style.bottom = "0%";
            divApprentissage.style.right = "0%";
            divApprentissage.style.width = "100%";
            divApprentissage.style.height = "100%";
            divApprentissage.style.border = "none";
            divApprentissage.style.zIndex = '1000';
            divApprentissage.style.backgroundColor = 'rgba(0,0,0,0.25)';

            // ajout container
            document.body.appendChild(container);
            // ajout bouton close
            const boutonIgnorerApprentissage = document.querySelector('.o_form_button_cancel');
            const boutonCloseApprentissage = document.querySelector('.btn-close-apprentissage');

            // on injecte le bouton dans container
            //container.appendChild(BoutonClose);
            function closeApprentissage() {
                document.body.removeChild(container);
                console.log('Bouton Close Sicalait Fermer');
            }

            boutonIgnorerApprentissage.addEventListener('click', closeApprentissage);
            boutonCloseApprentissage.addEventListener('click', closeApprentissage);

            // tab
            switchTab();

            //ajout ligne
            const btnAddLigne = document.getElementById('btnAjouteLigne')
            btnAddLigne.addEventListener('click', addRow);

            // Apprentissage champs recuperer
            uploadFileChampsApprentissage(container);
            //const btnEnvoyerApprentissage = document.querySelector('.o_form_button_save')
            //btnEnvoyerApprentissage.addEventListener('click', uploadFileChampsApprentissage)
        })
        .catch(error => console.error('Erreur lors du chargement de la apprentissage-ocr :', error));

}
