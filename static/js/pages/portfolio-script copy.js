/* ==========================================
   DATA SCIENCE PORTFOLIO - JAVASCRIPT
   Interactive Starfield + UI Interactions
   ========================================== */

// ==========================================
// INTERACTIVE STARFIELD (200 stars, 185px influence)
// ==========================================

class InteractiveStarfield {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.stars = [];
        this.constellations = [];
        this.mouse = { x: null, y: null };
        this.mouseTrail = [];
        
        // Configuration - DYNAMIC DENSITY: adjusts to screen size
        this.config = {
            starDensity: 0.00015,  // Stars per pixel (adjustable)
            influenceRadius: 185,
            maxBrightness: 1,
            minBrightness: 0.3,
            baseStarSize: 2,
            maxStarSize: 4,
            constellationOpacity: 0.3,
            constellationHighlightOpacity: 0.8,
            showConstellations: true,
            showMouseTrail: false,  // Disabled by default for cleaner look
            trailLength: 10
        };
        
        this.resize();
        this.init();
        this.setupEventListeners();
        this.animate();
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        // Recalculate star count based on screen area
        this.calculateStarCount();
    }
    
    calculateStarCount() {
        // Calculate stars based on screen area and density
        const area = this.canvas.width * this.canvas.height;
        this.config.starCount = Math.floor(area * this.config.starDensity);
        // Ensure minimum of 100 stars and maximum of 400 stars
        this.config.starCount = Math.max(100, Math.min(400, this.config.starCount));
    }
    
    init() {
        this.stars = [];
        this.constellations = [];
        
        // Create stars based on calculated density
        for (let i = 0; i < this.config.starCount; i++) {
            this.stars.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 2 + 1,
                brightness: Math.random() * 0.5 + 0.3,
                baseBrightness: Math.random() * 0.5 + 0.3,
                twinkleSpeed: Math.random() * 0.02 + 0.01,
                twinklePhase: Math.random() * Math.PI * 2,
                color: this.getStarColor()
            });
        }
        
        // Create constellations (connect nearby stars)
        this.createConstellations();
    }
    
    getStarColor() {
        const colors = [
            'rgba(96, 165, 250, ',   // Blue
            'rgba(167, 139, 250, ',  // Purple
            'rgba(244, 114, 182, ',  // Pink
            'rgba(251, 191, 36, ',   // Yellow
            'rgba(255, 255, 255, '   // White
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    createConstellations() {
        const connectionDistance = 120;
        
        for (let i = 0; i < this.stars.length; i++) {
            for (let j = i + 1; j < this.stars.length; j++) {
                const dx = this.stars[i].x - this.stars[j].x;
                const dy = this.stars[i].y - this.stars[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < connectionDistance) {
                    this.constellations.push({
                        star1: i,
                        star2: j,
                        distance: distance
                    });
                }
            }
        }
    }
    
    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => {
            this.resize();
            this.init();
        });
        
        // Mouse movement
        this.canvas.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
            
            // Add to mouse trail if enabled
            if (this.config.showMouseTrail) {
                this.mouseTrail.push({
                    x: this.mouse.x,
                    y: this.mouse.y,
                    alpha: 1
                });
                
                if (this.mouseTrail.length > this.config.trailLength) {
                    this.mouseTrail.shift();
                }
            }
        });
        
        // Mouse leave
        this.canvas.addEventListener('mouseleave', () => {
            this.mouse.x = null;
            this.mouse.y = null;
            this.mouseTrail = [];
        });
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw mouse trail (if enabled)
        if (this.config.showMouseTrail && this.mouseTrail.length > 0) {
            this.drawMouseTrail();
        }
        
        // Draw constellation lines
        if (this.config.showConstellations) {
            this.drawConstellations();
        }
        
        // Draw and update stars
        this.updateAndDrawStars();
        
        requestAnimationFrame(() => this.animate());
    }
    
    drawMouseTrail() {
        for (let i = 0; i < this.mouseTrail.length; i++) {
            const trail = this.mouseTrail[i];
            const alpha = (i / this.mouseTrail.length) * 0.5;
            const size = (i / this.mouseTrail.length) * 20;
            
            this.ctx.beginPath();
            const gradient = this.ctx.createRadialGradient(
                trail.x, trail.y, 0,
                trail.x, trail.y, size
            );
            gradient.addColorStop(0, `rgba(96, 165, 250, ${alpha})`);
            gradient.addColorStop(1, 'rgba(96, 165, 250, 0)');
            
            this.ctx.fillStyle = gradient;
            this.ctx.arc(trail.x, trail.y, size, 0, Math.PI * 2);
            this.ctx.fill();
        }
        
        // Fade out trail
        this.mouseTrail = this.mouseTrail.map(t => ({
            ...t,
            alpha: t.alpha * 0.95
        })).filter(t => t.alpha > 0.01);
    }
    
    drawConstellations() {
        this.constellations.forEach(constellation => {
            const star1 = this.stars[constellation.star1];
            const star2 = this.stars[constellation.star2];
            
            // Calculate if either star is near mouse (185px radius)
            let opacity = this.config.constellationOpacity;
            
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dist1 = this.getDistance(this.mouse.x, this.mouse.y, star1.x, star1.y);
                const dist2 = this.getDistance(this.mouse.x, this.mouse.y, star2.x, star2.y);
                
                if (dist1 < this.config.influenceRadius || dist2 < this.config.influenceRadius) {
                    opacity = this.config.constellationHighlightOpacity;
                }
            }
            
            // Draw line
            this.ctx.beginPath();
            this.ctx.strokeStyle = `rgba(96, 165, 250, ${opacity})`;
            this.ctx.lineWidth = 1;
            this.ctx.moveTo(star1.x, star1.y);
            this.ctx.lineTo(star2.x, star2.y);
            this.ctx.stroke();
        });
    }
    
    updateAndDrawStars() {
        this.stars.forEach(star => {
            // Natural twinkling
            star.twinklePhase += star.twinkleSpeed;
            const twinkle = Math.sin(star.twinklePhase) * 0.3;
            
            // Mouse influence (185px radius)
            let brightness = star.baseBrightness + twinkle;
            let size = star.size;
            
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const distance = this.getDistance(this.mouse.x, this.mouse.y, star.x, star.y);
                
                if (distance < this.config.influenceRadius) {
                    const influence = 1 - (distance / this.config.influenceRadius);
                    brightness = Math.min(1, brightness + influence * 0.7);
                    size = star.size + influence * 2;
                    
                    // Draw glow for nearby stars
                    this.ctx.beginPath();
                    const glowGradient = this.ctx.createRadialGradient(
                        star.x, star.y, 0,
                        star.x, star.y, size * 3
                    );
                    glowGradient.addColorStop(0, star.color + (brightness * 0.5) + ')');
                    glowGradient.addColorStop(1, star.color + '0)');
                    
                    this.ctx.fillStyle = glowGradient;
                    this.ctx.arc(star.x, star.y, size * 3, 0, Math.PI * 2);
                    this.ctx.fill();
                }
            }
            
            // Draw star
            this.ctx.beginPath();
            this.ctx.fillStyle = star.color + brightness + ')';
            this.ctx.arc(star.x, star.y, size, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }
    
    getDistance(x1, y1, x2, y2) {
        const dx = x1 - x2;
        const dy = y1 - y2;
        return Math.sqrt(dx * dx + dy * dy);
    }
}

// ==========================================
// INITIALIZE STARFIELD
// ==========================================

const canvas = document.getElementById('starfieldCanvas');
const starfield = new InteractiveStarfield(canvas);

console.log('🌟 Interactive Starfield Loaded');
console.log(`⚙️ Config: ${starfield.config.starCount} stars (dynamic density), 185px mouse influence`);
console.log(`📐 Screen: ${canvas.width}x${canvas.height}px`);

// ==========================================
// NAVIGATION SCROLL EFFECT
// ==========================================

const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// ==========================================
// MOBILE MENU TOGGLE
// ==========================================

const navToggle = document.getElementById('navToggle');
const navLinks = document.querySelector('.nav-links');

if (navToggle) {
    navToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Close menu when clicking a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });
}

