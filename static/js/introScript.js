class App {

  constructor() {

    console.log("JavaScript is working!");
    this.footer = document.querySelector("footer");
    this.arrowButton = document.getElementById("arrow-button");
    this.footerVisible = false;
    this._initialize();
    this._render();


  }

 

  _initialize() {
    this._setupFooterToogel();
    this._pageloader();
    this._initalanimation();
    this._createLenis();
    this._trigger();
    
    // this._startTypingEffect();
  }

  _setupFooterToogel() {
    this.arrowButton.addEventListener("click", () =>{
      this.footerVisible = !this.footerVisible;

      if(this.footerVisible) {
        this.footer.style.height = "70px";
        this.arrowButton.innerHTML = "&#x2193;";

        setTimeout(() => {
          window.scrollTo({
            top: document.body.scrollHeight,
            behavior: "smooth", // Smooth scrolling
          });
        }, 100);
      } else {
        this.footer.style.height = "0px";
        this.arrowButton.innerHTML = "&#x2191;";
      }
      

    });
  }

  _pageloader() {
    

    console.log("Page loader.....")
    
    const words = ["a Learner!", "a Curious Individual!", "an Analyst!"];
    let wordIndex = 0;
    let charIndex = 0;
    const typingElement = document.querySelector(".typing");

    function type() {
      if (charIndex < words[wordIndex].length) {
        typingElement.textContent += words[wordIndex].charAt(charIndex);
        charIndex++;
        setTimeout(type, 150); // Speed of typing
      } else {
        setTimeout(erase, 1000); // Delay before erasing
      }
    }

    function erase() {
      if (charIndex > 0) {
        typingElement.textContent = words[wordIndex].substring(0, charIndex - 1);
        charIndex--;
        setTimeout(erase, 100); // Speed of erasing
      } else {
        wordIndex = (wordIndex + 1) % words.length;
        setTimeout(type, 300); // Delay before typing next word
      }
    }

    // Start the animation
    type();
  }

  _initalanimation() {
    console.log("Scroll reveal...")
    ScrollReveal({ 
      reset: true,
      distance: '360px',
      duration: 2500,
      delay: 400 
    });

    
    ScrollReveal().reveal('.jedi',      {easing: 'ease-in', delay: 20, origin: "left" });
    // ScrollReveal().reveal('.left-box',  {easing: 'ease-in', delay: 20  , origin: "bottom" });
    // ScrollReveal().reveal('.right-box', {easing: 'ease-in', delay: 20  , origin: "top" });

  }

  _createLenis() {

    this.lenis = new Lenis({
      lerp: 0.1, // Smoothness factor
      smooth: true, // Enable smooth scrolling
      direction: 'vertical', // Scroll direction

    })

    // Listen to the scroll event
    const onScroll = (e) => {
      this.lenis.on(e); // Ensure Lenis manages the scroll event
    };
    window.addEventListener('scroll', onScroll);

    // Automatically render Lenis
    const raf = (time) => {
        this.lenis.raf(time);
        requestAnimationFrame(raf);
    };
    requestAnimationFrame(raf);
  }


  
  _trigger() {
    console.log("Starting contact.js...");
    const navEl = document.querySelector('nav');
    const hamburgerEl = document.querySelector('.hamburger');
    
    document.getElementById("send-button").addEventListener("click", function (event) {
        event.preventDefault();
        console.log("Clicked the send button...");

        // Get form data
        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const message = document.getElementById("message").value;
        
        // Validate form data
        if (!name || !email || !message) {
            alert("Please fill in all fields.");
            return;
        }

        const payload = { Name: name, Email: email, Message: message };
        console.log("Payload: ", payload);

        // Send data to FastAPI backend
        fetch("/post/message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Success: ", data);
                alert("Form submitted successfully!");
                console.log("Resetting the form...")
                document.getElementById("name").value = "";
                document.getElementById("email").value = "";
                document.getElementById("message").value = "";
                document.getElementById("contactForm").reset();
                
            })
            .catch((error) => {
                console.error("Error occurred: ", error.message);
                alert("There was an error submitting the form. Please try again.");
        });
});

  hamburgerEl.addEventListener("click",() =>{
    navEl.classList.toggle('nav--open');
    hamburgerEl.classList.toggle('hamburger--open');
  });

  navEl.addEventListener("click",() =>{
    navEl.classList.remove('nav--open');
    hamburgerEl.classList.remove('hamburger--open');
  });

  }

  _render(time) {
    this.lenis.raf(time);

    requestAnimationFrame(this._render.bind(this))

  }

}


new App();
