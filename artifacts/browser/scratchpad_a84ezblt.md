# Next.js App UI Verification Checklist

- [x] Step 1: Navigate to http://localhost:3000 and inspect initial page load (sidebar, user selector U01, user profile card, preset questions, welcome screen)
- [x] Step 2: Click preset button 'Tôi có bao nhiêu ngày nghỉ phép?' and send
- [x] Step 3: Wait for assistant response, verify status badge, answer text (15 ngày), and citation cards
- [x] Step 4: Submit second question 'Tôi được làm việc tại nhà mấy ngày?', verify multi-turn chat and distinct citation cards
- [x] Step 5: Select user U03 from sidebar dropdown, verify conversation history reset
- [x] Step 6: Submit 'Tôi có bao nhiêu ngày nghỉ phép?' for U03, verify answer (12 ngày) and different citation
- [x] Step 7: Click '➕ Cuộc trò chuyện mới', verify conversation clears back to welcome state
- [x] Step 8: Complete task and report final results
