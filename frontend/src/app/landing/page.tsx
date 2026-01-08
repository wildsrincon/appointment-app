import { FAQ } from '@/components/landing/FAQ';
import { Features } from '@/components/landing/Features';
import { Footer } from '@/components/landing/Footer';
import { HeroInteractive } from '@/components/landing/HeroInteractive';
import { Navbar } from '@/components/landing/Navbar';
import { Pricing } from '@/components/landing/Pricing';
import { Testimonials } from '@/components/landing/Testimonials';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ScheduleAI - Prenotazioni Intelligenti con AI | Gestione Appuntamenti Automatica',
  description: 'ScheduleAI è l\'assistente AI che gestisce le tue prenotazioni 24/7. Perfetto per professionisti e studi italiani. Zero chiamate perse, più tempo per il tuo business. Prova gratis con demo interattiva!',
  keywords: 'prenotazioni online, AI assistant, gestione appuntamenti, calendario automatico, booking AI, scheduleAI, prenotazioni intelligenti, assistente virtuale italiano, demo live',
  authors: [{ name: 'ScheduleAI Team' }],
  openGraph: {
    title: 'ScheduleAI - Prenotazioni Intelligenti con AI | Demo Live',
    description: 'Guarda l\'AI in azione! Gestione prenotazioni 24/7 con demo interattiva. Zero chiamate perse.',
    url: 'https://scheduleai.it',
    siteName: 'ScheduleAI',
    locale: 'it_IT',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ScheduleAI - Demo Live Interattiva',
    description: 'Guarda come l\'AI gestisce prenotazioni in tempo reale. Prova la demo!',
  },
  alternates: {
    canonical: 'https://scheduleai.it',
  },
};

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <HeroInteractive />
      <Features />
      <Testimonials />
      <Pricing />
      <FAQ />
      <Footer />

      {/* Schema.org Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "ScheduleAI",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "offers": {
              "@type": "Offer",
              "price": "0",
              "priceCurrency": "EUR"
            },
            "aggregateRating": {
              "@type": "AggregateRating",
              "ratingValue": "4.9",
              "ratingCount": "200"
            },
            "featureList": "AI-Powered Scheduling, 24/7 Availability, Google Calendar Integration, Multi-language Support, Real-time Notifications, Analytics Dashboard"
          })
        }}
      />
    </main>
  );
}
