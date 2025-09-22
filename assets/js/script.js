var isVoice = 0;

function stopSpeech() {
    const speechEngine = window.speechSynthesis;
    if (speechEngine.speaking) {
        speechEngine.cancel();
    }
}
$(document).ready(function() {

    $(document).click(function() {
        $('#microphone').removeClass('visible');
    })

    $('#voice_search').click(function(event) {
        stopSpeech();
        $('#microphone').addClass('visible');
        event.stopPropagation();

    })

    $(".recoder").click(function(event) {
        event.stopPropagation();

    })
    $('#microphone .close').click(function() {
        $('#microphone').removeClass('visible');
    })

});




$(document).ready(function() {
    var synth = window.speechSynthesis;
    var $langSelect = $('#lang');

    function populateLanguages() {
        var voices = synth.getVoices();
        $langSelect.empty();

        var addedLangs = new Set();
        var defaultSet = false;

        $.each(voices, function(index, voice) {
            if (!addedLangs.has(voice.lang)) {
                var $option = $('<option>', {
                    value: voice.lang,
                    text: voice.name + ' - ' + voice.lang
                });

                if (voice.name.includes()) {
                    $option.prop('selected', true);
                    defaultSet = true;
                }

                $langSelect.append($option);
                addedLangs.add(voice.lang);
            }
        });

        if (!defaultSet && $langSelect.children().length > 0) {
            $langSelect.children().first().prop('selected', true);
        }
    }

    populateLanguages();

    if (typeof synth.onvoiceschanged !== 'undefined') {
        synth.onvoiceschanged = populateLanguages;
    }
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
        if (r == 0) {
            // new Audio('assets/audio/end.mp3').play();
            setTimeout(function() {
                speech.recognition.stop();
                speechText();
                $('#sendBtn').click();
            }, 1500);
        }
        r++;
        setTimeout(function() {
            r = 0;
        }, 3000);

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
                let language = $('#microphone select').val().trim();
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

        let selectedLang = $('#lang').val() || 'en-US';

        let voiceToUse = voices.find(v => v.lang.startsWith(selectedLang)) ||
            voices.find(v => v.lang.startsWith('en-US'));

        if (selectedLang.startsWith('en')) say = 'Showing prompt: ' + say;
        else if (selectedLang.startsWith('bn')) say = 'প্রম্পট দেখানো হচ্ছে: ' + say;
        else if (selectedLang.startsWith('hi')) say = 'प्रॉम्प्ट दिखा रहा है: ' + say;
        else if (selectedLang.startsWith('ur')) say = 'پرومپٹ دکھا رہا ہے: ' + say;
        else if (selectedLang.startsWith('fr')) say = 'affichage de l’invite : ' + say;
        else if (selectedLang.startsWith('pt')) say = 'mostrando o prompt: ' + say;

        // Speak
        let utterance = new SpeechSynthesisUtterance(say);
        if (voiceToUse) utterance.voice = voiceToUse;
        synth.speak(utterance);
    }




});
