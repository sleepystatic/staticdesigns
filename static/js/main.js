// ============================================
// STATIC DESIGNS - MAIN JAVASCRIPT
// ============================================

document.addEventListener('DOMContentLoaded', function() {

    // ============================================
    // MOBILE MENU TOGGLE
    // ============================================
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mobileNav = document.getElementById('mobileNav');

    if (mobileMenuToggle && mobileNav) {
        function setMenuOpen(open) {
            mobileMenuToggle.classList.toggle('active', open);
            mobileNav.classList.toggle('active', open);
            mobileMenuToggle.setAttribute('aria-expanded', open);
        }

        mobileMenuToggle.addEventListener('click', function() {
            setMenuOpen(!mobileNav.classList.contains('active'));
        });

        // Close mobile menu when clicking a link
        const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', function() {
                setMenuOpen(false);
            });
        });

        // Close mobile menu when clicking outside or pressing Escape
        document.addEventListener('click', function(event) {
            const isClickInsideNav = mobileNav.contains(event.target);
            const isClickOnToggle = mobileMenuToggle.contains(event.target);

            if (!isClickInsideNav && !isClickOnToggle && mobileNav.classList.contains('active')) {
                setMenuOpen(false);
            }
        });

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && mobileNav.classList.contains('active')) {
                setMenuOpen(false);
                mobileMenuToggle.focus();
            }
        });
    }

    // ============================================
    // PORTFOLIO CAROUSEL
    // ============================================
    const carouselTrack = document.querySelector('.portfolio-carousel-track');
    const prevBtn = document.getElementById('carouselPrev');
    const nextBtn = document.getElementById('carouselNext');

    if (carouselTrack && prevBtn && nextBtn) {
        const scrollAmount = 320; // Width of item + gap

        prevBtn.addEventListener('click', function() {
            carouselTrack.scrollBy({
                left: -scrollAmount,
                behavior: 'smooth'
            });
        });

        nextBtn.addEventListener('click', function() {
            carouselTrack.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        });

        // The arrows are hidden on phones (style.css), so skip measuring there: it forces a full layout on load
        const arrowsHidden = window.matchMedia('(max-width: 767px)');

        // Update button visibility based on scroll position
        function updateCarouselButtons() {
            if (arrowsHidden.matches) return;
            const maxScroll = carouselTrack.scrollWidth - carouselTrack.clientWidth;

            if (carouselTrack.scrollLeft <= 0) {
                prevBtn.style.opacity = '0.5';
                prevBtn.style.cursor = 'default';
            } else {
                prevBtn.style.opacity = '1';
                prevBtn.style.cursor = 'pointer';
            }

            if (carouselTrack.scrollLeft >= maxScroll - 1) {
                nextBtn.style.opacity = '0.5';
                nextBtn.style.cursor = 'default';
            } else {
                nextBtn.style.opacity = '1';
                nextBtn.style.cursor = 'pointer';
            }
        }

        carouselTrack.addEventListener('scroll', updateCarouselButtons);
        window.addEventListener('resize', updateCarouselButtons);
        updateCarouselButtons(); // Initial check
    }

    // ============================================
    // HERO SHOWCASE
    // ============================================
    // Desktop: the browser frame shows one screenshot that fades to the next project every 5 seconds.
    // Phones: the phone frame's screen is a strip of all three phone screenshots (index.html). It's a native
    // scrolling area, so it follows a finger and snaps to one page (style.css), and it slides to the next page
    // every 5 seconds, pausing while it's touched.
    const heroImg = document.getElementById('heroShowcaseImg');
    const heroSlides = document.getElementById('heroSlides');
    const browserUrl = document.getElementById('browserUrlText');
    const indicators = document.querySelectorAll('.indicator-bar');

    if (heroImg && heroSlides && browserUrl && indicators.length) {
        // Desktop screenshot base name, address bar text, and alt text, in the same order as the strip and the bars
        const showcaseProjects = [
            { img: '/static/images/mqb-preview', url: 'moore-qualitybuilders.com', alt: 'Moore Quality Builders' },
            { img: '/static/images/pixelflip-dashboard-preview', url: 'dashboard.pixelflip.app', alt: 'PixelFlip Dashboard' },
            { img: '/static/images/gbr-preview', url: 'gameboyretreat.com', alt: 'Gameboy Retreat' }
        ];
        const slides = Array.from(heroSlides.querySelectorAll('.hero-slide'));
        const phoneLayout = window.matchMedia('(max-width: 767px)');
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        const ROTATE_MS = 5000;
        let currentIndex = 0;
        let rotationTimer;

        function markActive(index) {
            currentIndex = index;
            indicators.forEach((bar, i) => bar.classList.toggle('active', i === index));
        }

        // Desktop: put another project's screenshot and address in the browser frame
        function setDesktopProject(index) {
            const project = showcaseProjects[index];
            heroImg.srcset = `${project.img}-720.webp 720w, ${project.img}-1200.webp 1200w`;
            heroImg.src = `${project.img}-1200.webp`;
            heroImg.alt = project.alt + ' — a Static Designs project';
            browserUrl.textContent = project.url;
        }

        function fadeTo(index) {
            if (index === currentIndex) return;
            heroImg.classList.add('fade-out');
            setTimeout(() => {
                setDesktopProject(index);
                heroImg.classList.remove('fade-out');
                markActive(index);
            }, 300);
        }

        // Phones: slide the strip; the observer below marks the bar once that screenshot fills the screen
        function slideTo(index) {
            loadPhoneSlides();
            heroSlides.scrollTo({ left: index * heroSlides.clientWidth, behavior: reduceMotion.matches ? 'auto' : 'smooth' });
        }

        function show(index) {
            if (phoneLayout.matches) slideTo(index);
            else fadeTo(index);
        }

        function scheduleNext() {
            clearTimeout(rotationTimer);
            rotationTimer = setTimeout(() => {
                show((currentIndex + 1) % showcaseProjects.length);
                scheduleNext();
            }, ROTATE_MS);
        }

        // On phones, whichever screenshot fills most of the screen is the current one, however it got there:
        // a swipe, a tap on a bar, or the timer. On desktop only the first slide is displayed, so this stays quiet.
        const slideObserver = new IntersectionObserver(entries => {
            if (!phoneLayout.matches) return;
            entries.forEach(entry => {
                if (entry.isIntersecting) markActive(slides.indexOf(entry.target));
            });
        }, { root: heroSlides, threshold: 0.6 });
        slides.forEach(slide => slideObserver.observe(slide));

        // A finger on the strip pauses the rotation; it picks up again 5 seconds after the finger lifts
        heroSlides.addEventListener('touchstart', () => clearTimeout(rotationTimer), { passive: true });
        heroSlides.addEventListener('touchend', scheduleNext, { passive: true });
        heroSlides.addEventListener('touchcancel', scheduleNext, { passive: true });

        indicators.forEach(bar => {
            bar.addEventListener('click', () => {
                show(parseInt(bar.dataset.index, 10));
                scheduleNext();
            });
        });

        // The strip only scrolls on phones, so only there can it take keyboard focus (arrow keys then flip pages)
        function applyLayout() {
            if (phoneLayout.matches) heroSlides.tabIndex = 0;
            else heroSlides.removeAttribute('tabindex');
        }

        // Rotating a tablet or resizing a window across 768px starts over at the first project
        phoneLayout.addEventListener('change', () => {
            if (phoneLayout.matches) loadPhoneSlides();
            heroImg.classList.remove('fade-out');
            setDesktopProject(0);
            heroSlides.scrollLeft = 0;
            markActive(0);
            applyLayout();
            scheduleNext();
        });

        // Phones: the other two screenshots download at the first scroll or touch, or 4 seconds after the page loads
        // (before the first slide at 5), so they never compete with the first screenshot, which is what the page's
        // speed score waits on. Sliding to one also fetches them, in case that comes first.
        function loadPhoneSlides() {
            slides.forEach(slide => {
                if (slide.dataset.slideSrc) {
                    slide.src = slide.dataset.slideSrc;
                    delete slide.dataset.slideSrc;
                }
            });
        }
        function loadPhoneSlidesOnPhones() {
            if (phoneLayout.matches) loadPhoneSlides();
        }
        heroSlides.addEventListener('touchstart', loadPhoneSlides, { passive: true });
        window.addEventListener('scroll', loadPhoneSlidesOnPhones, { passive: true, once: true });
        const loadAfterPageLoad = () => setTimeout(loadPhoneSlidesOnPhones, 4000);
        if (document.readyState === 'complete') loadAfterPageLoad();
        else window.addEventListener('load', loadAfterPageLoad);

        applyLayout();
        scheduleNext();
    }

    // ============================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ============================================
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Ignore empty anchors
            if (href === '#') {
                e.preventDefault();
                return;
            }

            const target = document.querySelector(href);

            if (target) {
                e.preventDefault();

                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = target.offsetTop - navbarHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ============================================
    // NAVBAR SCROLL EFFECT
    // ============================================
    // At the very top of a page the navbar floats as a rounded bar. Once the page leaves the top it gets
    // "is-docked" and stretches edge to edge against the top; on phones it also slims down (see .navbar in
    // style.css). Watching a tiny marker at the top of the page avoids running code on every scroll event.
    const navbar = document.getElementById('navbar');

    if (navbar && 'IntersectionObserver' in window) {
        const topMarker = document.createElement('div');
        topMarker.setAttribute('aria-hidden', 'true');
        topMarker.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:16px;pointer-events:none';
        document.body.prepend(topMarker);

        let firstCheck = true;
        new IntersectionObserver(function(entries) {
            const docked = !entries[0].isIntersecting;

            // A page that opens already scrolled (say, a reload partway down) starts docked instead of
            // animating into place: transitions stay off until two frames have drawn
            if (firstCheck && docked) {
                navbar.classList.add('no-transition');
                requestAnimationFrame(function() {
                    requestAnimationFrame(function() {
                        navbar.classList.remove('no-transition');
                    });
                });
            }
            firstCheck = false;

            navbar.classList.toggle('is-docked', docked);
        }).observe(topMarker);
    }

    // ============================================
    // SPOTLIGHT GRADIENT EFFECT
    // ============================================
    const spotlightElements = document.querySelectorAll('.cta-section, .service-card.featured, .pricing-card.featured');

    if (window.matchMedia('(hover: hover)').matches) {
        spotlightElements.forEach(el => {
            el.addEventListener('mousemove', function(e) {
                const rect = this.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                this.style.setProperty('--gradient-x', x + '%');
                this.style.setProperty('--gradient-y', y + '%');
            });

            el.addEventListener('mouseleave', function() {
                this.style.setProperty('--gradient-x', '50%');
                this.style.setProperty('--gradient-y', '50%');
            });
        });
    }

    // ============================================
    // FLASH MESSAGES AUTO-DISMISS
    // ============================================
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(message => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Add slideOut animation to CSS dynamically
    if (flashMessages.length > 0) {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // ============================================
    // FORM VALIDATION ENHANCEMENT
    // ============================================
    const contactForm = document.getElementById('contactForm');

    if (contactForm) {
        const emailInput = document.getElementById('email');

        // Real-time email validation
        if (emailInput) {
            emailInput.addEventListener('blur', function() {
                const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

                if (this.value && !emailPattern.test(this.value)) {
                    this.style.borderColor = '#ef4444';
                } else {
                    this.style.borderColor = '';
                }
            });

            emailInput.addEventListener('input', function() {
                this.style.borderColor = '';
            });
        }

        // Add loading state to submit button
        contactForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Sending...';
                submitBtn.disabled = true;
            }
        });
    }

    // ============================================
    // INTERSECTION OBSERVER FOR ANIMATIONS
    // ============================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements that should animate in
    const animateElements = document.querySelectorAll('.service-card, .testimonial-card, .portfolio-item, .value-card, .pricing-card, .addon-card, .advantage-item');

    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // ============================================
    // LAZY LOADING IMAGES
    // ============================================
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // ============================================
    // BACK TO TOP BUTTON (if needed in future)
    // ============================================
    function createBackToTopButton() {
        const button = document.createElement('button');
        button.textContent = '↑';
        button.className = 'back-to-top';
        button.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #d946ef 0%, #c084fc 100%);
            color: white;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.3s, transform 0.3s;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        `;

        button.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 500) {
                button.style.opacity = '1';
                button.style.transform = 'scale(1)';
            } else {
                button.style.opacity = '0';
                button.style.transform = 'scale(0.8)';
            }
        });

        document.body.appendChild(button);
    }

    // Uncomment to enable back to top button
    // createBackToTopButton();

    // ============================================
    // LOG INITIALIZATION
    // ============================================
    console.log('Static Designs - Website initialized successfully');
});