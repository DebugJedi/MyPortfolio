// console.log("Currently fotter visibility: ", footerVisible)

// arrowButton.addEventListener("click", () =>{
//     footerVisible = !footerVisible;

//     if(footerVisible) {
//         console.log("Currently fotter visibility: ", footerVisible)
//         footer.style.height = "70px";
//         arrowButton.innerHTML = "&#x2193;";

//     setTimeout(() => {
//         window.scrollTo({
//         top: document.body.scrollHeight,
//         behavior: "smooth", // Smooth scrolling
//         });
//     }, 100);
//     } else {
//     footer.style.height = "0px";
//     arrowButton.innerHTML = "&#x2191;";
//     }
// });


// hamburgerEl.addEventListener("click",() =>{
//     navEl.classList.toggle('nav--open');
//     hamburgerEl.classList.toggle('hamburger--open');
//   });

//   navEl.addEventListener("click",() =>{
//     navEl.classList.remove('nav--open');
//     hamburgerEl.classList.remove('hamburger--open');
//   });

class App {

constructor() {

    console.log("JavaScript is working!");
    this.footer = document.querySelector("footer");
    this.arrowButton = document.getElementById("arrow-button");
    this.footerVisible = false;
    this._initialize();
    // this._render();


}



_initialize() {
    this._setupFooterToogel(); //arrow to toggle footer between 0 - 40px
    // this._createLenis();
    this._trigger();
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
    // const footer = document.querySelector("footer");
    // const arrowButton = document.getElementById("arrow-button");
    // let footerVisible = false;


    hamburgerEl.addEventListener("click",() =>{
        navEl.classList.toggle('nav--open');
        hamburgerEl.classList.toggle('hamburger--open');
    });

    navEl.addEventListener("click",() =>{
        navEl.classList.remove('nav--open');
        hamburgerEl.classList.remove('hamburger--open');
    });

    // ++++ Page-2 Trigger ++++
    
    document.addEventListener('DOMContentLoaded', function () {
        const leftButton = document.querySelector('.page-2 .left-button i');
        const rightButton = document.querySelector('.page-2 .right-button i');
        const certificatesContainer = document.querySelector('.certificates');
        console.log("Page 2 trigger")
        // Scroll distance per click
        const scrollDistance = 300;
    
        // Scroll left
        leftButton.addEventListener('click', function () {
            certificatesContainer.scrollBy({
                left: -scrollDistance,
                behavior: 'smooth',
            });
        });
    
        // Scroll right
        rightButton.addEventListener('click', function () {
            certificatesContainer.scrollBy({
                left: scrollDistance,
                behavior: 'smooth',
            });
        });
    });


    // ++++ Page 3 Trigger ++++
    document.addEventListener("DOMContentLoaded", () => {
        const descContainer = document.querySelector(".page-3 .page3-box.left-section");
        const projectsContainer = document.querySelector(".page-3 .page3-box.projects");
        const leftButton = document.querySelector(".page-3 .projects-left-button");
        const rightButton = document.querySelector(".page-3 .projects-right-button");
        console.log("trigger for page 3")
        let currentIndex = 0; // Keeps track of the current visible project.
    
        const updateScroll = (direction) => {
            const descItems = document.querySelectorAll(".page-3 .left-section .desc");
            const projectItems = document.querySelectorAll(".page-3 .projects .item");
    
            const totalProjects = descItems.length;
    
            // Update index based on the direction
            if (direction === "right") {
                currentIndex = (currentIndex + 1) % totalProjects;
            } else if (direction === "left") {
                currentIndex = (currentIndex - 1 + totalProjects) % totalProjects;
            }
    
            // Calculate the scroll height and width dynamically
            const descHeight = descItems[currentIndex].offsetHeight;
            const projectWidth = projectItems[currentIndex].offsetWidth + 30; // Add 20px to width
    
            // Scroll the containers
            descContainer.scrollTo({
                top: descHeight * currentIndex,
                behavior: "smooth"
            });
    
            projectsContainer.scrollTo({
                left: projectWidth * currentIndex,
                behavior: "smooth"
            });
    
            // Add/remove 'visible' class to sync visibility
            descItems.forEach((desc, index) => {
                desc.classList.toggle("visible", index === currentIndex);
            });
    
            projectItems.forEach((item, index) => {
                item.classList.toggle("visible", index === currentIndex);
            });
        };
    
        // Event listeners for navigation buttons
        rightButton.addEventListener("click", () => updateScroll("right"));
        leftButton.addEventListener("click", () => updateScroll("left"));
    
        // Disable manual scrolling
        const disableManualScroll = (event) => {
            event.preventDefault();
            event.stopPropagation();
        };
    
        descContainer.addEventListener("wheel", disableManualScroll, { passive: false });
        descContainer.addEventListener("touchmove", disableManualScroll, { passive: false });
        projectsContainer.addEventListener("wheel", disableManualScroll, { passive: false });
        projectsContainer.addEventListener("touchmove", disableManualScroll, { passive: false });
    });
}

_render(time) {
    this.lenis.raf(time);

    requestAnimationFrame(this._render.bind(this))

}

}


new App();
