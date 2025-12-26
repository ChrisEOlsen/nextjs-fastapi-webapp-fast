// src/router/index.js
import { HomePage } from '../pages/HomePage.js';
import { AboutPage } from '../pages/AboutPage.js';

const routes = {
    '/': HomePage,
    '/about': AboutPage,
};

const appContainer = document.getElementById('app');

export const router = () => {
    const path = window.location.pathname;
    const page = routes[path] || HomePage; // Default to HomePage if route not found
    appContainer.innerHTML = page();
};

// --- Handle navigation ---
// Listen for clicks on links with the 'nav-link' class
document.addEventListener('click', (e) => {
    const target = e.target.closest('.nav-link');
    if (target) {
        e.preventDefault();
        const href = target.getAttribute('href');
        history.pushState(null, null, href);
        router(); // Re-render the page
    }
});

// --- Handle browser back/forward buttons ---
window.addEventListener('popstate', router);
