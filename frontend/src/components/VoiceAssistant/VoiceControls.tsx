import { Mic, PhoneOff } from "lucide-react";

interface VoiceControlsProps {
  callStarted: boolean;
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  startCall: () => void;
  stopCall: () => void;
  startDisabled?: boolean;
}

export default function VoiceControls({
  callStarted,
  isListening,
  isProcessing,
  isSpeaking,
  startCall,
  stopCall,
  startDisabled,
}: VoiceControlsProps) {
  return (
    <div className="flex flex-col items-center gap-4">
      {!callStarted ? (
        <button
          onClick={startCall}
          disabled={startDisabled}
          className="flex items-center gap-2 px-9 py-3.5 rounded-full bg-[#1F6F64] text-white text-sm font-medium shadow-lg shadow-[#1F6F64]/20 transition hover:bg-[#195a51] hover:shadow-xl hover:shadow-[#1F6F64]/25 active:scale-[0.98] disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none disabled:cursor-not-allowed disabled:active:scale-100"
        >
          <Mic size={18} />
          Start Call
        </button>
      ) : (
        <button
          onClick={stopCall}
          className="flex items-center gap-2 px-9 py-3.5 rounded-full bg-[#E2654D] text-white text-sm font-medium shadow-lg shadow-[#E2654D]/20 transition hover:bg-[#c9553f] active:scale-[0.98]"
        >
          <PhoneOff size={18} />
          End Call
        </button>
      )}

      {callStarted && (
        <div className="text-sm font-medium text-slate-600 tracking-wide">
          {isListening && "Listening…"}
          {isProcessing && "Thinking…"}
          {isSpeaking && "Speaking…"}
        </div>
      )}
    </div>
  );
}