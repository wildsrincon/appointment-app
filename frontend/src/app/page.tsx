import { redirect } from 'next/navigation';
import { auth } from '@clerk/nextjs/server';

export default async function HomePage() {
  // Check if user is authenticated using auth() instead of currentUser()
  const { userId } = await auth();

  // If authenticated, redirect to app
  if (userId) {
    redirect('/app');
  }

  // If not authenticated, redirect to landing page
  redirect('/landing');
}
