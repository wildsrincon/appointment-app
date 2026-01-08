'use client';

import { Button } from '@/components/ui/button';
import { Calendar, Menu, X, SignIn, User } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';

export function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setIsMobileMenuOpen(false);
    }
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-gray-100'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <span className={`text-xl font-bold transition-colors ${
              isScrolled ? 'text-gray-900' : 'text-gray-900'
            }`}>
              ScheduleAI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <button
              onClick={() => scrollToSection('features')}
              className={`font-medium transition-colors hover:text-blue-600 ${
                isScrolled ? 'text-gray-700' : 'text-gray-700'
              }`}
            >
              Funzionalità
            </button>
            <button
              onClick={() => scrollToSection('pricing')}
              className={`font-medium transition-colors hover:text-blue-600 ${
                isScrolled ? 'text-gray-700' : 'text-gray-700'
              }`}
            >
              Prezzi
            </button>
            <button
              onClick={() => scrollToSection('faq')}
              className={`font-medium transition-colors hover:text-blue-600 ${
                isScrolled ? 'text-gray-700' : 'text-gray-700'
              }`}
            >
              FAQ
            </button>
          </div>

          {/* Auth Buttons - Desktop */}
          <div className="hidden md:flex items-center gap-4">
            <SignedOut>
              <SignInButton mode="modal">
                <Button
                  variant="outline"
                  className={`border-2 hover:bg-blue-50 hover:border-blue-300 transition-all ${
                    isScrolled
                      ? 'border-gray-200 text-gray-900'
                      : 'border-gray-200 text-gray-900'
                  }`}
                >
                  Accedi
                </Button>
              </SignInButton>
              <SignUpButton mode="modal">
                <Button className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20 hover:shadow-xl hover:shadow-blue-600/30 transition-all">
                  Inizia Gratis
                </Button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link href="/app">
                <Button className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20 hover:shadow-xl hover:shadow-blue-600/30 transition-all">
                  Vai all'App
                </Button>
              </Link>
              <div className="ml-2">
                <UserButton afterSignOutUrl="/landing" />
              </div>
            </SignedIn>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            <div className="flex flex-col gap-4">
              <button
                onClick={() => scrollToSection('features')}
                className="text-left px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors font-medium"
              >
                Funzionalità
              </button>
              <button
                onClick={() => scrollToSection('pricing')}
                className="text-left px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors font-medium"
              >
                Prezzi
              </button>
              <button
                onClick={() => scrollToSection('faq')}
                className="text-left px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors font-medium"
              >
                FAQ
              </button>

              {/* Auth Buttons - Mobile */}
              <div className="flex flex-col gap-2 pt-4 border-t border-gray-100">
                <SignedOut>
                  <SignInButton mode="modal">
                    <Button
                      variant="outline"
                      className="w-full border-2 border-gray-200"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Accedi
                    </Button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <Button
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      Inizia Gratis
                    </Button>
                  </SignUpButton>
                </SignedOut>
                <SignedIn>
                  <Link href="/app" onClick={() => setIsMobileMenuOpen(false)}>
                    <Button className="w-full bg-blue-600 hover:bg-blue-700">
                      Vai all'App
                    </Button>
                  </Link>
                  <div className="flex justify-center pt-2">
                    <UserButton afterSignOutUrl="/landing" />
                  </div>
                </SignedIn>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
