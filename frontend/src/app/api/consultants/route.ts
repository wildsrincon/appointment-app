import { NextRequest, NextResponse } from 'next/server';

const SCHEDULEAI_API_URL = process.env.SCHEDULEAI_API_URL ||
                          process.env.NEXT_PUBLIC_SCHEDULEAI_URL ||
                          'http://localhost:8000';

export async function GET() {
  try {
    console.log(`🔍 Fetching consultants from backend`);

    // Note: This endpoint might not exist in the backend yet
    // so we'll provide fallback data
    const response = await fetch(`${SCHEDULEAI_API_URL}/consultants`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SCHEDULEAI_API_KEY || ''}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    } else {
      // Return fallback consultants if endpoint doesn't exist
      return NextResponse.json({
        consultants: [
          { id: 'dr_rossi', name: 'Dr. Rossi', services: ['consulenza', 'consulenza_fiscale'] },
          { id: 'dr_bianchi', name: 'Dr. Bianchi', services: ['consulenza_legale', 'appunto'] },
          { id: 'dr_verdi', name: 'Dr. Verdi', services: ['consulenza', 'riunione'] },
        ]
      });
    }

  } catch (error) {
    console.error('❌ Fetch consultants error:', error);
    // Return fallback consultants if backend is unavailable
    return NextResponse.json({
      consultants: [
        { id: 'dr_rossi', name: 'Dr. Rossi', services: ['consulenza', 'consulenza_fiscale'] },
        { id: 'dr_bianchi', name: 'Dr. Bianchi', services: ['consulenza_legale', 'appunto'] },
        { id: 'dr_verdi', name: 'Dr. Verdi', services: ['consulenza', 'riunione'] },
      ]
    });
  }
}