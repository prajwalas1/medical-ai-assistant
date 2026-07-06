import { useState } from "react";
import LanguageSelector from "../components/VoiceAssistant/LanguageSelector";
import ListeningAnimation from "../components/VoiceAssistant/ListeningAnimation";
import VoiceControls from "../components/VoiceAssistant/VoiceControls";

import { useVoice } from "../hooks/useVoice";

export default function Home() {
  const [language, setLanguage] = useState("en");

  const {
    callStarted,
    isListening,
    isProcessing,
    isSpeaking,
    startCall,
    stopCall,
  } = useVoice();

  return (
    <div className="min-h-screen bg-slate-100 flex justify-center items-center">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl p-8">
        <h1 className="text-3xl font-bold text-center">
          ABC Hospital Voice Assistant
        </h1>
        <p className="text-center text-gray-500 mt-2">
          AI Powered Appointment Booking
        </p>

        <div className="mt-8">
          <LanguageSelector
            value={language}
            onChange={setLanguage}
            disabled={callStarted}
          />
        </div>

        <ListeningAnimation isListening={isListening} isSpeaking={isSpeaking} />

        <div className="mt-8">
          <VoiceControls
            callStarted={callStarted}
            isListening={isListening}
            isProcessing={isProcessing}
            isSpeaking={isSpeaking}
            startCall={() => startCall(language)}
            stopCall={stopCall}
          />
        </div>
      </div>
    </div>
  );
}