
document.addEventListener('DOMContentLoaded', function () {
    const leftButton = document.querySelector('.page-2 .left-button i');
    const rightButton = document.querySelector('.page-2 .right-button i');
    const certificatesContainer = document.querySelector('.certificates');

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


document.addEventListener("DOMContentLoaded", () => {
    const descContainer = document.querySelector(".page-3 .page3-box.left-section");
    const projectsContainer = document.querySelector(".page-3 .page3-box.projects");
    const leftButton = document.querySelector(".page-3 .projects-left-button");
    const rightButton = document.querySelector(".page-3 .projects-right-button");

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
