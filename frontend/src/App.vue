<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style>
/* Modern, vibrant root variables */
:root {
  --primary-color: #4F46E5;
  --primary-hover: #4338CA;
  --secondary-color: #10B981;
  --bg-color: #F3F4F6;
  --card-bg: #FFFFFF;
  --text-main: #111827;
  --text-muted: #6B7280;
  --danger-color: #EF4444;
}

body {
  margin: 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-main);
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: var(--card-bg);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--primary-color);
  font-weight: 800;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-btn {
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.2s;
}

.nav-btn:hover {
  background-color: var(--primary-hover);
}

.logout-btn {
  background-color: transparent;
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background-color: var(--danger-color);
  color: white;
}

.main-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Card classes widely used in the views */
.glass-card {
  background: var(--card-bg);
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  animation: slideUp 0.4s ease-out;
}

.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-main);
  font-size: 0.9rem;
}

.form-group input, .form-group select {
  padding: 0.75rem 1rem;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.form-group input:focus, .form-group select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.btn-primary {
  width: 100%;
  background-color: var(--primary-color);
  color: white;
  padding: 0.8rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:active {
  transform: translateY(2px);
}

.link-text {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}
.link-text:hover {
  text-decoration: underline;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
