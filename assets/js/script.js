var isVoice = 0;
var isVoiceConversation = false; // Track if current conversation was initiated by voice
const DEFAULT_VOICE_NAME = 'Flo-en-US';
const PREFERRED_VOICE_ALIASES = [
    'Flo-en-US',
    'Flo (en-US)',
    'Flo en-US',
    'Flo US',
    'Flo'
];
const VOICE_STORAGE_KEY = 'preferredVoiceName';
const LANG_STORAGE_KEY = 'preferredLangCode';

function stopSpeech() {
    const speechEngine = window.speechSynthesis;
    if (speechEngine.speaking) {
        speechEngine.cancel();
    }
}

// Simple voice response function - reads response in original language
function speakAIResponse(text, detectedLang, alwaysSpeak = false) {
    console.log('🔊 speakAIResponse called');

    // Check if speech synthesis is supported
    if (!('speechSynthesis' in window)) {
        console.error('❌ Speech synthesis not supported');
        return;
    }

    // Only speak if voice conversation is active or always speak is enabled
    const shouldSpeak = isVoiceConversation || alwaysSpeak || localStorage.getItem('alwaysSpeak') === 'true';
    if (!shouldSpeak) {
        console.log('🔇 Not speaking - conditions not met');
        return;
    }

    const synth = window.speechSynthesis;

    // Clean text for speech
    let cleanText = text
        .replace(/<[^>]*>/g, ' ')
        .replace(/\*\*([^*]+)\*\*/g, '$1')
        .replace(/\*([^*]+)\*/g, '$1')
        .replace(/\s+/g, ' ')
        .trim();

    if (!cleanText) {
        console.warn('⚠️ No text to speak');
        return;
    }

    // Stop any current speech
    synth.cancel();

    // Get voices and find appropriate one for detected language
    const voices = synth.getVoices();
    console.log('🎤 Available voices:', voices.length, 'Detected language:', detectedLang);
    
    // Language mapping: convert short codes to full locale codes for speech synthesis
    const languageMap = {
        'bn': 'bn-BD',    // Bengali (Bangladesh)
        'hi': 'hi-IN',    // Hindi (India) 
        'mr': 'mr-IN',    // Marathi (India)
        'ur': 'ur-PK',    // Urdu (Pakistan)
        'ta': 'ta-IN',    // Tamil (India)
        'te': 'te-IN',    // Telugu (India)
        'gu': 'gu-IN',    // Gujarati (India)
        'kn': 'kn-IN',    // Kannada (India)
        'ml': 'ml-IN',    // Malayalam (India)
        'pa': 'pa-IN',    // Punjabi (India)
        'as': 'as-IN',    // Assamese (India)
        'or': 'or-IN',    // Odia (India)
        'en': 'en-US',    // English (US)
        'ar': 'ar-SA',    // Arabic (Saudi Arabia)
        'zh': 'zh-CN',    // Chinese (China)
        'es': 'es-ES',    // Spanish (Spain)
        'fr': 'fr-FR',    // French (France)
        'de': 'de-DE',    // German (Germany)
        'it': 'it-IT',    // Italian (Italy)
        'pt': 'pt-PT',    // Portuguese (Portugal)
        'ru': 'ru-RU',    // Russian (Russia)
        'ja': 'ja-JP',    // Japanese (Japan)
        'ko': 'ko-KR',    // Korean (Korea)
        'th': 'th-TH',    // Thai (Thailand)
        'vi': 'vi-VN',    // Vietnamese (Vietnam)
        'id': 'id-ID',    // Indonesian (Indonesia)
        'ms': 'ms-MY',    // Malay (Malaysia)
        'tl': 'tl-PH',    // Filipino (Philippines)
        'my': 'my-MM',    // Myanmar (Myanmar)
        'km': 'km-KH',    // Khmer (Cambodia)
        'lo': 'lo-LA',    // Lao (Laos)
        'si': 'si-LK',    // Sinhala (Sri Lanka)
        'ne': 'ne-NP'     // Nepali (Nepal)
    };
    
    // PRIORITY: Use detected input language first, then fallback
    const selectedOption = $('#lang option:selected');
    let targetLang = detectedLang;
    
    // Convert short language code to full locale if needed
    if (targetLang && languageMap[targetLang]) {
        targetLang = languageMap[targetLang];
        console.log('🔄 Mapped language:', detectedLang, '->', targetLang);
    } else if (!targetLang) {
        targetLang = selectedOption.data('lang') || 'en-US';
    }
    
    console.log('🌍 Target language for speech:', targetLang);
    
    // Enhanced voice selection with better language matching
    let voice = null;
    let actualLang = targetLang;
    
    // Try exact language match first (e.g., 'bn-BD')
    voice = voices.find(v => v.lang === targetLang);
    if (voice) {
        console.log('✅ Found exact language match:', voice.name, voice.lang);
    } else {
        // Try language family match (e.g., 'bn' from 'bn-BD')
        const langCode = targetLang.split('-')[0];
        voice = voices.find(v => v.lang.startsWith(langCode));
        if (voice) {
            console.log('✅ Found language family match:', voice.name, voice.lang);
            actualLang = voice.lang;
        } else {
            // Fallback to English if target language not available
            voice = voices.find(v => v.lang.startsWith('en'));
            if (voice) {
                console.log('⚠️ Language not found, using English fallback:', voice.name, voice.lang);
                actualLang = voice.lang;
            } else {
                // Ultimate fallback - first available voice
                voice = voices[0];
                if (voice) {
                    console.log('⚠️ Using first available voice:', voice.name, voice.lang);
                    actualLang = voice.lang;
                }
            }
        }
    }

    if (!voice) {
        console.error('❌ No voice available for speech synthesis');
        return;
    }

    // Create utterance with proper language settings
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = actualLang; // Use the actual voice language
    utterance.voice = voice;
    utterance.rate = 0.9;
    utterance.volume = 1.0;
    
    console.log('🎙️ Speech setup:', {
        text: cleanText.substring(0, 50) + '...',
        targetLang: targetLang,
        actualLang: actualLang,
        voiceName: voice.name
    });

    // Show voice indicator
    $('#voiceIndicator').addClass('active').show();
    $('#voice_search').addClass('voice-active');

    // Set 25 second timeout ONLY for waiting for speech to start
    let startTimeout = setTimeout(() => {
        console.warn('⚠️ Speech failed to start within 25 seconds');
        synth.cancel();
        cleanupVoice();
    }, 25000);

    let speechStarted = false;

    // Event handlers
    utterance.onstart = () => {
        speechStarted = true;
        console.log('✅ Speech started - clearing timeout, will read complete response');
        clearTimeout(startTimeout); // Clear timeout once speech starts
        $('#voiceIndicator').addClass('speaking');
    };

    utterance.onend = () => {
        console.log('✅ Speech completed - full response read');
        if (!speechStarted) clearTimeout(startTimeout);
        cleanupVoice();
    };

    utterance.onerror = (event) => {
        console.error('❌ Speech error:', event.error, 'Target language:', targetLang);
        
        // Enhanced error handling with language-specific messages
        if (event.error === 'language-not-supported') {
            console.warn('⚠️ Language not supported:', targetLang, 'trying English fallback');
            // Could attempt fallback here if needed
        } else if (event.error === 'voice-unavailable') {
            console.warn('⚠️ Voice unavailable for language:', targetLang);
        } else if (event.error === 'network') {
            console.warn('⚠️ Network error during speech synthesis');
        } else if (event.error === 'synthesis-failed') {
            console.warn('⚠️ Speech synthesis failed for language:', targetLang);
        }
        
        if (!speechStarted) clearTimeout(startTimeout);
        cleanupVoice();
    };

    // Start speaking
    console.log('🚀 Starting speech');
    synth.speak(utterance);

    function cleanupVoice() {
        $('#voiceIndicator').removeClass('active speaking').hide();
        $('#voice_search').removeClass('voice-active speaking');
        console.log('🧹 Voice UI cleaned up');
    }
}
$(document).ready(function() {
    // Voice response controls
    $('#stopVoiceBtn').click(function() {
        console.log('🛑 Stop voice button clicked');
        stopSpeech();
        cleanupVoiceUI();
    });

    // Mic UI handlers
    $(document).click(function() {
        $('#microphone').removeClass('visible');
    });

    $('#voice_search').click(function(event) {
        stopSpeech();
        $('#microphone').addClass('visible');
        event.stopPropagation();
    });

    $('.recoder').click(function(event) {
        event.stopPropagation();
    });

    $('#microphone .close').click(function() {
        $('#microphone').removeClass('visible');
    });

    $('#customAlertClose').click(hideCustomAlert);
    $('#aboutLink').click(showAboutModal);
    $('#aboutModalClose').click(hideAboutModal);
});

