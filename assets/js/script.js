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
    
    // Enhanced voice selection with better language matching and Bengali support
    let voice = null;
    let actualLang = targetLang;
    
    // Special handling for Bengali voices
    if (targetLang === 'bn-BD' || targetLang.startsWith('bn')) {
        // Try multiple Bengali voice patterns
        voice = voices.find(v => v.lang === 'bn-BD') ||
                voices.find(v => v.lang === 'bn-IN') ||
                voices.find(v => v.lang.startsWith('bn')) ||
                voices.find(v => v.name.toLowerCase().includes('bengali')) ||
                voices.find(v => v.name.toLowerCase().includes('bangla'));
        
        if (voice) {
            console.log('✅ Found Bengali voice:', voice.name, voice.lang);
            actualLang = voice.lang;
        } else {
            console.warn('⚠️ Bengali voice not found, checking other options...');
        }
    }
    
    // General voice selection if Bengali not found or other languages
    if (!voice) {
        // Try exact language match first (e.g., 'hi-IN')
        voice = voices.find(v => v.lang === targetLang);
        if (voice) {
            console.log('✅ Found exact language match:', voice.name, voice.lang);
        } else {
            // Try language family match (e.g., 'hi' from 'hi-IN')
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
    }

    if (!voice) {
        console.error('❌ No voice available for speech synthesis');
        return;
    }

    // Create utterance with optimized settings for different languages
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = actualLang;
    utterance.voice = voice;
    
    // Language-specific optimizations
    if (actualLang.startsWith('bn')) {
        // Bengali voice optimization
        utterance.rate = 0.8; // Slower for better Bengali pronunciation
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        console.log('🎯 Bengali voice optimization applied');
    } else if (actualLang.startsWith('hi')) {
        // Hindi voice optimization
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
    } else if (actualLang.startsWith('en')) {
        // English voice optimization
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
    } else {
        // Default settings for other languages
        utterance.rate = 0.85;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
    }
    
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
            // Play end audio if available
            try {
                new Audio('assets/audio/end.mp3').play().catch(e => console.log('End audio play failed:', e));
            } catch (e) {
                console.log('End audio not available:', e);
            }
            
            setTimeout(function() {
                if (speech && speech.recognition) {
                    speech.recognition.stop();
                    speech.listening = false;
                }
                speechText();
                
                // Process the voice input
                let text = $('#recoredText').text().trim();
                if (text && text.length > 1 && text !== 'Listening...') {
                    console.log('🎤 Processing voice input:', text);
                    $('#prompt').val(text);
                    $('#recoredText').text('');
                    $("#prompt").trigger("keyup");
                    
                    // Hide microphone UI and send the message
                    setTimeout(() => {
                        $('#microphone').removeClass('visible');
                        $('#sendBtn').click();
                    }, 100);
                } else {
                    console.warn('⚠️ No valid voice input detected');
                    $('#microphone').removeClass('visible');
                }
            }, 2000); // Reduced to 2 seconds for better mobile experience
        }
        r++;
        setTimeout(function() {
            r = 0;
        }, 3000); // Reduced to 3 seconds for mobile compatibility
    }

    $('#speakBtn').click(function() {
        // Prevent multiple rapid clicks (debouncing for mobile)
        if ($(this).hasClass('processing')) {
            return;
        }
        
        $(this).addClass('processing');
        setTimeout(() => $(this).removeClass('processing'), 1000);

        if ($('#speakBtn').hasClass('active')) {
            // Stop listening when user clicks again
            console.log('🛑 Stopping voice recognition');
            $('#speakBtn').removeClass('active');
            if (speech && speech.recognition) {
                speech.recognition.stop();
                speech.listening = false;
            }
            $('#mic-status').removeClass('active').text('Microphone is off');
        } else {
            // Start listening
            console.log('🎤 Starting voice recognition');
            $('#speakBtn').addClass('active');
            
            // Play audio feedback if available
            try {
                new Audio('assets/audio/start.mp3').play().catch(e => console.log('Audio play failed:', e));
            } catch (e) {
                console.log('Audio not available:', e);
            }
            
            // Reset speech state
            if (speech) {
                speech.finalTranscript = '';
                speech.interimTranscript = '';
                speech.text = '';
            }
            
            setTimeout(function() {
                try {
                    // Recognition language = selected language (prioritize stored), default bn-BD then en-US
                    let language = ($('#microphone select option:selected').data('lang') || '').toString();
                    if (!language) language = (localStorage.getItem(LANG_STORAGE_KEY) || '');
                    if (!language) language = 'bn-BD';
                    if (!language) language = 'en-US';
                    
                    console.log('🌍 Voice recognition language:', language);
                    
                    speak(language);
                    if (speech && speech.recognition) {
                        speech.recognition.start();
                    }
                } catch (error) {
                    console.error('🎤 Error starting voice recognition:', error);
                    $('#speakBtn').removeClass('active');
                    showCustomAlert('Voice recognition failed to start. Please try again.');
                }
            }, 300); // Slight delay to allow UI update

            $('#mic-status').addClass('active').text('Microphone is on - Speak now');
        }
    });

    function speak(language) {
        window.SpeechRecognition = window.SpeechRecognition ||
            window.webkitSpeechRecognition ||
            window.mozSpeechRecognization;

        if (!window.SpeechRecognition) {
            console.error('🎤 Speech recognition not supported in this browser');
            showCustomAlert('Voice input is not supported in this browser. Please use a supported browser like Chrome.');
            return;
        }

        speech = {
            enabled: true,
            listening: false,
            recognition: new SpeechRecognition(),
            text: "",
            finalTranscript: "",
            interimTranscript: ""
        };
        
        // Enhanced settings for mobile Chrome compatibility
        speech.recognition.continuous = false; // Changed to false for better mobile experience
        speech.recognition.interimResults = true;
        speech.recognition.lang = language;
        speech.recognition.maxAlternatives = 1;
        
        // Mobile Chrome optimization
        if (/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent)) {
            speech.recognition.continuous = false; // Disable continuous for mobile
            console.log('📱 Mobile device detected - optimizing voice recognition');
        }

        // Enhanced result handling with better final result detection
        speech.recognition.addEventListener("result", (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Update display with interim results
            const displayText = finalTranscript + interimTranscript;
            $('#recoredText').text(displayText);
            
            // Store the current state
            speech.finalTranscript = finalTranscript;
            speech.interimTranscript = interimTranscript;
            speech.text = displayText;

            // Process final results
            if (finalTranscript) {
                console.log('🎤 Final transcript received:', finalTranscript);
                setTimeout(() => {
                    checkhSpeach();
                }, 500); // Small delay to ensure processing
            }
        });

        // Enhanced error handling for mobile Chrome
        speech.recognition.addEventListener("error", (event) => {
            console.error('🎤 Speech recognition error:', event.error);
            
            switch(event.error) {
                case 'no-speech':
                    console.warn('⚠️ No speech detected. Please try again.');
                    break;
                case 'audio-capture':
                    showCustomAlert('Microphone access denied. Please allow microphone access and try again.');
                    break;
                case 'not-allowed':
                    showCustomAlert('Microphone access not allowed. Please enable microphone permissions.');
                    break;
                case 'network':
                    showCustomAlert('Network error. Please check your internet connection.');
                    break;
                case 'service-not-allowed':
                    showCustomAlert('Speech recognition service not available. Please try again later.');
                    break;
                default:
                    console.warn('⚠️ Speech recognition error:', event.error);
            }
            
            // Reset UI on error
            $('#voice_search').removeClass('voice-active');
            $('#recoredText').text('');
        });

        // Handle recognition end
        speech.recognition.addEventListener("end", () => {
            console.log('🎤 Speech recognition ended');
            $('#voice_search').removeClass('voice-active');
            
            // For mobile, auto-restart if we're still listening and no final result
            if (speech.listening && !speech.finalTranscript && /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent)) {
                console.log('📱 Auto-restarting recognition for mobile');
                setTimeout(() => {
                    if (speech.listening) {
                        try {
                            speech.recognition.start();
                        } catch (e) {
                            console.error('Failed to restart recognition:', e);
                        }
                    }
                }, 100);
            }
        });

        // Handle recognition start
        speech.recognition.addEventListener("start", () => {
            console.log('🎤 Speech recognition started');
            $('#voice_search').addClass('voice-active');
            speech.listening = true;
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
    
    // Prevent body scrolling when modal is open (mobile fix)
    $('body').addClass('modal-open');
    
    // Add escape key handler
    $(document).on('keydown.aboutModal', function(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            hideAboutModal();
        }
    });
    
    // Add click outside to close (mobile-friendly)
    $('#aboutModal').on('click.aboutModal', function(e) {
        if (e.target === this) {
            hideAboutModal();
        }
    });
    
    // Focus management for accessibility
    setTimeout(() => {
        $('#aboutModalClose').focus();
    }, 100);
}

function hideAboutModal() {
    $('#aboutModal').removeClass('visible');
    
    // Re-enable body scrolling
    $('body').removeClass('modal-open');
    
    // Remove event handlers
    $(document).off('keydown.aboutModal');
    $('#aboutModal').off('click.aboutModal');
    
    // Return focus to the about link
    $('#aboutLink').focus();
}