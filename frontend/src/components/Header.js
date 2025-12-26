// src/components/Header.js

export const Header = () => {
    return `
        <header class="bg-gray-800 p-4 text-white">
            <nav class="container mx-auto flex justify-between">
                <a href="/" class="nav-link font-bold text-lg">MyApp</a>
                <div class="space-x-4">
                    <a href="/" class="nav-link hover:text-gray-300">Home</a>
                    <a href="/about" class="nav-link hover:text-gray-300">About</a>
                </div>
            </nav>
        </header>
    `;
};