// Populate voice/language selector with bn-BD priority and one voice per language
$(document).ready(function() {
    var synth = window.speechSynthesis;
    var $langSelect = $('#lang');

    function populateLanguages() {
        var voices = synth.getVoices();
        $langSelect.empty();

        // Build a map: language code -> best voice for that language
        function scoreVoice(v) {
            const name = (v.name || '').toLowerCase();
            let score = 0;
            if (name.includes('google')) score += 5;
            if (name.includes('microsoft')) score += 4;
            if (name.includes('natural') || name.includes('enhanced')) score += 2;
            if (PREFERRED_VOICE_ALIASES.map(n => n.toLowerCase()).includes(name)) score += 10;
            return score;
        }

        const byLang = {};
        voices.forEach(v => {
            const lang = v.lang || '';
            if (!lang) return;
            if (!byLang[lang] || scoreVoice(v) > scoreVoice(byLang[lang])) {
                byLang[lang] = v;
            }
        });

        // Ensure Bengali (Bangladesh) is included: map best bn* voice to bn-BD if bn-BD not present
        const bnVoices = voices.filter(v => (v.lang || '').toLowerCase().startsWith('bn'));
        if (!byLang['bn-BD'] && bnVoices.length) {
            const bestBn = bnVoices.reduce((a, b) => (scoreVoice(a) >= scoreVoice(b) ? a : b));
            byLang['bn-BD'] = bestBn;
        }

        // Sort languages: bn-BD first, then en-US, then others alphabetically
        const langs = Object.keys(byLang).sort((a,b) => {
            if (a === 'bn-BD') return -1;
            if (b === 'bn-BD') return 1;
            if (a === 'en-US') return -1;
            if (b === 'en-US') return 1;
            return a.localeCompare(b);
        });

        // If still no bn-BD in list, add a placeholder entry
        if (!langs.includes('bn-BD')) {
            langs.unshift('bn-BD');
        }

        // Populate options: one per language; value = lang, data-voice = voice name
        langs.forEach(lang => {
            const voice = byLang[lang];
            const label = voice ? `${lang} — ${voice.name}` : `${lang} — (no TTS voice)`;
            const $option = $('<option>', { value: lang, text: label });
            $option.attr('data-lang', lang);
            $option.attr('data-voice', voice ? voice.name : '');
            $langSelect.append($option);
        });

        // Restore preference or choose defaults with bn-BD priority
        const storedLang = localStorage.getItem(LANG_STORAGE_KEY) || '';
        const storedVoiceName = localStorage.getItem(VOICE_STORAGE_KEY) || '';

        let selected = false;
        function selectByLang(lang) {
            const opt = $langSelect.children().filter(function(){ return ($(this).val()||'') === lang; }).first();
            if (opt.length) { opt.prop('selected', true); return true; }
            return false;
        }

        // 1) Stored lang if present
        if (storedLang && selectByLang(storedLang)) selected = true;
        // 2) bn-BD
        if (!selected && selectByLang('bn-BD')) selected = true;
        // 3) en-US
        if (!selected && selectByLang('en-US')) selected = true;
        // 4) First available
        if (!selected && $langSelect.children().length > 0) $langSelect.children().first().prop('selected', true);

        // Persist the decided selection
        const selLang = ($langSelect.find('option:selected').attr('data-lang') || 'en-US');
        const selVoice = ($langSelect.find('option:selected').attr('data-voice') || '');
        if (selLang) localStorage.setItem(LANG_STORAGE_KEY, selLang);
        if (selVoice) localStorage.setItem(VOICE_STORAGE_KEY, selVoice);
    }

    populateLanguages();

    if (typeof synth.onvoiceschanged !== 'undefined') {
        synth.onvoiceschanged = populateLanguages;
    }

    // Save user selection changes
    $langSelect.on('change', function() {
        var lang = ($(this).find('option:selected').attr('data-lang') || '');
        var voice = ($(this).find('option:selected').attr('data-voice') || '');
        if (voice) localStorage.setItem(VOICE_STORAGE_KEY, voice);
        if (lang) localStorage.setItem(LANG_STORAGE_KEY, lang);
    });
});

