// loading page 

async function loadingPage(statut) {

    // Charger le fichier HTML
    

        await fetch(chrome.runtime.getURL('assets/html/loading-page.html'))
        .then(response => response.text())
        .then(html => {

            // Création d'un conteneur div pour template html facture            
            container = document.createElement("div");
            container.innerHTML = html
            container.id = "print-loadingPage-container";
            container.style.position = "absolute";
            container.style.display = "block";
            container.style.top = "0%";
            container.style.left = "0%";
            container.style.bottom = "0%";
            container.style.right = "0%";
            container.style.width = "100%";
            container.style.height = "100%";
            container.style.border = "none";
            container.style.zIndex = '9999';
            container.style.backgroundColor = 'rgba(0,0,0,0.5)';

            if  ( statut == true ) {

            // ajout container
            document.body.appendChild(container);

            }

            if ( statut == false )
            {
                // retire container
                let wrapper = document.getElementById('print-loadingPage-container');

                console.log( 'ICI WRAPPER' , wrapper);
                
                wrapper.style.display = 'none';
                document.body.removeAttribute(wrapper);
                document.body.removeChild(container);
            }

            return statut
        })
        .catch(error => console.error('Erreur lors du chargement de la apprentissage-ocr :', error));

    
    
}

