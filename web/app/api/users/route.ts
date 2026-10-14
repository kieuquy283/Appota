import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const backendUrl = process.env.PYTHON_API_URL || process.env.BACKEND_URL || 'http://127.0.0.1:8000';
  const internalSecret = process.env.INTERNAL_API_SECRET;

  const headers: Record<string, string> = {
    'Accept': 'application/json',
  };
  if (internalSecret) {
    headers['x-internal-key'] = internalSecret;
  }

  try {
    const res = await fetch(`${backendUrl}/users`, {
      method: 'GET',
      headers,
      cache: 'no-store',
    });

    if (!res.ok) {
      const errorText = await res.text().catch(() => '');
      return NextResponse.json(
        { error: 'Failed to fetch users from backend service', details: errorText },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error contacting Python API for /users:', error);
    return NextResponse.json(
      { error: 'Không thể kết nối đến máy chủ xử lý. Vui lòng kiểm tra dịch vụ backend.' },
      { status: 502 }
    );
  }
}
