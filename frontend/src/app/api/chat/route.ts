import { NextRequest, NextResponse } from "next/server";

const SCHEDULEAI_API_URL =
  process.env.SCHEDULEAI_API_URL ||
  process.env.NEXT_PUBLIC_SCHEDULEAI_URL ||
  "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const { message, sessionId, businessId, consultantId } =
      await request.json();

    if (!message) {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 }
      );
    }

    // Call the ScheduleAI backend
    const response = await fetch(`${SCHEDULEAI_API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.SCHEDULEAI_API_KEY || ""}`,
      },
      body: JSON.stringify({
        message,
        session_id: sessionId || "default",
        business_id: businessId,
        consultant_id: consultantId,
        stream: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`ScheduleAI API error: ${response.status}`);
    }

    // Handle streaming response
    if (response.body) {
      const reader = response.body.getReader();
      const encoder = new TextEncoder();

      const stream = new ReadableStream({
        async start(controller) {
          try {
            while (true) {
              const { done, value } = await reader.read();

              if (done) break;

              // Forward the chunk to the client
              controller.enqueue(value);
            }
          } catch (error) {
            controller.error(error);
          } finally {
            controller.close();
          }
        },
      });

      return new Response(stream, {
        headers: {
          "Content-Type": "text/plain; charset=utf-8",
          "Transfer-Encoding": "chunked",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    // Fallback for non-streaming responses
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: "ScheduleAI Chat API is running",
    version: "1.0.0",
  });
}
