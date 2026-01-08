'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, Calendar, CheckCircle2, Sparkles } from 'lucide-react';
import Link from 'next/link';

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-linear-to-br from-white via-blue-50 to-white">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-blue-50/[0.4] mask-[linear-gradient(0deg,white,rgba(255,255,255,0.6))]" />
      <div className="absolute inset-0 bg-linear-to-br from-blue-50/50 via-transparent to-transparent" />

      {/* Animated Gradient Orbs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl animate-pulse delay-1000" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 border border-blue-100 mb-8 animate-fade-in">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">AI-Powered Scheduling Platform</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6 animate-fade-in-up">
            <span className="block text-gray-900">Prenotazioni</span>
            <span className="block text-blue-600 mt-2">Intelligenti & Automatiche</span>
          </h1>

          {/* Subheadline */}
          <p className="mt-6 text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed animate-fade-in-up delay-200">
            L&apos;assistente AI che gestisce i tuoi appuntamenti 24/7. Più tempo per te,
            <span className="text-blue-600 font-semibold"> zero perdite di clienti</span>.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in-up delay-400">
            <Link href="/app">
              <Button
                size="lg"
                className="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg shadow-xl shadow-blue-600/20 hover:shadow-2xl hover:shadow-blue-600/30 transition-all duration-300 rounded-full"
              >
                Inizia Gratis Ora
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Button
              size="lg"
              variant="outline"
              className="px-8 py-6 text-lg border-2 border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-300 rounded-full"
            >
              Guarda Demo
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 flex flex-wrap justify-center items-center gap-8 animate-fade-in delay-600">
            {[
              { icon: CheckCircle2, text: 'Nessuna carta richiesta' },
              { icon: Calendar, text: 'Configurazione in 2 minuti' },
              { icon: Sparkles, text: 'AI multilingua' }
            ].map((item, index) => (
              <div key={index} className="flex items-center gap-2 text-gray-600">
                <item.icon className="w-5 h-5 text-blue-600 flex-shrink-0" />
                <span className="text-sm font-medium">{item.text}</span>
              </div>
            ))}
          </div>

          {/* Social Proof */}
          <div className="mt-16 animate-fade-in delay-800">
            <p className="text-sm text-gray-500 mb-4">Più di 500+ professionisti usano ScheduleAI</p>
            <div className="flex justify-center items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex">
                  {[...Array(5)].map((_, j) => (
                    <svg
                      key={`${i}-${j}`}
                      className="w-5 h-5 text-yellow-400 fill-current"
                      viewBox="0 0 20 20"
                    >
                      <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                    </svg>
                  ))}
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-600 mt-2">
              <span className="font-semibold text-blue-600">4.9/5</span> basato su 200+ recensioni
            </p>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-gray-300 rounded-full flex items-start justify-center p-2">
          <div className="w-1.5 h-3 bg-gray-400 rounded-full animate-pulse" />
        </div>
      </div>
    </section>
  );
}
