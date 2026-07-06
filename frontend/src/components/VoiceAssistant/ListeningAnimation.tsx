interface Props {
  isListening: boolean;
  isSpeaking: boolean;
}

export default function ListeningAnimation({
  isListening,
  isSpeaking,
}: Props) {
  return (
    <div className="flex justify-center mt-6">

      <div
        className={`
          w-28
          h-28
          rounded-full
          transition-all
          duration-300
          ${
            isListening
              ? "bg-green-500 animate-pulse scale-110"
              : isSpeaking
              ? "bg-blue-500 animate-ping"
              : "bg-gray-300"
          }
        `}
      />

    </div>
  );
}