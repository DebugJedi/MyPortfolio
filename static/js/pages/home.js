/* ==========================================
   DATA SCIENCE PORTFOLIO - JAVASCRIPT
   Interactive Starfield + UI Interactions
   ========================================== */

// ==========================================
// INTERACTIVE STARFIELD (200 stars, 185px influence)
// ==========================================

class InteractiveStarfield {
    constructor(canvas) {
        if (!canvas) {
            console.error('❌ Canvas element not found!');
            return;
        }
        
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
        
        console.log('✅ Starfield initialized successfully');
        console.log(`📊 ${this.config.starCount} stars created`);
        console.log(`🎯 185px mouse influence radius`);
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
        
        // Mouse movement - CRITICAL FOR INTERACTION!
        this.canvas.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
            
            // Debug log (remove after testing)
            if (Math.random() < 0.01) {  // Log occasionally to avoid spam
                console.log('🖱️ Mouse:', this.mouse.x, this.mouse.y);
            }
            
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

console.log('🚀 Starfield script loaded');

const canvas = document.getElementById('starfieldCanvas');
if (!canvas) {
    console.error('❌ ERROR: Canvas element #starfieldCanvas not found!');
    console.error('Make sure <canvas id="starfieldCanvas"></canvas> exists in your HTML');
} else {
    console.log('✅ Canvas element found');
    const starfield = new InteractiveStarfield(canvas);
    
    // Make starfield globally accessible for debugging
    window.debugStarfield = starfield;
    
    // FIX: Ensure canvas sizes correctly after page fully loads
    setTimeout(() => {
        const currentHeight = window.innerHeight;
        if (canvas.height !== currentHeight) {
            console.log(`🔧 Auto-fixing canvas: ${canvas.height}px → ${currentHeight}px`);
            starfield.resize();
            starfield.init();
        }
    }, 100);
    
    // Also fix on window load (backup)
    window.addEventListener('load', () => {
        const currentHeight = window.innerHeight;
        if (canvas.height !== currentHeight) {
            console.log(`🔧 Final resize on load: ${canvas.height}px → ${currentHeight}px`);
            starfield.resize();
            starfield.init();
        }
    });
}

// ==========================================
// NAVIGATION SCROLL EFFECT
// ==========================================

const header = document.querySelector('.header');

if (header) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

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

if (backToTopButton) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });

    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/* ==========================================
   SIMPLE CERTIFICATE CAROUSEL - GUARANTEED TO WORK
   Add this to the END of portfolio-script.js
   Replace everything after line 392 (the carousel section)
   ========================================== */

// ==========================================
// CERTIFICATE CAROUSEL - SIMPLE VERSION
// ==========================================

function initCertificateCarousel() {
    const container = document.querySelector('.certificates-container');
    const cards = document.querySelectorAll('.certificate-card');
    const prevBtn = document.getElementById('certPrev');
    const nextBtn = document.getElementById('certNext');
    
    if (!container || cards.length === 0) {
        console.log('ℹ️ No certificates on this page');
        return;
    }
    
    console.log(`🎯 Found ${cards.length} certificates`);
    
    let currentPage = 0;
    const cardsPerPage = 6; // 3×2 grid
    const totalPages = Math.ceil(cards.length / cardsPerPage);
    
    console.log(`📄 Total pages: ${totalPages}`);
    
    function showPage(pageIndex) {
        console.log(`📖 Showing page ${pageIndex + 1} of ${totalPages}`);
        
        // Hide all cards
        cards.forEach((card, index) => {
            const startIndex = pageIndex * cardsPerPage;
            const endIndex = startIndex + cardsPerPage;
            
            if (index >= startIndex && index < endIndex) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
        
        // Update buttons
        if (prevBtn) {
            prevBtn.disabled = (pageIndex === 0);
        }
        
        if (nextBtn) {
            nextBtn.disabled = (pageIndex === totalPages - 1);
        }
    }
    
    // Event listeners
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            console.log('⬅️ Previous clicked');
            if (currentPage > 0) {
                currentPage--;
                showPage(currentPage);
            }
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            console.log('➡️ Next clicked');
            if (currentPage < totalPages - 1) {
                currentPage++;
                showPage(currentPage);
            }
        });
    }
    
    // Show first page
    showPage(0);
    
    console.log('✅ Certificate carousel initialized successfully!');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCertificateCarousel);
} else {
    initCertificateCarousel();
}

