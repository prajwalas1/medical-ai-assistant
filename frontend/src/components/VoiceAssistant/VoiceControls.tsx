import { Mic, PhoneOff } from "lucide-react";

interface VoiceControlsProps {
  callStarted: boolean;
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  startCall: () => void;
  stopCall: () => void;
}

export default function VoiceControls({
  callStarted,
  isListening,
  isProcessing,
  isSpeaking,
  startCall,
  stopCall,
}: VoiceControlsProps) {
  return (
    <div className="flex flex-col items-center gap-5">

      {!callStarted ? (
        <button
          onClick={startCall}
          className="flex items-center gap-2 px-8 py-4 rounded-full bg-green-600 text-white hover:bg-green-700 transition"
        >
          <Mic size={22} />
          Start Call
        </button>
      ) : (
        <button
          onClick={stopCall}
          className="flex items-center gap-2 px-8 py-4 rounded-full bg-red-600 text-white hover:bg-red-700 transition"
        >
          <PhoneOff size={22} />
          End Call
        </button>
      )}

      {callStarted && (
        <div className="text-lg font-medium">

          {isListening && "🎤 Listening..."}

          {isProcessing && "⏳ Processing..."}

          {isSpeaking && "🔊 Speaking..."}

        </div>
      )}

    </div>
  );
}