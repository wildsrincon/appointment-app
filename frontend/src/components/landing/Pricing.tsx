'use client';

import { Button } from '@/components/ui/button';
import { Check, Zap } from 'lucide-react';
import Link from 'next/link';

export function Pricing() {
  const plans = [
    {
      name: 'Starter',
      description: 'Perfetto per iniziare',
      price: '0€',
      period: 'per sempre',
      features: [
        '100 prenotazioni/mese',
        '1 calendario',
        'Chat AI in italiano',
        'Notifiche email',
        'Analytics base',
        'Supporto email'
      ],
      cta: 'Inizia Gratis',
      highlighted: false,
      link: '/app'
    },
    {
      name: 'Professional',
      description: 'Per studi in crescita',
      price: '29€',
      period: 'al mese',
      features: [
        'Prenotazioni illimitate',
        '3 calendari',
        'AI multilingua (IT, EN, ES)',
        'Notifiche email & SMS',
        'Analytics avanzato',
        'Integrazione Google Calendar',
        'Personalizzazione brand',
        'Supporto prioritario'
      ],
      cta: 'Inizia Ora',
      highlighted: true,
      link: '/app'
    },
    {
      name: 'Enterprise',
      description: 'Per grandi organizzazioni',
      price: '99€',
      period: 'al mese',
      features: [
        'Tutto illimitato',
        'Calendari illimitati',
        'AI personalizzata',
        'API access',
        'SSO & Sicurezza avanzata',
        'Dedicated account manager',
        'SLA garantito',
        'Training on-site'
      ],
      cta: 'Contattaci',
      highlighted: false,
      link: 'mailto:info@scheduleai.it'
    }
  ];

  return (
    <section id="pricing" className="py-24 bg-gradient-to-br from-gray-50 to-blue-50 scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-600 text-white mb-4">
            <Zap className="w-4 h-4" />
            <span className="text-sm font-semibold">Prezzi Trasparenti</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Scegli il piano perfetto per
            <span className="text-blue-600"> il tuo business</span>
          </h2>
          <p className="text-xl text-gray-600">
            Nessun costo nascosto. Cancella in qualsiasi momento.
            Inizia gratuitamente, crescendo quando sei pronto.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative rounded-3xl p-8 transition-all duration-300 ${
                plan.highlighted
                  ? 'bg-white shadow-2xl shadow-blue-900/10 scale-105 border-2 border-blue-600'
                  : 'bg-white shadow-lg hover:shadow-xl border border-gray-100'
              }`}
            >
              {/* Popular Badge */}
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Più Popolare
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  {plan.description}
                </p>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-5xl font-bold text-gray-900">
                    {plan.price}
                  </span>
                  <span className="text-gray-600">{plan.period}</span>
                </div>
              </div>

              {/* Features List */}
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center mt-0.5">
                      <Check className="w-3 h-3 text-green-600" />
                    </div>
                    <span className="text-gray-700 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <Link href={plan.link}>
                <Button
                  className={`w-full py-6 text-lg rounded-xl transition-all duration-300 ${
                    plan.highlighted
                      ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/30'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                  }`}
                >
                  {plan.cta}
                </Button>
              </Link>

              {/* Trust Badge */}
              <p className="text-center text-xs text-gray-500 mt-4">
                Nessuna carta di credito richiesta
              </p>
            </div>
          ))}
        </div>

        {/* Money Back Guarantee */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-white rounded-full shadow-lg">
            <div className="flex items-center gap-2">
              {[...Array(5)].map((_, i) => (
                <svg
                  key={i}
                  className="w-5 h-5 text-yellow-400 fill-current"
                  viewBox="0 0 20 20"
                >
                  <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                </svg>
              ))}
            </div>
            <span className="text-sm font-medium text-gray-700">
              30 giorni di garanzia soddisfatti o rimborsati
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
