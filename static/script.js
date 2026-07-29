document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const recordingIndicator = document.getElementById('recording-indicator');

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if(this.value.trim() === '') {
            this.style.height = 'auto';
        }
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        sendMessage();
    });

    function appendMessage(sender, text, isHtml=false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isHtml) {
            contentDiv.innerHTML = text;
        } else {
            contentDiv.textContent = text;
        }
        
        msgDiv.appendChild(contentDiv);
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage(transcribedText = null) {
        const text = (typeof transcribedText === 'string') ? transcribedText : userInput.value.trim();
        if (!text) return;

        if (typeof transcribedText !== 'string') {
            userInput.value = '';
            userInput.style.height = 'auto';
        }

        appendMessage('user', text);

        // Add loading indicator
        const loadingId = 'loading-' + Date.now();
        const loadingHtml = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
        const loadingMsg = appendMessage('system', loadingHtml, true);
        loadingMsg.id = loadingId;

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: text })
            });

            const data = await response.json();
            
            // Remove loading
            document.getElementById(loadingId).remove();

            if (response.ok) {
                appendMessage('system', data.answer);
            } else {
                const errorMsg = data.error || data.detail || "अज्ञात त्रुटि (Unknown error)";
                appendMessage('system', `त्रुटि (Error): ${errorMsg}`);
            }
        } catch (error) {
            document.getElementById(loadingId).remove();
            appendMessage('system', "सर्वर से संपर्क करने में त्रुटि हुई। (Error connecting to server.)");
        }
    }

    // Voice Recording Logic
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    micBtn.addEventListener('click', async () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener("stop", async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendAudioToServer(audioBlob);
            });

            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('recording');
            recordingIndicator.classList.remove('hidden');
        } catch (err) {
            alert("माइक एक्सेस करने में समस्या हुई। (Error accessing microphone.)");
            console.error(err);
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            micBtn.classList.remove('recording');
            recordingIndicator.classList.add('hidden');
        }
    }

    async function sendAudioToServer(audioBlob) {
        // Add loading indicator for transcription
        const loadingHtml = `<div class="typing-indicator"><span></span><span></span><span></span></div> <span style="font-size: 0.85em; opacity: 0.8; margin-left: 10px;">आवाज़ समझ रहा हूँ... (Transcribing...)</span>`;
        const loadingMsg = appendMessage('system', loadingHtml, true);

        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');

        try {
            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            loadingMsg.remove();

            if (response.ok && data.transcription) {
                // Automatically send the transcribed text
                sendMessage(data.transcription);
            } else if (response.ok && !data.transcription) {
                 appendMessage('system', "मैं आपकी आवाज़ नहीं सुन सका। कृपया दोबारा बोलें। (Could not hear you. Please speak again.)");
            } else {
                appendMessage('system', `त्रुटि (Error): ${data.error}`);
            }
        } catch (error) {
            loadingMsg.remove();
            appendMessage('system', "सर्वर से संपर्क करने में त्रुटि हुई। (Error connecting to server.)");
        }
    }
});
