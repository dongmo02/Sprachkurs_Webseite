let anims=document.querySelectorAll(".anim")
          for ( let anim of anims)
              {

                 anim.addEventListener('click' , function() {
                    this.style.border = "2px solid red";
                    this.style.borderTop = " 0px black";

            });
             }


