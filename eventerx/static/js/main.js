(function () {

    // get all elements ment to invoke modals and attach events handlers
    document.querySelectorAll('.modal_invoke').forEach( button => {
        button.addEventListener('click',  function () {
            let target_modal_id = this.getAttribute('data-modal')
            if (target_modal_id) {
                let modal = document.querySelector(target_modal_id)
                if (modal) {
                    modal.classList.toggle("--shown")
                }  else {
                    console.log("no modal");
                }
            } else {
                console.log("no modal id");
            }
        })
    })

    document.querySelectorAll('.drop_zone').forEach( zone => {
        zone.addEventListener('dragenter', function(){
            this.style.backgroundColor = "#eeeeee";
        })
        zone.addEventListener('dragleave', function(){
            this.style.backgroundColor = "transparent";
        })
    })

})();