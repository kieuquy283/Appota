import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  const backendUrl = process.env.PYTHON_API_URL || process.env.BACKEND_URL || 'http://127.0.0.1:8000';
  const internalSecret = process.env.INTERNAL_API_SECRET;

  try {
    const body = await request.json().catch(() => null);
    if (!body || typeof body !== 'object') {
      return NextResponse.json(
        { error: 'Yêu cầu không hợp lệ. Dữ liệu JSON phải được cung cấp.' },
        { status: 400 }
      );
    }

    const { user_id, question } = body;

    if (!user_id || typeof user_id !== 'string') {
      return NextResponse.json(
        { error: 'Thiếu hoặc sai định dạng user_id.' },
        { status: 400 }
      );
    }

    if (!question || typeof question !== 'string' || !question.trim()) {
      return NextResponse.json(
        { error: 'Câu hỏi không được để trống.' },
        { status: 400 }
      );
    }

    if (question.length > 2000) {
      return NextResponse.json(
        { error: 'Câu hỏi vượt quá giới hạn 2000 ký tự.' },
        { status: 400 }
      );
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (internalSecret) {
      headers['x-internal-key'] = internalSecret;
    }

    const res = await fetch(`${backendUrl}/answer`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        user_id,
        question: question.trim(),
      }),
      cache: 'no-store',
    });

    if (!res.ok) {
      if (res.status === 404) {
        return NextResponse.json(
          { error: 'Người dùng không tồn tại hoặc đã ngừng kích hoạt.' },
          { status: 404 }
        );
      }
      return NextResponse.json(
        {
          status: 'ERROR',
          answer: 'Hiện chưa thể trả lời câu hỏi này. Vui lòng thử lại sau.',
          reason: 'service_error',
          citations: [],
        },
        { status: res.status }
      );
    }

    const data = await res.json();

    // Sanitize response to guarantee no internal leaks to browser
    return NextResponse.json({
      status: data.status || 'ANSWER',
      answer: data.answer || '',
      reason: data.reason || null,
      citations: Array.isArray(data.citations)
        ? data.citations.map((c: any) => ({
            title: c.title || '',
            section: c.section || null,
            excerpt: c.excerpt || null,
          }))
        : [],
    });
  } catch (error) {
    console.error('Error in /api/answer:', error);
    return NextResponse.json(
      {
        status: 'ERROR',
        answer: 'Không thể kết nối đến máy chủ xử lý. Vui lòng thử lại sau.',
        reason: 'network_error',
        citations: [],
      },
      { status: 502 }
    );
  }
}
