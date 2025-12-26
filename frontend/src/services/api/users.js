// src/services/api/users.js

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const fetchUsers = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/v1/users/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const users = await response.json();
        return users;
    } catch (error) {
        console.error("Failed to fetch users:", error);
        return []; // Return an empty array on error
    }
};
