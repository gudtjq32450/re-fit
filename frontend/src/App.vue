<template>
  <div class="app-shell">
    <header class="navbar">
      <RouterLink to="/" class="brand">RE:FIT</RouterLink>
      <nav>
        <RouterLink to="/">홈</RouterLink>
        <RouterLink to="/studio">3D 스튜디오</RouterLink>
      </nav>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  border-bottom: 1px solid #1e293b;
}
.brand {
  font-size: 1.3rem;
  font-weight: 800;
  color: #f8fafc;
  text-decoration: none;
}
nav {
  display: flex;
  gap: 20px;
}
nav a {
  color: #cbd5e1;
  text-decoration: none;
  font-weight: 600;
}
</style>