$(document).ready(function() {
    var speech;
    let r = 0;
    let voices = [];
    let synth;
    let micActive = false;
    let mediaStream = null;

    window.addEventListener("load", () => {
        synth = window.speechSynthesis;
        voices = synth.getVoices();
        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = voices;
        }
    });

    function checkhSpeach() {
        $('#speakBtn').removeClass('active');
        
        // Mark this as a voice-initiated conversation with extended timeout for long responses
        isVoiceConversation = true;
        console.log('🎤 Voice conversation initiated');
        
        // Set a generous timeout for voice conversation (5 minutes) to handle long backend processing
        if (window.voiceConversationTimeout) {
            clearTimeout(window.voiceConversationTimeout);
        }
        window.voiceConversationTimeout = setTimeout(() => {
            console.log('⏰ Voice conversation timeout - resetting state');
            isVoiceConversation = false;
        }, 300000); // 5 minutes timeout
        
        if (r == 0) {
            // new Audio('assets/audio/end.mp3').play();
            setTimeout(function() {
                speech.recognition.stop();
                speechText();
                $('#sendBtn').click();
            }, 4000); // Increased to 8 seconds for mobile compatibility
        }
        r++;
        setTimeout(function() {
            r = 0;
        }, 4000); // Increased to 8 seconds for mobile compatibility

        let text = $('#recoredText').text().trim();
        if (text.length > 1) {
            $('#prompt').val(text);
            $('#recoredText').val('');
            $("#prompt").trigger("keyup");
            $('#microphone').removeClass('visible');
        }
    }

    $('#speakBtn').click(function() {
        if ($('#speakBtn').hasClass('active')) {
            // Stop listening when user clicks again
            $('#speakBtn').removeClass('active');
            if (speech && speech.recognition) {
                speech.recognition.stop();
            }
        } else {
            // Start listening
            $('#speakBtn').addClass('active');
            new Audio('assets/audio/start.mp3').play();
            setTimeout(function() {
                // Recognition language = selected language (prioritize stored), default bn-BD then en-US
                let language = ($('#microphone select option:selected').data('lang') || '').toString();
                if (!language) language = (localStorage.getItem(LANG_STORAGE_KEY) || '');
                if (!language) language = 'bn-BD';
                if (!language) language = 'en-US';
                speak(language);
                if (speech && speech.recognition) {
                    speech.recognition.start();
                }
            }, 300);

            $('#mic-status').removeClass('active').text('Microphone is off');
        }
    });

    function speak(language) {
        window.SpeechRecognition = window.SpeechRecognition ||
            window.webkitSpeechRecognition ||
            window.mozSpeechRecognition;


        speech = {
            enabled: true,
            listening: false,
            recognition: new SpeechRecognition(),
            text: ""
        };
        speech.recognition.continuous = true;
        speech.recognition.interimResults = true;
        speech.recognition.lang = language;

        speech.recognition.addEventListener("result", (event) => {
            const audio = event.results[event.results.length - 1];
            speech.text = audio[0].transcript;
            const tag = document.activeElement.nodeName;
            if (tag === "INPUT" || tag === "TEXTAREA") {
                if (audio.isFinal) {
                    document.activeElement.value += speech.text;
                }
            }
            $('#recoredText').text(speech.text);

            if (audio.isFinal) {
                checkhSpeach();
            }
        });
    }



    function speechText() {
        let say = $('#recoredText').text().trim();
        if (!say) return;

        isVoice = 1;

        let synth = window.speechSynthesis;

        let voices = synth.getVoices();
        if (!voices.length) {
            synth.onvoiceschanged = () => speechText(); // Retry after voices load
            return;
        }

        const selectedOption = $('#lang option:selected');
        const selectedLang = selectedOption.data('lang') || 'bn-BD';
        const selectedVoiceName = selectedOption.data('voice') || localStorage.getItem(VOICE_STORAGE_KEY) || '';

        // Prefer the exact selected voice by name, then fallback by language
        let voiceToUse = voices.find(v => v.name === selectedVoiceName) ||
            voices.find(v => (v.lang || '') === selectedLang) ||
            voices.find(v => (v.lang || '').startsWith(selectedLang.split('-')[0])) ||
            voices.find(v => (v.lang || '').startsWith('bn-BD')) ||
            voices.find(v => (v.lang || '').startsWith('en-US'));

        if (selectedLang.startsWith('en')) say = 'Showing prompt: ' + say;
        else if (selectedLang.startsWith('bn')) say = 'প্রম্পট দেখানো হচ্ছে: ' + say;
        else if (selectedLang.startsWith('hi')) say = 'प्रॉम्प्ट दिखा रहा है: ' + say;
        else if (selectedLang.startsWith('ur')) say = 'پرومپٹ دکھا رہا ہے: ' + say;
        else if (selectedLang.startsWith('fr')) say = 'affichage de l’invite : ' + say;
        else if (selectedLang.startsWith('pt')) say = 'mostrando o prompt: ' + say;

        // Speak
        let utterance = new SpeechSynthesisUtterance(say);
        utterance.lang = selectedLang || 'bn-BD';
        if (voiceToUse) utterance.voice = voiceToUse;
        synth.speak(utterance);
    }

    $('#stopVoiceBtn').click(function() {
        speech.recognition.stop();
        stopSpeech();
        isVoiceConversation = false; // Reset voice conversation flag
    });

});

function showCustomAlert(message) {
    $('#customAlertMessage').html(message);
    $('#customAlert').addClass('visible');
}

function hideCustomAlert() {
    $('#customAlert').removeClass('visible');
}

function showAboutModal() {
    $('#aboutModal').addClass('visible');
}

function hideAboutModal() {
    $('#aboutModal').removeClass('visible');
}