'use client';

import { Quote } from 'lucide-react';

export function Testimonials() {
  const testimonials = [
    {
      name: 'Dr. Maria Rossi',
      role: 'Commercialista, Milano',
      content: 'ScheduleAI ha rivoluzionato il mio studio. Prima perdevo il 30% delle chiamate, ora ogni cliente viene gestito perfettamente. Risparmio 10 ore a settimana!',
      rating: 5,
      image: '👩‍💼'
    },
    {
      name: 'Avv. Luca Bianchi',
      role: 'Studio Legale Bianchi, Roma',
      content: 'L\'AI comprende perfettamente le esigenze dei clienti e propone automaticamente gli orari disponibili. Un\'assistente virtuale che non dorme mai.',
      rating: 5,
      image: '👨‍💼'
    },
    {
      name: 'Dott.ssa Giulia Ferrari',
      role: 'Psicologa, Torino',
      content: 'I miei clienti apprezzano poter prenotare quando vogliono, anche alle 2 di notte. Ho aumentato le prenotazioni del 40% nel primo mese.',
      rating: 5,
      image: '👩‍⚕️'
    }
  ];

  return (
    <section className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 border border-blue-100 mb-4">
            <Quote className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-semibold text-blue-900">Testimonianze</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Amato dai
            <span className="text-blue-600"> professionisti italiani</span>
          </h2>
          <p className="text-xl text-gray-600">
            Scopri perché centinaia di studi professionali hanno scelto ScheduleAI
            per gestire le loro prenotazioni.
          </p>
        </div>

        {/* Testimonials Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="group relative p-8 bg-gradient-to-br from-white to-gray-50 rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-xl transition-all duration-300"
            >
              {/* Quote Icon */}
              <div className="absolute top-6 right-6 text-blue-100">
                <Quote className="w-12 h-12" />
              </div>

              {/* Rating */}
              <div className="flex items-center gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <svg
                    key={i}
                    className="w-5 h-5 text-yellow-400 fill-current"
                    viewBox="0 0 20 20"
                  >
                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                  </svg>
                ))}
              </div>

              {/* Content */}
              <p className="text-gray-700 leading-relaxed mb-6">
                "{testimonial.content}"
              </p>

              {/* Author */}
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center text-2xl">
                  {testimonial.image}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">
                    {testimonial.name}
                  </h4>
                  <p className="text-sm text-gray-600">{testimonial.role}</p>
                </div>
              </div>

              {/* Hover Effect */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-50/0 to-purple-50/0 group-hover:from-blue-50/50 group-hover:to-purple-50/50 transition-all duration-300 -z-10" />
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { value: '500+', label: 'Professionisti' },
            { value: '50k+', label: 'Prenotazioni/Mese' },
            { value: '99.9%', label: 'Uptime' },
            { value: '4.9/5', label: 'Rating Medio' }
          ].map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">
                {stat.value}
              </div>
              <div className="text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
