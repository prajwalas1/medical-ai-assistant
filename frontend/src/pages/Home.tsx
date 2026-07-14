import { useState } from "react";
import { AudioLines, Sparkles } from "lucide-react";
import LanguageSelector from "../components/VoiceAssistant/LanguageSelector";
import ProviderSelector from "../components/VoiceAssistant/ProviderSelector";
import ListeningAnimation from "../components/VoiceAssistant/ListeningAnimation";
import VoiceControls from "../components/VoiceAssistant/VoiceControls";

import { useVoice } from "../hooks/useVoice";

const LANGUAGE_LABELS: Record<string, string> = {
  en: "English",
  hi: "Hindi",
  kn: "Kannada",
};

const STT_OPTIONS = [
  { value: "sarvam", label: "Sarvam", supportedLanguages: ["en", "hi", "kn"] },
  { value: "deepgram", label: "Deepgram", supportedLanguages: ["en", "hi"] },
  { value: "elevenlabs", label: "ElevenLabs", supportedLanguages: ["en", "hi", "kn"] },
];

const LLM_OPTIONS = [
  { value: "sarvam", label: "Sarvam", supportedLanguages: ["en", "hi", "kn"] },
];

export default function Home() {
  const [language, setLanguage] = useState("en");
  const [sttProvider, setSttProvider] = useState("sarvam");
  const [llmProvider, setLlmProvider] = useState("sarvam");

  const {
    callStarted,
    isListening,
    isProcessing,
    isSpeaking,
    startCall,
    stopCall,
  } = useVoice();

  const selectedStt = STT_OPTIONS.find((o) => o.value === sttProvider);
  const isMismatch = Boolean(
    selectedStt && !selectedStt.supportedLanguages.includes(language)
  );

  const handleStart = () => {
    if (isMismatch) return;
    startCall(language, sttProvider, llmProvider);
  };

  return (
    <div className="min-h-screen bg-[#EEF2F4] flex justify-center items-center px-4 py-12">
      <div className="w-full max-w-3xl bg-white rounded-3xl shadow-xl shadow-slate-900/5 border border-slate-100 p-10 sm:p-12">
        <div className="text-center mb-10">
          <p className="text-[11px] font-semibold tracking-[0.18em] text-[#1F6F64] uppercase mb-3">
            ABC Hospital · Voice Reception
          </p>
          <h1
            className="text-4xl sm:text-[2.75rem] font-semibold text-[#16302E] leading-tight"
            style={{ fontFamily: "'Fraunces', serif" }}
          >
            Talk to us, we're listening
          </h1>
          <p className="text-slate-500 mt-3 text-[15px]">
            AI-powered appointment booking, day or night.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-100 bg-slate-50/60 p-5 mb-10">
          <p className="text-xs font-semibold tracking-wide text-slate-400 uppercase mb-4">
            Call setup
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <LanguageSelector
              value={language}
              onChange={setLanguage}
              disabled={callStarted}
            />
            <ProviderSelector
              label="Speech-to-Text"
              icon={AudioLines}
              value={sttProvider}
              onChange={setSttProvider}
              options={STT_OPTIONS}
              disabled={callStarted}
              language={language}
            />
            <ProviderSelector
              label="Language Model"
              icon={Sparkles}
              value={llmProvider}
              onChange={setLlmProvider}
              options={LLM_OPTIONS}
              disabled={callStarted}
              language={language}
            />
          </div>

          {isMismatch && (
            <p className="text-[#E2654D] text-xs font-medium mt-4 text-center">
              {selectedStt?.label} doesn't support {LANGUAGE_LABELS[language]}.
              Please select English{selectedStt?.value === "deepgram" ? " or Hindi" : ""}, or choose Sarvam.
            </p>
          )}
        </div>

        <ListeningAnimation isListening={isListening} isSpeaking={isSpeaking} />

        <div className="mt-10">
          <VoiceControls
            callStarted={callStarted}
            isListening={isListening}
            isProcessing={isProcessing}
            isSpeaking={isSpeaking}
            startCall={handleStart}
            stopCall={stopCall}
            startDisabled={isMismatch}
          />
        </div>
      </div>
    </div>
  );
}