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

// Function to speak AI response
function speakAIResponse(text, detectedLang, forceSpeak = false) {
    // Check sessionStorage for voice conversation persistence (mobile compatibility)
    const wasVoiceConversation = sessionStorage.getItem('isVoiceConversation') === 'true';
    if (wasVoiceConversation) {
        isVoiceConversation = true;
    }
    
    console.log('speakAIResponse called:', { text: text?.length, detectedLang, isVoiceConversation, wasVoiceConversation, forceSpeak });
    
    // Check if we should speak: either voice conversation or user preference for always speaking
    const shouldSpeak = isVoiceConversation || wasVoiceConversation || forceSpeak || localStorage.getItem('alwaysSpeak') === 'true';
    
    if (!shouldSpeak) {
        console.log('Not a voice conversation and no force speak, skipping speech');
        return;
    }

    let synth = window.speechSynthesis;
    let voices = synth.getVoices();
    
    if (!voices.length) {
        console.log('No voices available, waiting for voices to load');
        synth.onvoiceschanged = () => speakAIResponse(text, detectedLang);
        return;
    }

    // Clean HTML tags from response for speech
    let cleanText = text.replace(/<[^>]*>/g, ' ')
                       .replace(/\s+/g, ' ')
                       .replace(/&nbsp;/g, ' ')
                       .replace(/&amp;/g, '&')
                       .replace(/&lt;/g, '<')
                       .replace(/&gt;/g, '>')
                       .replace(/&quot;/g, '"')
                       .trim();

    console.log('Clean text for speech:', cleanText.substring(0, 100) + '...');

    // Use detected language or fallback to stored preference
    const selectedOption = $('#lang option:selected');
    const preferredLang = detectedLang || selectedOption.data('lang') || 'bn-BD';
    const preferredVoiceName = selectedOption.data('voice') || localStorage.getItem(VOICE_STORAGE_KEY) || '';

    console.log('Voice preferences:', { preferredLang, preferredVoiceName, detectedLang });

    // Enhanced voice selection with Bangla priority
    let voiceToUse = null;
    
    // First, try exact match with preferred voice and language
    if (preferredVoiceName) {
        voiceToUse = voices.find(v => v.name === preferredVoiceName && (v.lang || '').startsWith(preferredLang.split('-')[0]));
    }
    
    // Then try exact language match
    if (!voiceToUse) {
        voiceToUse = voices.find(v => (v.lang || '') === preferredLang);
    }
    
    // For Bangla, try various Bengali language codes
    if (!voiceToUse && (preferredLang.startsWith('bn') || detectedLang?.startsWith('bn'))) {
        voiceToUse = voices.find(v => (v.lang || '').startsWith('bn-BD')) ||
                     voices.find(v => (v.lang || '').startsWith('bn-IN')) ||
                     voices.find(v => (v.lang || '').startsWith('bn')) ||
                     voices.find(v => (v.name || '').toLowerCase().includes('bangla')) ||
                     voices.find(v => (v.name || '').toLowerCase().includes('bengali'));
    }
    
    // Fallback to language family match
    if (!voiceToUse) {
        voiceToUse = voices.find(v => (v.lang || '').startsWith(preferredLang.split('-')[0]));
    }

    console.log('Selected voice:', voiceToUse?.name, voiceToUse?.lang);

    // If no specific voice is found for the language, use fallback strategy
    if (!voiceToUse) {
        console.log('No specific voice found, trying fallback voices');
        
        // Try to find any available voice, prioritizing common languages
        voiceToUse = voices.find(v => (v.lang || '').startsWith('en-US')) ||
                     voices.find(v => (v.lang || '').startsWith('en')) ||
                     voices.find(v => (v.lang || '').startsWith('hi')) ||
                     voices[0];
        
        if (!voiceToUse) {
            let langDisplayName = preferredLang;
            try {
                langDisplayName = new Intl.DisplayNames(['en'], { type: 'language' }).of(preferredLang.split('-')[0]) || preferredLang;
            } catch (e) {
                // Fallback if DisplayNames is not supported
                if (preferredLang.startsWith('bn')) langDisplayName = 'Bengali';
                else if (preferredLang.startsWith('hi')) langDisplayName = 'Hindi';
                else if (preferredLang.startsWith('ur')) langDisplayName = 'Urdu';
            }
            
            const alertMessage = `Could not find a voice for <strong>${langDisplayName}</strong> to read the response. You may need to install the text-to-speech voice pack for this language in your browser or operating system.`;
            
            showCustomAlert(alertMessage);

            console.warn(`No voice found for language: ${preferredLang}. Cannot speak response.`);
            
            // Clean up UI and flags as if speech ended
            $('#voiceIndicator').removeClass('active');
            $('#voice_search').removeClass('voice-active');
            isVoiceConversation = false;
            sessionStorage.removeItem('isVoiceConversation');
            return;
        } else if (preferredLang.startsWith('bn')) {
            // For Bangla content with non-Bangla voice, show informative message
            console.log('Using non-Bengali voice for Bengali content, may not sound natural');
        }
    }

    // Create and configure speech utterance
    let utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = preferredLang || 'bn-BD';
    if (voiceToUse) utterance.voice = voiceToUse;
    
    // Adjust speech parameters based on language and device
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (preferredLang.startsWith('bn')) {
        // Optimize for Bengali speech
        utterance.rate = isMobile ? 0.8 : 0.85;
        utterance.pitch = 1.1;
    } else if (preferredLang.startsWith('hi') || preferredLang.startsWith('ur')) {
        // Optimize for Hindi/Urdu speech
        utterance.rate = isMobile ? 0.8 : 0.9;
        utterance.pitch = 1.0;
    } else {
        // Default for English and other languages
        utterance.rate = isMobile ? 0.85 : 0.9;
        utterance.pitch = 1.0;
    }
    
    utterance.volume = 1.0;

    // Show voice indicator
    $('#voiceIndicator').addClass('active');
    $('#voice_search').addClass('voice-active');

    // Add event listeners for better user experience
    utterance.onstart = () => {
        console.log('Started speaking AI response');
    };
    
    utterance.onend = () => {
        console.log('Finished speaking AI response');
        // Hide voice indicator
        $('#voiceIndicator').removeClass('active');
        $('#voice_search').removeClass('voice-active');
        // Reset voice conversation flag after response is complete
        isVoiceConversation = false;
        sessionStorage.removeItem('isVoiceConversation');
    };

    utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event.error);
        // Hide voice indicator on error
        $('#voiceIndicator').removeClass('active');
        $('#voice_search').removeClass('voice-active');
        isVoiceConversation = false;
        sessionStorage.removeItem('isVoiceConversation');
    };

    // Stop any current speech and speak the new response
    console.log('Starting speech synthesis...');
    stopSpeech();
    synth.speak(utterance);
}
$(document).ready(function() {
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

    let voiceTimeout = null;
    let lastVoiceActivity = Date.now();
    
    function checkhSpeach() {
        $('#speakBtn').removeClass('active');
        
        // Mark this as a voice-initiated conversation and store persistently
        isVoiceConversation = true;
        sessionStorage.setItem('isVoiceConversation', 'true');
        
        // Update last voice activity timestamp
        lastVoiceActivity = Date.now();
        
        // Clear any existing timeout
        if (voiceTimeout) {
            clearTimeout(voiceTimeout);
        }
        
        if (r == 0) {
            // Mobile-friendly approach: shorter initial delay but more reliable
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            const initialDelay = isMobile ? 1500 : 2500;
            const silenceThreshold = isMobile ? 1500 : 2000;
            
            voiceTimeout = setTimeout(function() {
                // Check if enough time has passed since last voice activity
                const timeSinceLastActivity = Date.now() - lastVoiceActivity;
                if (timeSinceLastActivity >= silenceThreshold) {
                    speech.recognition.stop();
                    speechText();
                    // Store voice flag again before sending
                    isVoiceConversation = true;
                    sessionStorage.setItem('isVoiceConversation', 'true');
                    $('#sendBtn').click();
                } else {
                    // Extend the wait if user was speaking recently
                    voiceTimeout = setTimeout(function() {
                        speech.recognition.stop();
                        speechText();
                        // Store voice flag again before sending
                        isVoiceConversation = true;
                        sessionStorage.setItem('isVoiceConversation', 'true');
                        $('#sendBtn').click();
                    }, Math.max(500, silenceThreshold - timeSinceLastActivity));
                }
            }, initialDelay);
        }
        r++;
        setTimeout(function() {
            r = 0;
        }, 4000); // Increased from 3000ms to 4000ms

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
            }, 500);

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
            
            // Update last voice activity on any speech detection (interim or final)
            lastVoiceActivity = Date.now();
            
            const tag = document.activeElement.nodeName;
            if (tag === "INPUT" || tag === "TEXTAREA") {
                if (audio.isFinal) {
                    document.activeElement.value += speech.text;
                }
            }
            $('#recoredText').text(speech.text);

            // Only process when speech is final AND we have substantial text
            if (audio.isFinal && speech.text.trim().length > 2) {
                checkhSpeach();
            }
        });

        // Handle recognition end event
        speech.recognition.addEventListener("end", (event) => {
            // Clear any pending timeouts when recognition ends
            if (voiceTimeout) {
                clearTimeout(voiceTimeout);
                voiceTimeout = null;
            }
            $('#speakBtn').removeClass('active');
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
        // Clear any pending voice processing timeouts
        if (voiceTimeout) {
            clearTimeout(voiceTimeout);
            voiceTimeout = null;
        }
        
        speech.recognition.stop();
        stopSpeech();
        isVoiceConversation = false; // Reset voice conversation flag
        $('#speakBtn').removeClass('active');
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