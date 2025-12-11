import { NextRequest, NextResponse } from 'next/server';

const SCHEDULEAI_API_URL = process.env.SCHEDULEAI_API_URL ||
                          process.env.NEXT_PUBLIC_SCHEDULEAI_URL ||
                          'http://localhost:8000';

export async function GET() {
  try {
    console.log(`🔍 Fetching services from backend: ${SCHEDULEAI_API_URL}/services`);

    const response = await fetch(`${SCHEDULEAI_API_URL}/services`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SCHEDULEAI_API_KEY || ''}`,
      },
    });

    if (!response.ok) {
      console.error(`❌ Backend error: ${response.status}`);
      return NextResponse.json(
        { error: 'Failed to fetch services' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ Services fetched successfully:', data);

    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Fetch services error:', error);
    // Return fallback services if backend is unavailable
    return NextResponse.json({
      services: [
        { id: 'consulenza', name: 'Consulenza', duration: 60 },
        { id: 'consulenza_fiscale', name: 'Consulenza Fiscale', duration: 90 },
        { id: 'consulenza_legale', name: 'Consulenza Legale', duration: 90 },
        { id: 'appunto', name: 'Appunto', duration: 30 },
        { id: 'riunione', name: 'Riunione', duration: 60 },
        { id: 'incontro', name: 'Incontro', duration: 45 },
        { id: 'visita', name: 'Visita', duration: 60 },
      ]
    });
  }
}