// ==========================================
// ROTATING TEXT ANIMATION
// ==========================================

const rotatingTexts = ['Problem Solver', 'Data Scientist', 'ML Engineer', 'Innovator'];
let currentTextIndex = 0;
const rotatingTextElement = document.querySelector('.rotating-text');

if (rotatingTextElement) {
    setInterval(() => {
        currentTextIndex = (currentTextIndex + 1) % rotatingTexts.length;
        rotatingTextElement.style.opacity = '0';
        
        setTimeout(() => {
            rotatingTextElement.textContent = rotatingTexts[currentTextIndex];
            rotatingTextElement.style.opacity = '1';
        }, 300);
    }, 3000);
}

// ==========================================
// BACK TO TOP BUTTON
// ==========================================

const backToTopButton = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        backToTopButton.classList.add('visible');
    } else {
        backToTopButton.classList.remove('visible');
    }
});

if (backToTopButton) {
    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ==========================================
// CERTIFICATE CAROUSEL - 3×2 GRID (6 visible)
// ==========================================

class CertificateCarousel {
    constructor() {
        this.container = document.querySelector('.certificates-container');
        this.cards = document.querySelectorAll('.certificate-card');
        this.prevBtn = document.getElementById('certPrev');
        this.nextBtn = document.getElementById('certNext');
        
        // Check if elements exist
        if (!this.container || this.cards.length === 0) {
            console.warn('⚠️ Certificate carousel elements not found');
            return;
        }
        
        this.currentPage = 0;
        this.cardsPerPage = 6; // 3 columns × 2 rows
        this.totalPages = Math.ceil(this.cards.length / this.cardsPerPage);
        
        this.init();
    }
    
    init() {
        // Show first page
        this.showPage(0);
        
        // Add event listeners
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevPage());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextPage());
        }
        
        // Create pagination indicators
        this.createIndicators();
        
        console.log(`✅ Certificate carousel initialized: ${this.cards.length} cards, ${this.totalPages} pages`);
    }
    
    showPage(pageIndex) {
        this.currentPage = pageIndex;
        
        // Hide all cards
        this.cards.forEach((card, index) => {
            const startIndex = pageIndex * this.cardsPerPage;
            const endIndex = startIndex + this.cardsPerPage;
            
            if (index >= startIndex && index < endIndex) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
        
        // Update buttons
        this.updateButtons();
        
        // Update indicators
        this.updateIndicators();
    }
    
    updateButtons() {
        if (this.prevBtn) {
            this.prevBtn.disabled = this.currentPage === 0;
        }
        
        if (this.nextBtn) {
            this.nextBtn.disabled = this.currentPage === this.totalPages - 1;
        }
    }
    
    createIndicators() {
        const wrapper = document.querySelector('.certificates-wrapper');
        if (!wrapper || this.totalPages <= 1) return;
        
        const indicatorsDiv = document.createElement('div');
        indicatorsDiv.className = 'carousel-indicators';
        
        for (let i = 0; i < this.totalPages; i++) {
            const indicator = document.createElement('div');
            indicator.className = 'carousel-indicator';
            if (i === 0) indicator.classList.add('active');
            
            indicator.addEventListener('click', () => this.showPage(i));
            indicatorsDiv.appendChild(indicator);
        }
        
        wrapper.appendChild(indicatorsDiv);
    }
    
    updateIndicators() {
        const indicators = document.querySelectorAll('.carousel-indicator');
        indicators.forEach((indicator, index) => {
            if (index === this.currentPage) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }
    
    prevPage() {
        if (this.currentPage > 0) {
            this.showPage(this.currentPage - 1);
        }
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages - 1) {
            this.showPage(this.currentPage + 1);
        }
    }
}

// Initialize certificate carousel when page loads
if (document.querySelector('.certificates-container')) {
    const certCarousel = new CertificateCarousel();
}


// ==========================================
// CONTACT FORM VALIDATION
// ==========================================

const contactForm = document.getElementById('contactForm');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Get form fields
        const name = document.getElementById('name');
        const email = document.getElementById('email');
        const message = document.getElementById('message');
        
        let isValid = true;
        
        // Validate name
        if (name.value.trim() === '') {
            name.parentElement.classList.add('error');
            isValid = false;
        } else {
            name.parentElement.classList.remove('error');
        }
        
        // Validate email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value.trim())) {
            email.parentElement.classList.add('error');
            isValid = false;
        } else {
            email.parentElement.classList.remove('error');
        }
        
        // Validate message
        if (message.value.trim() === '') {
            message.parentElement.classList.add('error');
            isValid = false;
        } else {
            message.parentElement.classList.remove('error');
        }
        
        // If valid, submit (you can add your submission logic here)
        if (isValid) {
            alert('Message sent! (This is a demo - add your submission logic here)');
            contactForm.reset();
        }
    });
}

// ==========================================
// SMOOTH SCROLL FOR ANCHOR LINKS
// ==========================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==========================================
// CONSOLE EASTER EGG
// ==========================================

console.log('%c🚀 Debug Jedi Portfolio', 'color: #ef4444; font-size: 20px; font-weight: bold;');
console.log('%c✨ Interactive Starfield Active', 'color: #60a5fa; font-size: 14px;');
console.log('%cMove your mouse to interact with the stars!', 'color: #94a3b8; font-size: 12px;');