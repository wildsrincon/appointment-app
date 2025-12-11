import { NextRequest, NextResponse } from 'next/server';

const SCHEDULEAI_API_URL = process.env.SCHEDULEAI_API_URL ||
                          process.env.NEXT_PUBLIC_SCHEDULEAI_URL ||
                          'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const appointmentData = await request.json();

    // Validate required fields
    if (!appointmentData.client_name || !appointmentData.service_type || !appointmentData.datetime_request) {
      return NextResponse.json(
        { error: 'Client name, service type, and datetime are required' },
        { status: 400 }
      );
    }

    console.log(`📅 Creating appointment via backend: ${SCHEDULEAI_API_URL}/appointments`);
    console.log('📝 Appointment data:', appointmentData);

    // Forward to backend ScheduleAI API
    const response = await fetch(`${SCHEDULEAI_API_URL}/appointments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SCHEDULEAI_API_KEY || ''}`,
      },
      body: JSON.stringify(appointmentData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`❌ Backend error: ${response.status} - ${JSON.stringify(errorData)}`);
      return NextResponse.json(
        { error: errorData.detail || 'Failed to create appointment' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ Appointment created successfully:', data);

    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Appointment creation error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const response = await fetch(`${SCHEDULEAI_API_URL}/appointments`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SCHEDULEAI_API_KEY || ''}`,
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch appointments' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Fetch appointments error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}