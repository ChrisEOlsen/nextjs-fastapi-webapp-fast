// src/pages/HomePage.js
import { fetchUsers } from '../services/api/users.js';

export const HomePage = () => {
    // Add event listener after the component is rendered
    setTimeout(() => {
        const fetchBtn = document.getElementById('fetch-users-btn');
        const usersList = document.getElementById('users-list');
        if (fetchBtn) {
            fetchBtn.addEventListener('click', async () => {
                usersList.textContent = 'Loading...';
                const users = await fetchUsers();
                usersList.textContent = JSON.stringify(users, null, 2);
            });
        }
    }, 0);

    return `
        <div class="p-8 text-center">
            <h1 class="text-4xl font-bold mb-4">Welcome to the Home Page</h1>
            <p class="text-lg text-gray-400 mb-6">This content is rendered dynamically by the vanilla JS router!</p>
            <button id="fetch-users-btn" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Fetch Users from Backend
            </button>
            <div class="mt-4 text-left">
                <h2 class="text-2xl font-bold mb-2">Users:</h2>
                <pre id="users-list" class="bg-gray-800 p-4 rounded"></pre>
            </div>
        </div>
    `;
};