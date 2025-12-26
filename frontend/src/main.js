// src/main.js
import { router } from './router/index.js';
import { Header } from './components/Header.js';

const headerContainer = document.getElementById('header-container');
headerContainer.innerHTML = Header();

// Initial page load
document.addEventListener('DOMContentLoaded', () => {
    router();
});