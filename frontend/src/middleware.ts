import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

// Define qué rutas son públicas (no requieren autenticación)
const isPublicRoute = createRouteMatcher([
  '/landing(.*)',
  '/api/webhook(.*)',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/',
  '/api(.*)',
  '/_next(.*)',
  '/favicon.ico',
  '/static(.*)'
]);

export default clerkMiddleware((auth, request) => {
  // Para rutas NO públicas, verificar autenticación manualmente
  if (!isPublicRoute(request)) {
    // Verificar si el usuario está autenticado
    if (!auth().userId) {
      // Si no está autenticado, Clerk redirigirá automáticamente
      // No necesitamos llamar a protect(), clerkMiddleware lo maneja
    }
  }
});
