import { NextRequest, NextResponse } from 'next/server';

const SCHEDULEAI_API_URL = process.env.SCHEDULEAI_API_URL ||
                          process.env.NEXT_PUBLIC_SCHEDULEAI_URL ||
                          'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const date = searchParams.get('date');
    const service = searchParams.get('service');
    const consultant = searchParams.get('consultant');

    if (!date) {
      return NextResponse.json(
        { error: 'Date parameter is required' },
        { status: 400 }
      );
    }

    console.log(`🔍 Checking availability for ${date} (service: ${service}, consultant: ${consultant})`);

    // Build query parameters
    const queryParams = new URLSearchParams({ date });
    if (service) queryParams.append('service', service);
    if (consultant) queryParams.append('consultant', consultant);

    const response = await fetch(`${SCHEDULEAI_API_URL}/availability?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SCHEDULEAI_API_KEY || ''}`,
      },
    });

    if (!response.ok) {
      console.error(`❌ Backend error: ${response.status}`);
      return NextResponse.json(
        { error: 'Failed to check availability' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ Availability checked successfully:', data);

    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Check availability error:', error);
    // Return fallback availability if backend is unavailable
    return NextResponse.json({
      date: request.nextUrl.searchParams.get('date'),
      available_slots: [
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30'
      ],
      timestamp: new Date().toISOString()
    });
  }
}