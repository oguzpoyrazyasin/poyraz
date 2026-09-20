import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    ok: true,
    service: "poyraz-kids-web",
    timestamp: new Date().toISOString()
  });
}
