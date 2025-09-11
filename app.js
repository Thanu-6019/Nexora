// Smooth scrolling for internal links
document.querySelectorAll('nav a[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e){
        e.preventDefault();
        document.querySelectorAll('nav a').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        const targetId = this.getAttribute('href').substring(1);
        const target = document.getElementById(targetId);
        if(target){
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Scroll-to-Top Button
const scrollBtn = document.getElementById('scrollTopBtn');
window.addEventListener('scroll', () => {
    scrollBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
});
scrollBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Hero Buttons click animation is handled with btn-scale class

